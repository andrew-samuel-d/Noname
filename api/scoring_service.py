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
            "repayment_mode": "N/A (Application Declined)",
            "security_type": "N/A",
            "dscr_estimate": 0.0,
            "terms_summary": "Ineligible for unsecured cash-flow credit due to elevated risk indicators."
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
        repayment_mode = "Daily / Weekly auto-deduction via UPI AutoPay & QR settlement"
    else:
        repayment_mode = "Monthly auto-debit via e-NACH mandate"

    if score >= 75:
        security_type = "100% Collateral-Free (Eligible for CGTMSE Credit Guarantee Scheme)"
    else:
        security_type = "Unsecured with Personal Guarantee of Proprietor + Security PDCs"

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
        "terms_summary": f"Sanction up to Rs. {credit_limit:,} @ {interest_rate}% p.a. for {tenure} months (EMI: Rs. {monthly_emi:,})."
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
        # Sanitize and ensure numeric types for all features
        clean_features = {}
        for col in FEATURE_ORDER:
            raw_val = feature_dict.get(col, 0)
            try:
                clean_features[col] = float(raw_val) if raw_val is not None else 0.0
            except (ValueError, TypeError):
                clean_features[col] = 0.0

        # Predict probability
        if _xgb_model is not None:
            import pandas as pd
            df = pd.DataFrame([clean_features])[FEATURE_ORDER]
            probability = float(_xgb_model.predict_proba(df)[0][1])
            prediction = int(_xgb_model.predict(df)[0])
        elif _tree_model_data is not None:
            probability = _predict_with_trees(clean_features, _tree_model_data)
            prediction = 1 if probability >= 0.5 else 0
        else:
            # Fallback heuristic if model file could not be read
            score_heuristic = (
                clean_features["gst_filing_regularity"] * 0.25 +
                clean_features["income_stability"] * 0.25 +
                clean_features["business_age_years"] * 2 +
                clean_features["avg_monthly_balance"] / 50000 -
                clean_features["bounce_frequency"] * 4 -
                clean_features["loan_default_history"] * 25
            )
            probability = max(0.0, min(1.0, score_heuristic / 100.0))
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

        if clean_features["loan_default_history"] == 1:
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
            if clean_features["loan_default_history"] == 0:
                top_reasons.append("Clean repayment track record with zero defaults")
            if clean_features["avg_monthly_balance"] >= 500000:
                top_reasons.append(f"Strong liquidity with Rs. {int(clean_features['avg_monthly_balance']):,} avg balance")
            if clean_features["gst_filing_regularity"] >= 95:
                top_reasons.append("Exceptional tax compliance (95%+ on-time GST)")
            if clean_features["business_age_years"] >= 5:
                top_reasons.append(f"Established market vintage ({int(clean_features['business_age_years'])} years)")

        # Calculate F2 Loan Sizing & Terms
        credit_terms = calculate_credit_terms(clean_features, score, risk_tier)

        return {
            "score": score,
            "prediction": prediction,
            "decision": decision,
            "risk_tier": risk_tier,
            "probability": round(probability, 4),
            "top_reasons": top_reasons,
            "credit_terms": credit_terms
        }

    except Exception as e:
        return {
            "error": str(e)
        }
