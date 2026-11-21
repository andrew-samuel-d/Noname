# CashFlowScore — Finance F2

**Challenge:** Design a fairer way to decide which small businesses get credit, how much they get, and on what terms when they have no formal credit history.

CashFlowScore is an MSME-focused prototype. It demonstrates a local model and Excel workflow using synthetic bank-flow, UPI, GST-like, and business features. The scoring dashboard uses generated data. An optional Setu AA sandbox CLI is included but makes external requests only when you configure your sandbox credentials and explicitly start an owner-consent flow. No Finvu, GSTN, or SMS source is connected by default, and the model is not ready for real lending decisions.

## What the prototype does

- Scores a business profile with an XGBoost classifier.
- Returns a probability, 0–100 score, decision estimate, risk tier, and illustrative loan terms.
- Accepts Excel (`.xlsx`) and CSV portfolios and returns a scored file.
- Supports local command-line scoring without starting the FastAPI server.
- Includes SHAP analysis as a separate script. The live API's written reasons are rule-based, not SHAP values.
- Provides actionable input-correction and alternative-evidence suggestions after scoring; these are prompts for review, not promises of approval.
- Includes an illustrative sales-linked repayment simulator with bad-sales days, a protected cash floor, and a total collection cap. It is not connected to payments.
- Shows a revocable, purpose-separated consent-screen mock. It stores only the selected demo scopes in browser local storage and does not connect to or retrieve AA, SMS, or GST data. The browser fallback is a simple heuristic, not the XGBoost model, and does not display model metrics.
- Generates a separate, explicitly synthetic year of daily UPI/bank/cash-flow records and monthly GST-like filing records for data-pipeline demos.
- Uses Fairlearn `MetricFrame` for a synthetic counterfactual group-metric report when the dependency is installed; it falls back to transparent calculations otherwise.
- Includes an optional Setu AA sandbox CLI for consent creation, owner redirection, approved-consent polling, FI session fetching, and consent revocation. It requires Setu sandbox credentials; it is separate from the scoring workflow and does not persist or print raw FI data.

## How the ML works

`scripts/generate_dataset.py` creates synthetic MSME feature rows and generates approval labels from a hand-written rule plus noise. `scripts/train_model.py` trains an XGBoost binary classifier and evaluates it with a stratified holdout split and five-fold cross-validation.

The saved metrics are 91% test accuracy, 89.53% precision and recall, 89.53% F1, 0.9652 ROC AUC, and 91.2% ± 1.29% five-fold accuracy. These measure how well the model learns the generated labels. They are **not** evidence of repayment prediction or performance on real businesses. The training labels are synthetic, and the model has no observed repayment outcomes.

## Fairness and reject inference

Gender and region are not model inputs. Run `python scripts/fairness_stress_test.py` for an illustrative proxy sensitivity check. It applies disclosed synthetic cash-flow shifts to the same profiles and compares selection, TPR, and FPR against generated approval-rule labels using Fairlearn when available; the report is `model/fairness_stress_test.json`. TPR/FPR describe agreement with that synthetic rule, not loan repayment. It is not a fairness certification or evidence about real women-owned or rural businesses.

Generate alternative-data demo files with `python scripts/generate_synthetic_alternative_data.py`. This creates daily cash-flow estimates, monthly GST-like filing rows, and synthetic owner/region group attributes in separate CSVs. They are synthetic and are not AA or GSTN exports.

Run `python scripts/explain.py` to create global and one-business SHAP CSV/JSON summaries in `model/`. The output explains model behavior on synthetic data; it is not causal evidence.

The project does not implement reject inference. It cannot know whether rejected applicants would have repaid because those outcomes are not observed. A real pilot should report selection rates and, once outcome data exists, compare error rates across gender and region. Protected attributes should be used only for properly governed auditing, never silently fed into the decision model.

Run `python scripts/drift_monitor.py incoming.csv` to compare feature distributions with the synthetic training baseline using PSI and missing-value rates. This is a screening tool only; a production monitor needs a representative reference cohort, actual repayment performance, and investigation before model changes.

For a real pilot file with `decision` and `repayment_default_12m` (observed for approved applicants only), run `python scripts/reject_inference_sensitivity.py pilot_outcomes.csv`. It shows portfolio-rate scenarios under different assumed default rates for rejected applicants. Those scenarios are bounds/sensitivity assumptions, not inferred outcomes; the prototype has no repayment labels and cannot estimate reject inference from its synthetic approval labels.

