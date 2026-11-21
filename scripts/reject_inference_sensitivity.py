"""Sensitivity analysis for missing repayment outcomes among rejected applicants.

Input must contain decision (Approved/Rejected) and, for approved rows only,
repayment_default_12m (0/1). This does not impute a single "true" rejected label.
"""

import json
import sys

import pandas as pd


def analyze(frame):
    required = {"decision", "repayment_default_12m"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
    decision = frame["decision"].astype(str).str.strip().str.lower()
    approved = frame[decision == "approved"].copy()
    rejected = frame[decision == "rejected"].copy()
    if approved.empty or rejected.empty:
        raise ValueError("Input needs at least one approved and one rejected applicant.")
    outcomes = pd.to_numeric(approved["repayment_default_12m"], errors="coerce")
    if outcomes.isna().any() or not outcomes.isin([0, 1]).all():
        raise ValueError("Approved rows require observed repayment_default_12m values of 0 or 1.")
    observed_default_rate = float(outcomes.mean())
    scenarios = []
    total = len(frame)
    observed_approved_defaults = int(outcomes.sum())
    for rejected_default_rate in (0.0, 0.25, 0.50, 0.75, 1.0):
        estimated_defaults = observed_approved_defaults + len(rejected) * rejected_default_rate
        scenarios.append({
            "assumed_rejected_default_rate": rejected_default_rate,
            "estimated_portfolio_default_rate": round(estimated_defaults / total, 4),
        })
    return {
        "status": "sensitivity_analysis_not_reject_inference_truth",
        "applicants": total,
        "approved_with_observed_outcome": len(approved),
        "rejected_without_observed_outcome": len(rejected),
        "approved_observed_default_rate": round(observed_default_rate, 4),
        "scenarios": scenarios,
        "limitations": [
            "The rejected applicants' repayment outcomes are unobserved and cannot be verified from this file.",
            "Assumed reject default rates are sensitivity values, not predictions or imputed labels.",
            "Run only on properly governed, consented pilot records with mature repayment windows.",
        ],
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/reject_inference_sensitivity.py pilot_outcomes.csv")
    result = analyze(pd.read_csv(sys.argv[1]))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
