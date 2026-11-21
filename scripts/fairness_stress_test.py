"""Fairlearn group-metric report for disclosed synthetic proxy scenarios only."""

import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from api.scoring_service import FEATURE_ORDER, score_business


def _metric_values(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    n = len(y_true)
    return {
        "selection_rate": float(np.mean(y_pred)) if n else 0.0,
        "true_positive_rate": float(tp / (tp + fn)) if tp + fn else None,
        "false_positive_rate": float(fp / (fp + tn)) if fp + tn else None,
        "n": int(n),
    }


def _fairlearn_metrics(y_true, y_pred, groups):
    try:
        from fairlearn.metrics import MetricFrame, selection_rate, true_positive_rate, false_positive_rate
        frame = MetricFrame(
            metrics={
                "selection_rate": selection_rate,
                "true_positive_rate": true_positive_rate,
                "false_positive_rate": false_positive_rate,
            },
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=groups,
        )
        return {
            "library": "Fairlearn MetricFrame",
            "by_group": json.loads(frame.by_group.to_json(orient="index")),
            "max_group_difference": json.loads(frame.difference(method="between_groups").to_json()),
        }
    except ImportError:
        result = {}
        for group in sorted(pd.Series(groups).unique()):
            mask = np.asarray(groups) == group
            result[str(group)] = _metric_values(np.asarray(y_true)[mask], np.asarray(y_pred)[mask])
        return {"library": "built-in fallback (install fairlearn for MetricFrame)", "by_group": result}


def _score(rows):
    return np.array([int(score_business(row)["score"] >= 50) for row in rows.to_dict(orient="records")])


def _proxy_report(name, reference_features, shifted_features, labels, group_names):
    # Duplicate the same businesses across two counterfactual proxy cohorts.
    y_true = np.concatenate([labels, labels])
    y_pred = np.concatenate([_score(reference_features), _score(shifted_features)])
    groups = np.array(["reference scenario"] * len(labels) + [name] * len(labels))
    measured = _fairlearn_metrics(y_true, y_pred, groups)
    measured["selection_rate_gap_percentage_points"] = round(
        (float(np.mean(y_pred[groups == name])) - float(np.mean(y_pred[groups == "reference scenario"]))) * 100, 2
    )
    measured["group_labels_are_real_demographics"] = False
    measured["invented_group_assumptions"] = group_names
    return measured


def main():
    path = os.path.join(ROOT, "data", "synthetic_msme_data.csv")
    source = pd.read_csv(path)
    features = source[FEATURE_ORDER].astype(float).copy()
    labels = source["score_label"].astype(int).to_numpy()

    women = features.copy()
    women["avg_monthly_balance"] *= 0.85
    women["monthly_upi_volume"] *= 0.85
    women["monthly_bank_volume"] *= 0.90

    rural = features.copy()
    rural["monthly_upi_volume"] *= 0.80
    rural["monthly_bank_volume"] *= 0.80
    rural["avg_monthly_balance"] *= 0.90

    report = {
        "status": "synthetic_counterfactual_sensitivity_not_fairness_certification",
        "package": "Fairlearn MetricFrame when installed; transparent built-in fallback otherwise",
        "n_base_businesses": int(len(features)),
        "model_input_features": FEATURE_ORDER,
        "protected_attributes_used_as_model_inputs": [],
        "reference_label": "score_label is a generated approval-rule label, not a repayment outcome",
        "metrics": {
            "women_owned_proxy": _proxy_report(
                "women-owned proxy", features, women, labels,
                "Same businesses with assumed 15% lower balance and UPI, 10% lower bank volume; not observed gender data.",
            ),
            "rural_proxy": _proxy_report(
                "rural proxy", features, rural, labels,
                "Same businesses with assumed 20% lower UPI/bank volume and 10% lower balance; not observed region data.",
            ),
        },
        "limitations": [
            "Inputs, groups, and generated labels are synthetic; metrics do not describe real demographic groups.",
            "The generated target is an approval-rule label, not successful repayment; TPR/FPR here measure agreement with that synthetic rule only.",
            "This script cannot establish equal opportunity, regulatory compliance, or model fairness in a lending population.",
            "A production audit needs consented protected-group attributes, representative applicants, matured outcomes, and a documented governance process.",
        ],
    }
    output_path = os.path.join(ROOT, "model", "fairness_stress_test.json")
    with open(output_path, "w", encoding="utf-8") as output:
        json.dump(report, output, indent=2, allow_nan=False)
    print(json.dumps(report, indent=2, allow_nan=False))
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
