# CashFlowScore-ML 🚀
**FINANCE · F2: Credit for the Credit-Invisible**

> *"To a lender, a healthy business with no credit history looks the same as a risky one."*

### 📌 Problem Context & Ground Realities
* **The Reality:** India has crores of micro, small and medium enterprises (MSMEs)—kirana stores, tailors, repair shops, and small manufacturers. They sell every day, and many accept UPI payments.
* **The Dilemma:** Before lending, banks check bureau credit scores (CIBIL), audited accounts, and physical property collateral. Many small businesses have none of these—they are **credit-invisible**.
* **The Cost:** Good businesses are either denied credit or charged exorbitant interest by informal moneylenders.
* **Macro Impact (SIDBI & Govt Data):**
  * **₹30 Lakh Crore:** Estimated credit gap for small businesses in India (~24% of total credit demand, SIDBI).
  * **35%:** Estimated credit gap for women-owned small businesses (SIDBI).
  * **7.28 Crore:** Enterprises registered on the Udyam portal by December 2025.

---

## 🎯 The Challenge: 3 Core Underwriting Questions

> **Design a fairer way to decide which small businesses get credit, how much they get and on what terms, when the business has no formal credit history.**

```
                     [11 Alternative Cash-Flow Features]
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 1. WHO SHOULD GET CREDIT?                                              │
│    • Real-time XGBoost Classifier predicting repayment probability    │
│    • Normalized Credit Score: 0 to 100                                 │
│    • Approval Gate: Approved (Score ≥ 50) vs Rejected (Score < 50)    │
│    • Risk Tiering: Low Risk (≥75) | Moderate (50–74) | High Risk (<50) │
│    • SHAP Directional Explainer: Plain-English, auditor-ready reasons  │
└────────────────────────────────────────────────────────────────────────┘
                                      │ (If Score ≥ 50)
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. HOW MUCH CREDIT SHOULD THEY RECEIVE? (Loan Sizing)                  │
│    • Cash-Flow Capacity = max(AMB, (UPI + Bank Volume) × 0.20)         │
│    • Prime Tier (Score ≥ 85): Up to ₹25 Lakhs (2.5× AMB multiplier)   │
│    • Mid-Risk Tier (Score 70–84): Up to ₹15 Lakhs (1.8× AMB)           │
│    • Moderate Tier (Score 50–69): Up to ₹5 Lakhs (1.2× AMB)            │
│    • Rejected (Score < 50): ₹0 Exposure Limit                          │
└────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. ON WHAT TERMS SHOULD THEY RECEIVE IT?                               │
│    • Risk-Based Pricing: 12.5% to 19.0% p.a. tied to credit score      │
│    • Flexible Tenures: 9 to 24 months dynamically matched to season    │
│    • Repayment Mechanism: Monthly e-NACH or Daily UPI AutoPay (EDI)    │
│    • Security: 100% Collateral-Free under Govt CGTMSE Guarantee Scheme │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Model Evaluation & Metrics

The model is trained on financial transaction and compliance features using an **XGBoost Classifier** with 5-fold stratified cross-validation and regularized trees (`max_depth=4`, `colsample_bytree=0.85`, `reg_lambda=2.0`).

| Metric | Score | Underwriting Context |
| :--- | :---: | :--- |
| **Baseline Accuracy** | **57.0%** | Naive majority class heuristic |
| **Test Accuracy** | **91.0%** | **+34.0% improvement** on unseen MSME profiles |
| **Precision** | **89.53%** | Minimizes non-performing assets (NPAs) |
| **Recall** | **89.53%** | Captures creditworthy unbanked borrowers |
| **F1 Score** | **89.53%** | Harmonic mean balancing risk and credit access |
| **ROC AUC** | **0.9652** | High class separation capability |
| **5-Fold CV Accuracy** | **91.20% ± 1.29%** | Robust validation consistency |
| **Train-Test Gap** | **9.0%** | Regularized against overfitting |

---

## 🔍 The 11 Underwriting Features & Importance

| Rank | Feature | Gain Importance | Category | Description |
| :---: | :--- | :---: | :--- | :--- |
| 1 | `bounce_frequency` | **34.65%** | Risk Flag | Count of cheque / NACH mandate return events |
| 2 | `avg_monthly_balance` | **22.84%** | Liquidity | Average monthly bank balance (₹) |
| 3 | `business_age_years` | **21.77%** | Vintage | Operational survival track record (years) |
| 4 | `loan_default_history` | **5.01%** | Credit Track | Past default flag (0 = clean, 1 = default) |
| 5 | `income_stability` | **4.99%** | Revenue | Predictability and stability index (0–100) |
| 6 | `gst_filing_regularity`| **2.78%** | Compliance | % on-time GST filings over 12 months (0–100) |
| 7 | `monthly_bank_volume` | **2.31%** | Cash Flow | Net monthly bank throughput (₹) |
| 8 | `monthly_cash_volume` | **1.82%** | Cash Flow | Monthly physical cash turnover (₹) |
| 9 | `seasonality_score` | **1.46%** | Risk Flag | Cash flow resilience to seasonal dips (0–100) |
| 10| `monthly_upi_volume` | **1.42%** | Digital Flow | Digital UPI merchant collection throughput (₹) |
| 11| `gst_turnover` | **0.95%** | Scale | Declared annual GST turnover (₹) |

---

## 💻 Tech Stack Alignment

* **Backend & ML:** Python 3.13+, FastAPI, XGBoost, SHAP, Scikit-Learn
* **Data & Cache:** Redis (real-time feature caching & dedup), TimescaleDB (time-series transactions)
* **Event Pipeline:** Apache Kafka (simulated real-time ingestion queue)
* **Frontend:** React 18 Single Page Application, Tailwind CSS, Lucide Icons (mounted natively at `GET /` and `GET /dashboard`)
* **Edge / Offline:** Zero-dependency pure-Python tree inference engine running without C-libraries or internet

---

## 🛠 Project Structure

```
CashFlowScore-ML/
│
├── api/
│   ├── main.py              # FastAPI application server (routes: /, /dashboard, /score, /score-batch)
│   ├── scoring_service.py   # Underwriting & F2 loan sizing engine with tree solver
│   └── batch_api.py         # Batch file upload endpoints (.xlsx / .csv)
│
├── frontend/
│   ├── index.html           # Full React 18 + Tailwind CSS Lender Underwriting Dashboard
│   ├── package.json         # Dashboard metadata & scripts
│   └── README.md            # Frontend UI architecture & guide
│
├── data/
│   ├── sample_100_businesses_input.xlsx   # 100 benchmark MSME application profiles
│   ├── sample_100_businesses_scored.xlsx  # Companion pre-scored output with F2 loan terms
│   └── synthetic_msme_data.csv            # 1,000-record MSME training dataset
│
├── model/
│   ├── xgb_model.json           # Trained 120-tree regularized XGBoost model
│   ├── metrics.json             # Evaluator metrics (91% Acc, 0.9652 AUC)
│   ├── feature_importance.json  # Feature ranking weights
│   ├── confusion_matrix.png     # Visual confusion matrix
│   └── feature_importance.png   # Horizontal feature weight chart
│
├── services/
│   ├── predictor.py         # Pure-Python tree traversal fallback (works with zero native C-libs)
│   ├── explainability.py    # Directional feature impact & SHAP local reasons
│   ├── batch_scorer.py      # Multi-format Excel/CSV batch scorer with OpenXML fallback
│   ├── cache.py             # Redis caching with automated in-memory fallback
│   └── logger.py            # Central logging
│
├── offline/
│   └── offline_score.py     # Standalone CLI tool for scoring files offline with zero internet
│
└── scripts/
    ├── train_model.py       # Training pipeline with 5-fold CV & artifact exporter
    ├── run_tests.py         # Comprehensive 8-test validation suite
    └── create_100_samples.py# Generator for benchmark datasets
