# FINANCE · F2: Credit for the Credit-Invisible
**Challenge:** Design a fairer way to decide which small businesses get credit, how much they get and on what terms, when the business has no formal credit history.  
**Core Dilemma:** *"To a lender, a healthy business with no credit history looks the same as a risky one."*

---

## ⚡ 60-Second Elevator Pitch (What to say to the Evaluator)

> *"Good morning / afternoon, respected judges. India has over **7.28 crore small enterprises** on the Udyam portal—kirana stores, tailors, repair shops, and small manufacturers. They sell every day and collect via UPI, yet they face a **₹30 Lakh Crore credit gap** according to SIDBI, with a **35% credit gap for women-owned small businesses**.*
>
> *Why? Because to a traditional bank, **a healthy business with no credit history looks the exact same as a risky one**. Traditional underwriting requires past CIBIL records, audited financial statements, and physical collateral. Because they are credit-invisible, they are either rejected or forced to borrow from predatory lenders.*
>
> *We built **CashFlowScore** to directly solve the **FINANCE · F2 challenge**:
> 1. **Which small businesses get credit?** Our 120-tree regularized XGBoost model analyzes 11 alternative cash-flow signals (UPI throughput, average bank balance, GST filings, bounce regularity) to identify healthy borrowers with 91% test accuracy and plain-English SHAP reasons.
> 2. **How much credit do they get?** Sized dynamically based on cash-flow capacity rather than property collateral, capping exposure from ₹50,000 to ₹25 Lakhs.
> 3. **On what terms do they get it?** Fair, risk-adjusted pricing (12.5% to 19%), daily EDI repayment auto-swept via UPI AutoPay matching their daily sales cycle, and 100% collateral-free under CGTMSE.*
>
> *Best of all, it runs online or 100% offline at the edge for rural branch loan officers without internet."*

---

## 🎯 The Three Core F2 Questions (Explained Simply)

| Question | How We Solve It | Output in System |
| :--- | :--- | :--- |
| **1. Who should get credit?** | • **120-Tree Regularized XGBoost Classifier** predicts repayment probability.<br>• Mapped to a normalized **Credit Score (0–100)**.<br>• **Approval Decision:** Approved (Score $\ge 50$) vs Rejected (Score $< 50$).<br>• **Risk Tier:** Low Risk ($\ge 75$), Moderate Risk ($50–74$), High Risk ($< 50$).<br>• **SHAP Explainability Layer:** Automatically translates machine learning tree splits into 4 auditor-ready, plain-English reasons (e.g. *"Strong liquidity with ₹4.5L balance"*). | `score: 98`<br>`decision: "Approved"`<br>`risk_tier: "Low Risk"`<br>`top_reasons: [...]` |
| **2. How much credit should they receive?** | • **Dynamic Cash-Flow Capacity:** Evaluates verified liquidity cushion: $\text{Capacity} = \max(\text{AMB}, (\text{UPI} + \text{Bank Vol}) \times 0.20)$.<br>• **Risk-Tier Multipliers:**<br>  - **Prime Tier ($\ge 85$):** $2.5\times$ AMB, capped at **₹25 Lakhs**.<br>  - **Mid-Tier (70–84):** $1.8\times$ AMB, capped at **₹15 Lakhs**.<br>  - **Moderate Tier (50–69):** $1.2\times$ AMB, capped at **₹5 Lakhs**.<br>  - **Rejected ($< 50$):** ₹0 (No unhedged exposure). | `max_credit_limit_inr: 1880000`<br>(Sanction limit up to ₹18.8 Lakhs) |
| **3. On what terms should they receive it?** | • **Risk-Based Pricing:** From **12.5% p.a.** (Prime) to **19.0% p.a.** (Moderate Risk).<br>• **Dynamic Tenures:** 9, 12, 18, or 24 months based on score and cash-flow seasonality.<br>• **Repayment Mechanism:**<br>  - **Retail / Merchant:** Daily EDI deduction (₹1,500 – ₹4,000/day) swept automatically via **UPI AutoPay**.<br>  - **B2B Enterprises:** Monthly auto-debit via **e-NACH mandate**.<br>• **Security & Collateral:** **100% Collateral-Free** under the Government of India's **CGTMSE** Credit Guarantee Scheme. | `interest_rate_pct: 12.5%`<br>`tenure_months: 24`<br>`monthly_emi_inr: 88938`<br>`daily_repayment_inr: 3558`<br>`security_type: "100% Collateral-Free (CGTMSE)"` |

