import os
import json
import math

FEATURE_ORDER = [
    "business_age_years",
    "monthly_upi_volume",
    "monthly_bank_volume",
    "monthly_cash_volume",
    "gst_filing_regularity",
    "gst_turnover",
    "bounce_frequency",
    "avg_monthly_balance",
    "income_stability",
    "seasonality_score",
    "loan_default_history"
]

def _resolve_model_path():
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model", "xgb_model.json"),
        "model/xgb_model.json",
        "../model/xgb_model.json"
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return "model/xgb_model.json"

MODEL_PATH = _resolve_model_path()

# Attempt to load native XGBoost; fallback to pure-Python tree inference
_xgb_model = None
_tree_model_data = None

try:
    from xgboost import XGBClassifier
    _xgb_model = XGBClassifier()
    _xgb_model.load_model(MODEL_PATH)
except Exception:
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "r") as f:
                _tree_model_data = json.load(f)
        except Exception:
            pass


def calculate_credit_terms(clean_features, score, risk_tier):
    """
    Solves the 3 core underwriting questions (F2):
    1. Who gets credit? (Eligibility / Decision / Risk Tier)
    2. How much credit? (Loan Sizing / Exposure Limit based on Cash Flow)
    3. On what terms? (Interest Rate, Tenure, EMI, Repayment Mode, Security)
    """
    if score < 50:
        return {
            "eligible": False,
            "max_credit_limit_inr": 0,
            "interest_rate_pct": None,
            "tenure_months": 0,
            "monthly_emi_inr": 0,
            "daily_repayment_inr": 0,
            "repayment_mode": "N/A (not eligible under prototype threshold)",
            "security_type": "Not assessed by this prototype",
            "dscr_estimate": 0.0,
            "terms_summary": "Prototype estimate only; a lender review is required."
        }

    # 1. Loan Sizing (How much credit?)
    amb = clean_features.get("avg_monthly_balance", 0.0)
    upi_vol = clean_features.get("monthly_upi_volume", 0.0)
    bank_vol = clean_features.get("monthly_bank_volume", 0.0)
    monthly_inflow = max(amb, (upi_vol + bank_vol) * 0.20)

    # Exposure limits by risk tier
    if score >= 85:
        multiplier = 2.5
        max_cap = 2500000.0  # Rs. 25 Lakhs
        min_limit = 100000.0
    elif score >= 70:
        multiplier = 1.8
        max_cap = 1500000.0  # Rs. 15 Lakhs
        min_limit = 75000.0
    else:
        multiplier = 1.2
        max_cap = 500000.0   # Rs. 5 Lakhs
        min_limit = 50000.0

    raw_limit = max(amb * multiplier, monthly_inflow * 1.5)
    credit_limit = min(max_cap, max(min_limit, raw_limit))
    credit_limit = int(round(credit_limit / 10000.0) * 10000)

    # 2. Risk-Based Pricing (What terms?)
    if score >= 85:
        interest_rate = 12.5  # 12.5% p.a. Prime
    elif score >= 75:
        interest_rate = 14.5  # 14.5% p.a.
    elif score >= 65:
        interest_rate = 16.5  # 16.5% p.a.
    else:
        interest_rate = 19.0  # 19.0% p.a. Risk-adjusted

    # 3. Tenure
    age = clean_features.get("business_age_years", 0)
    stability = clean_features.get("income_stability", 50)
    seasonality = clean_features.get("seasonality_score", 50)

    if age >= 5 and stability >= 80 and score >= 75:
        tenure = 24  # 24 months
    elif age >= 3 and score >= 60:
        tenure = 18
    elif seasonality < 50:
        tenure = 9   # Short tenure for high-seasonality business
    else:
        tenure = 12  # Standard 12-month working capital

    # 4. EMI Amortization Calculation
    monthly_rate = (interest_rate / 100.0) / 12.0
    if monthly_rate > 0 and tenure > 0:
        emi = credit_limit * (monthly_rate * (1 + monthly_rate) ** tenure) / ((1 + monthly_rate) ** tenure - 1)
        monthly_emi = int(round(emi))
    else:
        monthly_emi = int(round(credit_limit / (tenure or 1)))

    daily_repayment = int(round(monthly_emi / 25.0))

    # 5. Repayment Mode & Security
    if upi_vol > (bank_vol * 0.4):
        repayment_mode = "Proposed daily / weekly sales-linked repayment; no payment rail connected"
    else:
        repayment_mode = "Proposed monthly repayment; no payment rail connected"

    security_type = "Collateral and guarantee eligibility not assessed by this prototype"

    est_free_cash = max(1000.0, amb * 0.4)
    dscr = round(est_free_cash / (monthly_emi or 1.0), 2)

    return {
        "eligible": True,
        "max_credit_limit_inr": credit_limit,
        "interest_rate_pct": interest_rate,
        "tenure_months": tenure,
        "monthly_emi_inr": monthly_emi,
        "daily_repayment_inr": daily_repayment,
        "repayment_mode": repayment_mode,
        "security_type": security_type,
        "dscr_estimate": max(1.1, min(3.5, dscr)),
        "terms_summary": f"Illustrative only: up to Rs. {credit_limit:,} at {interest_rate}% p.a. for {tenure} months (estimated EMI: Rs. {monthly_emi:,}). Not a loan offer."
    }