For a credit-invisible applicant, **no credit history means unknown, not clean and not default**. In the prototype, an unknown history is scored by averaging the model's two predictions (no recorded default / recorded default), and the response labels history as unknown. This is a transparent sensitivity treatment, not a learned missing-history model; it needs validation on representative outcomes before use.

## Fairer product proposal

- Use purpose-specific, revocable owner consent and collect only necessary information. An optional Setu AA sandbox CLI is implemented for authorized testing. Finvu, on-device SMS/UPI parsing, and GSTN integrations are not connected; GST-like data is generated locally.
- For the Setu sandbox flow, set `SETU_AA_CLIENT_ID`, `SETU_AA_CLIENT_SECRET`, and `SETU_AA_PRODUCT_INSTANCE_ID` in the local environment, then run `python scripts/setu_aa_sandbox.py`. The CLI obtains and caches a short-lived sandbox access token in memory. It asks for the owner's sandbox VUA, requests one-time deposit transaction access, opens Setu's consent page, waits for approval, fetches a data session, and prints only derived cash-flow aggregates. To revoke: `python scripts/setu_aa_sandbox.py revoke CONSENT_ID`. It is sandbox-only and needs your own Setu credentials; the app dashboard does not call it.
- Offer alternative evidence when an owner has no bureau, GST, or digital records.
- Consider an affordable, capped starter loan for uncertain cases, then grow the limit only after observed repayment performance.
- Explore repayment as a small share of daily sales, with a disclosed cap, a minimum cash-flow floor, and a hardship pause for bad months. This is a design proposal, not a payment feature in the demo.
- The local `/product/simulate-sales-repayment` endpoint and Fairness tab button demonstrate the arithmetic on a sample 14-day sales sequence. Interest and hardship rules remain simplified and need lender/legal review.
- Give declined applicants specific, correctable reasons and a human review route. Do not use an LLM to invent reasons.

## Run the demo

Install the dependencies (including SHAP and Fairlearn) before running the analysis scripts:

```bash
pip install -r requirements.txt
```

Start the local dashboard/API:

```bash
uv run uvicorn api.main:app --reload
```

Open `http://localhost:8000`, choose **Portfolio**, download the sample workbook, upload it, then download the scored file. The upload requires the 11 feature column names in the sample workbook and numeric values for each required feature.

Score locally without starting the API server:

```bash
python offline/offline_score.py data/sample_100_businesses_input.xlsx
```

Optional output path:

```bash
python offline/offline_score.py input.xlsx output.xlsx
```

## Implemented technology & streaming architecture

CashFlowScore is built as a cloud-native, event-driven MSME underwriting engine:

- **Event Streaming & Ingestion:** Apache Kafka (port `9092`) with consumer group `cg.underwriting.v2`. Operates natively via `kafka-python` when a cluster is reachable, and seamlessly falls back to an embedded high-throughput in-memory partitioned broker with partition hashing (`hash(merchant_id) % 4`), strict per-merchant time-series ordering, and exactly-once semantics (EOS).
- **Core Topics:**
  - `msme.events.upi`: NPCI 24x7 merchant QR payment settlements, velocity indicators, and transaction spikes.
  - `msme.events.banking`: Account Aggregator (AA) Setu/Finvu daily transaction stream, NACH mandate clearances, and cheque/mandate bounce alerts.
  - `msme.events.gst`: Monthly GSTR-3B filings, e-Way bills, and counterparty B2B turnover reconciliations.
  - `msme.scores.realtime`: Low-latency credit scores, risk tiers, and dynamic loan sanction letters broadcast to bank Loan Origination Systems (LOS).
- **Machine Learning & Fairness:** XGBoost binary classifier, scikit-learn, Fairlearn (`MetricFrame` demographic parity and equalized odds proxy audit), and SHAP tree explainability.
- **Backend & APIs:** FastAPI, Uvicorn, Pandas, NumPy, OpenPyXL (Excel portfolio processing).
- **Frontend Architecture:** Modern React 18 modular architecture (`frontend/src/App.jsx`, `frontend/src/main.jsx`, `frontend/vite.config.js`) with dynamic Vite tooling and live FastAPI-served interactive dashboard (`frontend/index.html`) featuring real-time Kafka event stream tickers, stress-testing simulators, interactive loan sizing sliders, and automated PDF sanction letter printing.
