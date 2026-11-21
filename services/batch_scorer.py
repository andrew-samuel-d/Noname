"""Validated CSV/XLSX batch scoring using the same decision path as the API."""

import os
import math

import pandas as pd

from api.scoring_service import FEATURE_ORDER, score_business


VALUE_RANGES = {
    "business_age_years": (0, None),
    "monthly_upi_volume": (0, None),
    "monthly_bank_volume": (0, None),
    "monthly_cash_volume": (0, None),
    "gst_filing_regularity": (0, 100),
    "gst_turnover": (0, None),
    "bounce_frequency": (0, None),
    "avg_monthly_balance": (0, None),
    "income_stability": (0, 100),
    "seasonality_score": (0, 100),
    "loan_default_history": (0, 1),
}


def _read_input(input_file: str) -> pd.DataFrame:
    ext = os.path.splitext(input_file)[1].lower()
    if ext not in {".csv", ".xlsx"}:
        raise ValueError("Please upload a .xlsx or .csv file.")
    try:
        if ext == ".csv":
            frame = pd.read_csv(input_file)
        else:
            frame = pd.read_excel(input_file, engine="openpyxl")
    except Exception as exc:
        raise ValueError("Could not read this file. Please use a valid .xlsx workbook or .csv file.") from exc

    frame.columns = [str(column).strip() for column in frame.columns]
    if frame.empty:
        raise ValueError("The uploaded spreadsheet has no business rows.")
    missing = [name for name in FEATURE_ORDER if name not in frame.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    return frame


def _validate_features(row: pd.Series, row_number: int) -> dict:
    cleaned = {}
    for name in FEATURE_ORDER:
        value = pd.to_numeric(row[name], errors="coerce")
        if pd.isna(value):
            raise ValueError(f"Row {row_number}: '{name}' is blank or not numeric.")
        value = float(value)
        if not math.isfinite(value):
            raise ValueError(f"Row {row_number}: '{name}' must be a finite number.")
        low, high = VALUE_RANGES[name]
        if value < low or (high is not None and value > high):
            limit = f"{low} to {high}" if high is not None else f"at least {low}"
            raise ValueError(f"Row {row_number}: '{name}' must be {limit}.")
        if name == "loan_default_history" and value not in (0, 1):
            raise ValueError(f"Row {row_number}: 'loan_default_history' must be 0 or 1.")
        cleaned[name] = value
    return cleaned


def score_excel(input_file: str, output_file: str) -> dict:
    """Score a CSV or XLSX file, preserving source columns and returning summary stats."""
    frame = _read_input(input_file)
    generated_columns = {
        "score_label", "credit_score", "approval_probability_pct", "confidence",
        "decision", "risk_tier", "max_credit_limit_inr", "interest_rate_pct",
        "tenure_months", "monthly_emi_inr", "repayment_mode", "top_reasons",
    }
    frame = frame.drop(columns=[name for name in generated_columns if name in frame.columns])

    outputs = []
    for index, (_, row) in enumerate(frame.iterrows(), start=2):
        features = _validate_features(row, index)
        result = score_business(features)
        if "error" in result:
            raise ValueError(f"Row {index}: scoring failed: {result['error']}")
        terms = result["credit_terms"]
        outputs.append({
            "credit_score": result["score"],
            "approval_probability_pct": round(result["probability"] * 100, 2),
            "decision": result["decision"],
            "risk_tier": result["risk_tier"],
            "max_credit_limit_inr": terms["max_credit_limit_inr"],
            "interest_rate_pct": terms["interest_rate_pct"],
            "tenure_months": terms["tenure_months"],
            "monthly_emi_inr": terms["monthly_emi_inr"],
            "repayment_mode": terms["repayment_mode"],
            "top_reasons": "; ".join(result["top_reasons"]),
        })

    result_frame = pd.concat([frame.reset_index(drop=True), pd.DataFrame(outputs)], axis=1)
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    if os.path.splitext(output_file)[1].lower() == ".csv":
        result_frame.to_csv(output_file, index=False)
    else:
        result_frame.to_excel(output_file, index=False, engine="openpyxl")

    decisions = result_frame["decision"]
    return {
        "records": int(len(result_frame)),
        "approved": int((decisions == "Approved").sum()),
        "rejected": int((decisions == "Rejected").sum()),
        "average_score": round(float(result_frame["credit_score"].mean()), 1),
    }
