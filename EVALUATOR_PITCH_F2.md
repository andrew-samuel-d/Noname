# Finance · F2 — Credit for the Credit-Invisible

## Round 1 pitch (about one minute)

“Small businesses such as kirana stores, tailors, repair shops, and manufacturers may have daily sales but no formal borrowing history. A blank bureau file does not tell us whether the business is healthy or risky.

We built CashFlowScore, an MSME-focused prototype that uses synthetic bank-flow, UPI, GST-like, and business features. An XGBoost model estimates an approval probability. When formal repayment history is unknown, the scoring service averages the predictions for the two possible history values instead of treating missing data as a clean record. It returns a score, decision estimate, suggested limit, indicative terms, and rule-based reasons. A separate script demonstrates SHAP analysis.

Lenders can score one profile or upload Excel/CSV; the same scoring service also runs from a local command line without starting the API server. We propose a fairer pilot with owner-consented data, a capped starter facility, repayments that flex with sales and protect a minimum cash-flow floor, and a clear path to correct or appeal a rejection.

The current model is trained and evaluated on synthetic labels, so our reported metrics are a prototype check—not real repayment performance. Our next step is a consented pilot with real MSME repayment outcomes and a fairness audit across gender and region.”

## Show the three decisions

1. **Whether:** model score and an eligibility estimate; uncertain or thin-file cases should go to review or a small starter offer, not an automatic final rejection.
2. **How much:** current limit is illustrative and based on balance and transaction volume. A real limit needs net operating cash flow, expenses, current debt payments, and the requested amount.
3. **On what terms:** current terms are illustrative fixed-rate amortization. Product proposal: a small share of daily sales, with a cap, cash-flow floor, hardship pause, clear total cost, and maximum term.

## What is implemented vs proposed

- **Implemented:** synthetic MSME and GST-like daily/monthly data generation; XGBoost training; holdout and cross-validation metrics; individual API scoring; Excel/CSV batch scoring; offline CLI; rule-based reasons and correction/alternative-evidence coaching; SHAP analysis script; Fairlearn MetricFrame group metrics (with built-in fallback); PSI feature-drift screening against the synthetic baseline; bad-month sales-linked repayment arithmetic demo; reject-outcome sensitivity analysis for future pilot data; optional credentialed Setu AA sandbox CLI.
- **Not implemented:** real repayment outcome training, actual gender/region data or parity claims, true reject inference, Finvu AA integration, GSTN integration, on-device SMS parsing, payment collection, dynamic sales-based collections, supplier verification, or lending/CGTMSE eligibility.
- **Production data proposal:** request purpose-specific, revocable owner consent through a Finvu Account Aggregator sandbox for eligible account data; offer optional on-device SMS/UPI parsing only with explicit opt-in; obtain GST information only through an authorized consented route. Minimize and protect data, explain retention, and allow alternative documents.

## Explain the ML accurately

The generator creates synthetic MSME feature rows and assigns labels with a hand-written formula plus noise. XGBoost learns those labels from 11 numeric features. Stratified holdout and five-fold cross-validation test consistency on the generated dataset. Saved metrics: 91% test accuracy, 89.53% precision, 89.53% recall, 89.53% F1, and 0.9652 ROC AUC. Since the target is generated from those inputs, these figures do not establish real-world creditworthiness.

Global feature importance summarizes model use. The SHAP script explains a sample prediction separately; live API reasons are threshold rules, not SHAP. No rejected-applicant repayment outcomes exist, so reject inference is not performed.

## Fairness probe

Run `python scripts/fairness_stress_test.py`. This creates simulated gender and region cohorts with explicit, invented changes to cash-flow features, then compares model approval rates. It is a proxy sensitivity exercise only. It is not an audit of real women-owned or rural businesses and does not validate equal opportunity. A real audit needs appropriately governed protected-group data and observed outcomes; compare selection rates, false-approval/false-rejection rates, and terms across groups, then investigate gaps.

## Judge questions

**Who might the model unfairly reject?**
“We do not have real demographic or outcome data to answer that yet. We provide a synthetic proxy stress test and would audit group selection and error rates in a consented pilot. We would not claim the model is fair based on synthetic data.”

**What happens in a bad month?**
“The current indicative terms still show a fixed monthly estimate. In the Fairness tab, we can simulate a proposed alternative: collect a capped share of daily sales, protect a minimum daily cash floor, and collect nothing on zero-sales days. This is arithmetic only; payment collection, interest servicing, term extension, and hardship operations are not implemented.”

**Where does data come from, with consent?**
“The scoring demo uses generated data. We included an optional Setu AA sandbox CLI that requests a one-time, limited consent, sends the owner to the provider approval page, and fetches only after approval. It requires our own sandbox credentials and has not been connected to this dashboard. Finvu, SMS/UPI parsing, and GSTN are not connected.”

**How do you know whether rejected businesses would repay?**
“We do not. Rejected-applicant outcomes are unobserved; the prototype does not implement reject inference. A carefully limited starter-loan pilot could collect outcomes under clear affordability and consumer-protection controls.”

## Demo path

1. Start: `uv run uvicorn api.main:app --reload`
2. Open the dashboard and score a sample MSME.
3. Select **Unknown — No formal history** to show unknown is not treated as a clean record.
4. Open the fairness tab: distinguish the synthetic stress test and proposals from live integrations.
5. Open Portfolio, download the sample Excel file, upload it, then download the scored workbook.
6. Show fairness sensitivity and drift scripts; explain both compare against synthetic assumptions/baselines, not real-world fairness or repayment performance.
7. Mention offline file scoring: `python offline/offline_score.py data/sample_100_businesses_input.xlsx`.
8. Show the dashboard consent-screen mock and explain its choices stay local. If sandbox credentials are configured, demonstrate Setu consent separately with `python scripts/setu_aa_sandbox.py`; otherwise state that the CLI requires credentials.
9. For command-line analysis, run `python scripts/generate_synthetic_alternative_data.py`, `python scripts/explain.py`, and `python scripts/fairness_stress_test.py`. Explain that all generated records and labels are synthetic.
