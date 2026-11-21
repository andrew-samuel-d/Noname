"""Generate global and per-business SHAP explanations for the saved XGBoost model."""

import json
import os

import numpy as np
import pandas as pd
import shap
from xgboost import XGBClassifier

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES = [
    "business_age_years", "monthly_upi_volume", "monthly_bank_volume",
    "monthly_cash_volume", "gst_filing_regularity", "gst_turnover",
    "bounce_frequency", "avg_monthly_balance", "income_stability",
    "seasonality_score", "loan_default_history",
]


def main():
    data = pd.read_csv(os.path.join(ROOT, "data", "synthetic_msme_data.csv"))
    x = data[FEATURES].sample(n=min(300, len(data)), random_state=42)
    model = XGBClassifier()
    model.load_model(os.path.join(ROOT, "model", "xgb_model.json"))
    explainer = shap.TreeExplainer(model)
    values = explainer(x)
    shap_matrix = np.asarray(values.values)
    if shap_matrix.ndim == 3:
        shap_matrix = shap_matrix[:, :, 1]

    mean_absolute = np.abs(shap_matrix).mean(axis=0)
    global_summary = pd.DataFrame({
        "feature": FEATURES,
        "mean_abs_shap_raw_margin": mean_absolute,
    }).sort_values("mean_abs_shap_raw_margin", ascending=False)

    sample_features = x.iloc[0]
    individual = pd.DataFrame({
        "feature": FEATURES,
        "feature_value": sample_features.to_numpy(),
        "shap_value_raw_margin": shap_matrix[0],
    }).sort_values("shap_value_raw_margin", key=lambda series: series.abs(), ascending=False)

    out = os.path.join(ROOT, "model")
    global_summary.to_csv(os.path.join(out, "shap_global_importance.csv"), index=False)
    individual.to_csv(os.path.join(out, "shap_sample_explanation.csv"), index=False)
    payload = {
        "status": "synthetic_model_explanation_not_repayment_causality",
        "output_scale": "raw XGBoost margin (log-odds scale)",
        "explained_rows": int(len(x)),
        "global_mean_absolute_shap": global_summary.to_dict(orient="records"),
        "sample_business_explanation": individual.to_dict(orient="records"),
        "note": "SHAP attributes this model's output across input features; it does not establish causation, fairness, or real-world creditworthiness.",
    }
    with open(os.path.join(out, "shap_explanations.json"), "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

    print("Saved model/shap_global_importance.csv")
    print("Saved model/shap_sample_explanation.csv")
    print("Saved model/shap_explanations.json")
    print(global_summary.to_string(index=False))


if __name__ == "__main__":
    main()
