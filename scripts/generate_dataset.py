import os
import pandas as pd
import numpy as np

# Reproducible random seed
np.random.seed(42)

NUM_RECORDS = 2000

data = pd.DataFrame({
    "business_age_years": np.random.randint(1, 21, NUM_RECORDS),
    "monthly_upi_volume": np.random.randint(50000, 1000000, NUM_RECORDS),
    "monthly_bank_volume": np.random.randint(100000, 5000000, NUM_RECORDS),
    "monthly_cash_volume": np.random.randint(10000, 500000, NUM_RECORDS),
    "gst_filing_regularity": np.random.randint(50, 101, NUM_RECORDS),
    "gst_turnover": np.random.randint(500000, 50000000, NUM_RECORDS),
    "bounce_frequency": np.random.randint(0, 12, NUM_RECORDS),
    "avg_monthly_balance": np.random.randint(15000, 2000000, NUM_RECORDS),
    "income_stability": np.random.randint(40, 100, NUM_RECORDS),
    "seasonality_score": np.random.randint(30, 100, NUM_RECORDS),
    "loan_default_history": np.random.choice([0, 1], NUM_RECORDS, p=[0.88, 0.12])
})

# -----------------------------------------------------
# Realistic Underwriting Rules (All 11 Features Active)
# -----------------------------------------------------
# Positive factors:
# - Compliance: GST regularity & income stability (max ~45 pts)
# - Scale & Liquidity: Avg balance, Bank & UPI throughput, Vintage (max ~45 pts)
# Negative factors:
# - Bounce penalties & Default history penalty
score = (
    (data["gst_filing_regularity"] * 0.20) +
    (data["income_stability"] * 0.20) +
    (data["business_age_years"] * 1.5) +
    (data["avg_monthly_balance"] / 60000.0) +
    (data["monthly_bank_volume"] / 1000000.0) +
    (data["monthly_upi_volume"] / 500000.0) +
    (data["gst_turnover"] / 10000000.0) -
    (data["bounce_frequency"] * 3.5) -
    (data["loan_default_history"] * 30.0) -
    ((100 - data["seasonality_score"]) * 0.08)
)

# Realistic Gaussian noise to simulate unobserved real-world variance
score += np.random.normal(0, 4.0, NUM_RECORDS)

# Approval label: 1 = Approved, 0 = Rejected
data["score_label"] = (score >= 45).astype(int)

# Target output path
output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "synthetic_msme_data.csv")

data.to_csv(output_file, index=False)

print(f"✅ Generated {len(data)} MSME records saved to {output_file}")
approval_rate = (data['score_label'].sum() / len(data)) * 100
print(f"📊 Approval Rate: {approval_rate:.1f}% | Rejection Rate: {100 - approval_rate:.1f}%")
