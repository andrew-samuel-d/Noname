"""Compare an incoming MSME file with the synthetic training feature baseline."""

import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from api.scoring_service import FEATURE_ORDER


def _load(path):
    extension = os.path.splitext(path)[1].lower()
    if extension == ".csv":
        frame = pd.read_csv(path)
    elif extension == ".xlsx":
        frame = pd.read_excel(path, engine="openpyxl")
    else:
        raise ValueError("Input must be a .csv or .xlsx file.")
    missing = [name for name in FEATURE_ORDER if name not in frame.columns]
    if missing:
        raise ValueError("Missing feature columns: " + ", ".join(missing))
    return frame[FEATURE_ORDER].apply(pd.to_numeric, errors="coerce")


def _psi(reference, current, bins=10):
    edges = np.unique(np.quantile(reference.dropna(), np.linspace(0, 1, bins + 1)))
    if len(edges) < 2:
        return 0.0
    edges[0], edges[-1] = -np.inf, np.inf
    ref_counts = np.histogram(reference.dropna(), bins=edges)[0].astype(float)
    cur_counts = np.histogram(current.dropna(), bins=edges)[0].astype(float)
    ref_share = np.clip(ref_counts / max(ref_counts.sum(), 1), 1e-6, None)
    cur_share = np.clip(cur_counts / max(cur_counts.sum(), 1), 1e-6, None)
    return float(np.sum((cur_share - ref_share) * np.log(cur_share / ref_share)))


def main():
    if len(sys.argv) not in (2, 3):
        print("Usage: python scripts/drift_monitor.py <incoming.csv|incoming.xlsx> [report.json]")
        raise SystemExit(2)

    reference_path = os.path.join(ROOT, "data", "synthetic_msme_data.csv")
    reference = _load(reference_path)
    current = _load(os.path.abspath(sys.argv[1]))
    rows = {}
    for feature in FEATURE_ORDER:
        valid_reference = reference[feature].dropna()
        valid_current = current[feature].dropna()
        rows[feature] = {
            "psi": round(_psi(valid_reference, valid_current), 4),
            "reference_missing_pct": round(float(reference[feature].isna().mean() * 100), 2),
            "incoming_missing_pct": round(float(current[feature].isna().mean() * 100), 2),
        }

    report = {
        "status": "screening_only_synthetic_reference_not_production_monitoring",
        "reference": "data/synthetic_msme_data.csv",
        "incoming_rows": int(len(current)),
        "features": rows,
        "note": "PSI is a drift signal, not a performance or fairness measure. Investigate before changing or retraining a model.",
    }
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if len(sys.argv) == 3:
        output_path = os.path.abspath(sys.argv[2])
        with open(output_path, "w", encoding="utf-8") as output:
            output.write(rendered + "\n")
        print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