---

## 🧠 The ML Architecture Explained in Layman Terms

### 1. The 11 Features & Why They Matter
1. **Cheque / NACH Bounce Frequency (34.65% weight - Top Risk Flag):**
   * *Layman:* If a business bounces mandates, they are facing cash distress. A single bounce alerts the lender.
2. **Average Monthly Balance (22.84% weight - Liquidity):**
   * *Layman:* Money sitting in the account proves liquidity cushion when sales fluctuate.
3. **Business Age / Vintage (21.77% weight - Stability):**
   * *Layman:* A business surviving 5+ years has proven staying power through local market cycles.
4. **Loan Default History (5.01%):** Past delinquency flag.
5. **Income Stability (4.99%):** Month-on-month volatility coefficient.
6. **GST Regularity (2.78%):** On-time compliance shows operational discipline.
7. **Bank Throughput (2.31%) & UPI Volume (1.42%):** Proof of active commercial throughput.
8. **Cash Volume (1.82%) & Seasonality (1.46%):** Detects festival dependence.
9. **Annual GST Turnover (0.95%):** Macro size sanity check.

### 2. Regularization Against Overfitting
* *Evaluator question:* *"Did your model overfit on training data?"*
* *Answer:* *"No. Initially, unconstrained trees memorized the data (100% train accuracy). We introduced explicit regularization: restricted `max_depth=4`, set `subsample=0.85`, `colsample_bytree=0.85`, and $L_2$ regularization `reg_lambda=2.0`. On unseen test data, we achieve **91.0% accuracy**, **0.9652 ROC AUC**, and a 5-fold cross-validation of **91.20% ± 1.29%**, keeping the train-test gap to a healthy 9%."*

---

## 🛡️ Answers to Tough Questions from Evaluators

### Q1: "Why XGBoost and not Deep Learning or LLMs?"
> *"For credit underwriting in regulated financial institutions (RBI guidelines), two things are strictly mandatory: **Explainability** and **Deterministic Reliability**. Neural networks are black boxes where you cannot explain to an auditor or a rejected applicant why they failed. XGBoost paired with TreeSHAP yields exact feature attribution (local directional impact). Furthermore, our XGBoost model evaluates in **under 4 milliseconds**, allowing it to run offline on low-power devices in remote rural branches without GPU servers."*

### Q2: "How do you get borrower bank and GST data without a banking license?"
> *"We do not need a banking license because we are an **underwriting technology layer (B2B SaaS)**, not a balance-sheet lender. Data is ingested strictly via consent under the **RBI Account Aggregator (AA) framework** (via Sahamati-certified AAs) and the GSTN sandbox API. We never scrape credentials, and borrower consent is mandatory."*

### Q3: "What if there is no internet in rural branches?"
> *"Our system includes a **Pure-Python Tree Inference Fallback (`_predict_with_trees`)**. It evaluates the exported JSON decision trees directly without requiring native C-libraries or internet connectivity. A loan officer in a Tier-3 district can run the scoring CLI or offline dashboard on a basic laptop and sanction loans on the spot."*

### Q4: "How does the lender recover the money if there is no collateral?"
> *"Two protective layers:
> 1. **Repayment Structuring:** For high-velocity UPI merchants, we split monthly EMIs into **Daily Repayment Deductions (EDI)** swept automatically via UPI AutoPay or QR settlement before profits can be diverted.
> 2. **CGTMSE Cover:** All sanctioned loans under ₹2 Crore qualify for the Govt of India's CGTMSE scheme, where the guarantee trust covers 75% to 85% of default exposure."*

---

## 🖥️ Live Demo Checklist for the Presentation

1. **Dashboard Overview:** Open `http://localhost:8000/dashboard` in the browser.
2. **Preset 1 (Prime Kirana Store):** Click 'High Volume Retailer' -> Score 98 -> See ₹18.8L limit @ 12.5% -> Highlight 4 SHAP green reasons.
3. **Preset 2 (High-Risk Defaulter):** Click 'High Risk Micro-Vendor' -> Score 0 -> See Declined status, ₹0 limit, and red warning flags (bounces, default history).
4. **Batch Excel Scorer:** Drag and drop `data/sample_100_businesses_input.xlsx` into the Batch Scorer -> Download scored output with all 100 loans sized.
5. **Offline Mode Toggle:** Flip the top-right toggle to 'Offline' -> Score instantly evaluates in < 5ms without network calls.
