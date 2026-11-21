import os
import json

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

def _resolve_path(filename: str):
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model", filename),
        os.path.join("model", filename),
        os.path.join("..", "model", filename)
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return os.path.join("model", filename)


def get_global_feature_importance():
    """Returns global feature importance ranked from high to low."""
    imp_file = _resolve_path("feature_importance.json")
    if os.path.exists(imp_file):
        try:
            with open(imp_file, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def explain_prediction(features_dict):
    """
    Computes local feature contribution for an individual business profile.
    Returns sorted list of features with directional impact.
    """
    contributions = []
    importance_list = get_global_feature_importance()
    weight_map = {item["feature"]: item["importance"] for item in importance_list}

    # Reference MSME baseline thresholds
    benchmarks = {
        "business_age_years": 5.0,
        "monthly_upi_volume": 300000.0,
        "monthly_bank_volume": 1500000.0,
        "monthly_cash_volume": 150000.0,
        "gst_filing_regularity": 85.0,
        "gst_turnover": 10000000.0,
        "bounce_frequency": 2.0,
        "avg_monthly_balance": 350000.0,
        "income_stability": 70.0,
        "seasonality_score": 50.0,
        "loan_default_history": 0.0
    }

    for feat in FEATURE_ORDER:
        val = float(features_dict.get(feat, 0.0))
        bench = benchmarks.get(feat, 0.0)
        global_w = weight_map.get(feat, 0.05)

        # Risk features: lower is better
        if feat in ["bounce_frequency", "loan_default_history"]:
            delta = bench - val
        else: # Growth/stability features: higher is better
            delta = (val - bench) / (bench if bench > 0 else 1.0)

        impact_score = round(delta * global_w, 4)
        contributions.append({
            "feature": feat,
            "value": val,
            "impact": impact_score,
            "effect": "Positive" if impact_score >= 0 else "Negative"
        })

    contributions.sort(key=lambda x: abs(x["impact"]), reverse=True)
    return contributions
