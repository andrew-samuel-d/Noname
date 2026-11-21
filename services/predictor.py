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
    for p in candidates:
        if os.path.exists(p):
            return p
    return "model/xgb_model.json"

MODEL_PATH = _resolve_model_path()

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


def _predict_with_trees(features_dict, tree_data):
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

    return 1.0 / (1.0 + math.exp(-margin))


def predict_score(feature_dict):
    """
    Returns score (0-100) and probability (0-1).
    Safe against missing features or format discrepancies.
    """
    clean_dict = {col: float(feature_dict.get(col, 0.0)) for col in FEATURE_ORDER}

    if _xgb_model is not None:
        try:
            import pandas as pd
            df = pd.DataFrame([clean_dict])[FEATURE_ORDER]
            probability = float(_xgb_model.predict_proba(df)[0][1])
            score = int(round(probability * 100))
            return score, probability
        except Exception:
            pass

    if _tree_model_data is not None:
        probability = _predict_with_trees(clean_dict, _tree_model_data)
        score = int(round(probability * 100))
        return score, probability

    # Heuristic fallback if model not loaded
    score_heuristic = (
        clean_dict["gst_filing_regularity"] * 0.25 +
        clean_dict["income_stability"] * 0.25 +
        clean_dict["business_age_years"] * 2 +
        clean_dict["avg_monthly_balance"] / 50000 -
        clean_dict["bounce_frequency"] * 4 -
        clean_dict["loan_default_history"] * 25
    )
    probability = max(0.0, min(1.0, score_heuristic / 100.0))
    return int(round(probability * 100)), probability