```

---

## 🚀 Getting Started

### 1. Start the Server & React Dashboard
```bash
# Using uv (fastest)
uv run uvicorn api.main:app --reload

# Or using standard python
python -m uvicorn api.main:app --reload
```

* **Interactive Lender Dashboard:** Open [http://localhost:8000/dashboard](http://localhost:8000/dashboard)
* **Interactive API Swagger Docs:** Open [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 2. Single Business Underwriting API (`POST /score`)

**Request:**
```bash
curl -X POST "http://localhost:8000/score" \
  -H "Content-Type: application/json" \
  -d '{
    "business_age_years": 8,
    "monthly_upi_volume": 450000,
    "monthly_bank_volume": 2500000,
    "monthly_cash_volume": 120000,
    "gst_filing_regularity": 96,
    "gst_turnover": 18000000,
    "bounce_frequency": 0,
    "avg_monthly_balance": 850000,
    "income_stability": 88,
    "seasonality_score": 75,
    "loan_default_history": 0
  }'
```

**Response (F2 Compliant):**
```json
{
  "score": 100,
  "prediction": 1,
  "decision": "Approved",
  "risk_tier": "Low Risk",
  "probability": 0.9977,
  "top_reasons": [
    "Clean repayment track record with zero defaults",
    "Strong liquidity with Rs. 850,000 avg balance",
    "Exceptional tax compliance (95%+ on-time GST)",
    "Established market vintage (8 years)"
  ],
  "credit_terms": {
    "eligible": true,
    "max_credit_limit_inr": 2120000,
    "interest_rate_pct": 12.5,
    "tenure_months": 24,
    "monthly_emi_inr": 100291,
    "daily_repayment_inr": 4012,
    "repayment_mode": "Monthly auto-debit via e-NACH mandate",
    "security_type": "100% Collateral-Free (Eligible for CGTMSE Credit Guarantee Scheme)",
    "dscr_estimate": 3.82,
    "terms_summary": "Sanction up to Rs. 2,120,000 @ 12.5% p.a. for 24 months (EMI: Rs. 100,291)."
  },
  "model_metrics": {
    "test_accuracy": 0.91,
    "precision": 0.8953,
    "recall": 0.8953,
    "f1_score": 0.8953,
    "auc": 0.9652
  }
}
```

---

### 3. Batch Scoring with Excel or CSV

Use `data/sample_100_businesses_input.xlsx` as a sample workbook. Keep the 11 feature column names unchanged and provide a numeric value for each required feature in every business row. The scorer checks required columns, blanks, and supported value ranges. Results include score, approval probability, decision, risk tier, suggested limit, rate, tenure, EMI, repayment mode, and reasons.

Upload from the dashboard or directly through the API:

```bash
curl -X POST "http://localhost:8000/score-batch" \
  -F "file=@data/sample_100_businesses_input.xlsx" \
  --output scored_businesses.xlsx
```

### 4. Offline Excel Scoring (No API Server)

The command-line scorer runs locally without starting or calling FastAPI:
```bash
python offline/offline_score.py data/sample_100_businesses_input.xlsx
```
Output is saved to `offline/scored_output.xlsx`. Pass an optional second path to choose another output location. CSV input is also supported.

---

### 5. Running the Test Suite
```bash
python scripts/run_tests.py
```
Exercises representative scoring, explanation, feature-importance, and cache paths.
