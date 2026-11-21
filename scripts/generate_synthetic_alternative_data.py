"""Generate clearly synthetic daily cash-flow and GST-like MSME records.

No real people, businesses, banks, GSTN, or Account Aggregator data are used.
These files are for local demonstrations and feature-pipeline exercises only.
"""

import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data")
SEED = 2026
BUSINESSES = 250
DAYS = 365


def generate():
    rng = np.random.default_rng(SEED)
    daily_rows, gst_rows, protected = [], [], []
    start = pd.Timestamp("2025-01-01")
    for index in range(BUSINESSES):
        business_id = f"SYN-{index + 1:05d}"
        base = float(rng.lognormal(mean=8.35, sigma=0.7))
        seasonality = float(rng.uniform(0.05, 0.45))
        upi_share = float(rng.uniform(0.25, 0.8))
        bank_share = float(rng.uniform(0.1, 0.5))
        cash_share = max(0.0, 1.0 - upi_share - bank_share)
        owner_gender = str(rng.choice(["woman-owned", "other/unspecified"], p=[0.35, 0.65]))
        region = str(rng.choice(["urban", "rural"], p=[0.65, 0.35]))
        registered = bool(rng.random() < (0.55 if base < 50000 else 0.85))
        month_turnover = np.zeros(12, dtype=float)
        month_filed = np.zeros(12, dtype=int)
        balance = float(rng.lognormal(mean=10.0, sigma=0.55))

        for day in range(DAYS):
            date = start + pd.Timedelta(days=day)
            annual_wave = 1 + seasonality * np.sin(2 * np.pi * (date.day_of_year / 365.25))
            weekday_wave = 0.78 if date.day_of_week == 0 else 1.08 if date.day_of_week in (4, 5) else 1.0
            sales = max(0.0, rng.normal(base * annual_wave * weekday_wave, base * 0.32))
            noisy_shares = np.array([upi_share, bank_share, cash_share]) * rng.uniform(0.75, 1.25, 3)
            noisy_shares /= noisy_shares.sum()
            upi, bank, cash = sales * noisy_shares
            operating_cost = sales * rng.uniform(0.55, 0.88)
            balance = max(0.0, balance + sales - operating_cost)
            month_turnover[date.month - 1] += sales
            daily_rows.append({
                "business_id": business_id,
                "date": date.date().isoformat(),
                "upi_credit_inr": round(upi, 2),
                "bank_transfer_credit_inr": round(bank, 2),
                "cash_sales_estimate_inr": round(cash, 2),
                "operating_debit_estimate_inr": round(operating_cost, 2),
                "closing_balance_estimate_inr": round(balance, 2),
                "bounce_count": int(rng.random() < 0.015),
                "source": "synthetic_generator",
            })

        for month in range(1, 13):
            filed = int(registered and rng.random() < 0.92)
            month_filed[month - 1] = filed
            gst_rows.append({
                "business_id": business_id,
                "tax_period": f"2025-{month:02d}",
                "registration_status": "synthetic_registered" if registered else "synthetic_not_registered",
                "return_filed": filed,
                "reported_turnover_inr": round(float(month_turnover[month - 1]), 2) if filed else None,
                "source": "synthetic_generator_not_gstn",
            })

        protected.append({
            "business_id": business_id,
            "synthetic_owner_group": owner_gender,
            "synthetic_region_group": region,
            "synthetic_gst_registration_status": "registered" if registered else "not_registered",
            "synthetic_annual_turnover_inr": round(float(month_turnover.sum()), 2),
            "synthetic_gst_filing_rate_pct": round(float(month_filed.mean() * 100), 2),
            "source": "synthetic_generator_not_real_demographics_or_GST",
        })

    os.makedirs(OUT, exist_ok=True)
    pd.DataFrame(daily_rows).to_csv(os.path.join(OUT, "synthetic_cashflow_daily.csv"), index=False)
    pd.DataFrame(gst_rows).to_csv(os.path.join(OUT, "synthetic_gst_returns.csv"), index=False)
    pd.DataFrame(protected).to_csv(os.path.join(OUT, "synthetic_business_audit_groups.csv"), index=False)
    return len(daily_rows), len(gst_rows), len(protected)


if __name__ == "__main__":
    daily, returns, firms = generate()
    print(f"Synthetic only: {firms} businesses, {daily} daily cash-flow rows, {returns} GST-like monthly rows.")
    print("Outputs: data/synthetic_cashflow_daily.csv, data/synthetic_gst_returns.csv, data/synthetic_business_audit_groups.csv")