def _predict_with_trees(features_dict, tree_data):
    """Pure-Python evaluation of the XGBoost JSON trees (zero native dependency fallback)."""
    trees = tree_data["learner"]["gradient_booster"]["model"]["trees"]
    feat_names = tree_data["learner"]["feature_names"]
    margin = 0.0

    for tree in trees:
        node = 0
        while tree["left_children"][node] != -1:
            f_idx = tree["split_indices"][node]
            f_name = feat_names[f_idx]
            val = float(features_dict.get(f_name, 0.0))
            cond = tree["split_conditions"][node]
            if val < cond:
                node = tree["left_children"][node]
            else:
                node = tree["right_children"][node]
        margin += tree["base_weights"][node]

    # Logistic sigmoid
    prob = 1.0 / (1.0 + math.exp(-margin))
    return prob


def score_business(feature_dict):
    """
    Evaluates business features and returns:
    - credit score (0-100)
    - probability of approval (0.0 - 1.0)
    - prediction (1 = Approved, 0 = Rejected)
    - risk_tier ('Low Risk', 'Moderate Risk', 'High Risk')
    - top_reasons (explainable drivers)
    """
    try:
        raw_history = feature_dict.get("loan_default_history")
        history_unknown = raw_history is None or str(raw_history).strip().lower() in {"", "unknown", "na", "n/a"}
        # Sanitize and ensure numeric types for all features
        clean_features = {}
        for col in FEATURE_ORDER:
            raw_val = feature_dict.get(col, 0)
            if col == "loan_default_history" and history_unknown:
                clean_features[col] = 0.0
                continue
            try:
                clean_features[col] = float(raw_val) if raw_val is not None else 0.0
            except (ValueError, TypeError):
                clean_features[col] = 0.0

        def model_probability(values):
            if _xgb_model is not None:
                import pandas as pd
                df = pd.DataFrame([values])[FEATURE_ORDER]
                return float(_xgb_model.predict_proba(df)[0][1])
            if _tree_model_data is not None:
                return _predict_with_trees(values, _tree_model_data)
            score_heuristic = (
                values["gst_filing_regularity"] * 0.25 +
                values["income_stability"] * 0.25 +
                values["business_age_years"] * 2 +
                values["avg_monthly_balance"] / 50000 -
                values["bounce_frequency"] * 4 -
                values["loan_default_history"] * 25
            )
            return max(0.0, min(1.0, score_heuristic / 100.0))

        if history_unknown:
            # Marginalize over both possible recorded outcomes. Missing history
            # is not treated as a clean record or as a default.
            no_default = dict(clean_features, loan_default_history=0.0)
            default = dict(clean_features, loan_default_history=1.0)
            probability = (model_probability(no_default) + model_probability(default)) / 2
        else:
            probability = model_probability(clean_features)
        prediction = 1 if probability >= 0.5 else 0

        score = max(0, min(100, int(round(probability * 100))))

        # Determine risk tier
        if score >= 75:
            risk_tier = "Low Risk"
        elif score >= 50:
            risk_tier = "Moderate Risk"
        else:
            risk_tier = "High Risk"

        decision = "Approved" if score >= 50 else "Rejected"

        # Explainable reasons (positive and negative drivers)
        top_reasons = []

        if not history_unknown and clean_features["loan_default_history"] == 1:
            top_reasons.append("Previous loan default recorded")
        if clean_features["bounce_frequency"] > 3:
            top_reasons.append(f"High cheque/mandate bounce frequency ({int(clean_features['bounce_frequency'])} times)")
        if clean_features["gst_filing_regularity"] < 80:
            top_reasons.append(f"Low GST filing regularity ({clean_features['gst_filing_regularity']}%)")
        if clean_features["avg_monthly_balance"] < 100000:
            top_reasons.append(f"Low average monthly balance (Rs. {int(clean_features['avg_monthly_balance']):,})")
        if clean_features["business_age_years"] < 3:
            top_reasons.append(f"Young business vintage ({int(clean_features['business_age_years'])} years)")
        if clean_features["income_stability"] < 60:
            top_reasons.append(f"Income stability index is low ({clean_features['income_stability']})")

        # Positive drivers if healthy
        if not top_reasons:
            if not history_unknown and clean_features["loan_default_history"] == 0:
                top_reasons.append("Clean repayment track record with zero defaults")
            if clean_features["avg_monthly_balance"] >= 500000:
                top_reasons.append(f"Strong liquidity with Rs. {int(clean_features['avg_monthly_balance']):,} avg balance")
            if clean_features["gst_filing_regularity"] >= 95:
                top_reasons.append("Exceptional tax compliance (95%+ on-time GST)")
            if clean_features["business_age_years"] >= 5:
                top_reasons.append(f"Established market vintage ({int(clean_features['business_age_years'])} years)")

        if history_unknown:
            top_reasons.insert(0, "No formal repayment history supplied; score averages both history scenarios")

        coaching = []
        if clean_features["bounce_frequency"] > 1:
            coaching.append("If accurate, review recent returned payments and share corrected records; this prototype flags bounce frequency.")
        if clean_features["gst_filing_regularity"] < 90:
            coaching.append("If applicable, bring GST filing records up to date or provide alternative sales records; do not file inaccurate returns to change a score.")
        if clean_features["income_stability"] < 60 or clean_features["avg_monthly_balance"] < 100000:
            coaching.append("Optional: provide several months of business cash-flow evidence so a lender can review seasonality and operating needs.")
        if history_unknown:
            coaching.append("No formal loan history is not a default. A lender could review supplier invoices, utility bills, or a small affordable starter facility with consent.")
        if score < 50:
            coaching.append("Request correction of inaccurate inputs and human review; these suggestions do not guarantee eligibility or a higher score.")

        # Calculate F2 Loan Sizing & Terms
        credit_terms = calculate_credit_terms(clean_features, score, risk_tier)

        return {
            "score": score,
            "prediction": prediction,
            "decision": decision,
            "risk_tier": risk_tier,
            "probability": round(probability, 4),
            "credit_history_status": "unknown" if history_unknown else "reported",
            "top_reasons": top_reasons,
            "coaching": coaching,
            "credit_terms": credit_terms
        }

    except Exception as e:
        return {
            "error": str(e)
        }
