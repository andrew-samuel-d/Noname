# F2 Judge Defense — Accurate Prototype Claims

## What this project demonstrates

CashFlowScore is an MSME-focused prototype. Its XGBoost model is trained on synthetic approval-rule labels, not observed loan repayment. The project demonstrates local scoring, Excel/CSV batch scoring, SHAP explanations, synthetic cash-flow/GST-like data generation, a Fairlearn-compatible group-metric stress report, and illustrative loan-product scenarios.

Do not describe the prototype as a live lender, production-ready credit model, RBI-certified service, or completed Fairness/Account Aggregator integration.

## Tools and demo commands

Generate synthetic business cash-flow and GST-like records:

```bash
python scripts/generate_synthetic_alternative_data.py
```

Outputs are explicitly synthetic: one year of daily UPI/bank/cash flow estimates, monthly GST-like filing records, and separate synthetic audit-group attributes. They are not downloaded from an Account Aggregator, GSTN, or real merchants.

Generate SHAP global and individual explanations for the saved model:

```bash
python scripts/explain.py
```

The script writes `model/shap_global_importance.csv`, `model/shap_sample_explanation.csv`, and `model/shap_explanations.json`. Values are model-output attributions on the raw margin scale; they do not establish causation or repayment risk. Install project dependencies first; SHAP is included in `requirements.txt`.

Run the group fairness sensitivity report:

```bash
python scripts/fairness_stress_test.py
```

The script uses Fairlearn `MetricFrame` when Fairlearn is installed and a transparent built-in metric fallback otherwise. It compares identical synthetic profiles under explicitly invented women-owned and rural cash-flow shifts. It reports selection rate, TPR, and FPR against the synthetic approval-rule labels. These are not real demographic results, repayment performance, or fairness certification. Protected attributes are not model inputs.

Other prototype checks:

```bash
python scripts/drift_monitor.py incoming.csv
python scripts/reject_inference_sensitivity.py pilot_outcomes.csv
```

The first compares profiles to a synthetic reference distribution. The second varies assumed default rates among rejected applicants in a future consented pilot dataset; it does not infer or invent their actual outcomes.

## Judge questions

### Who could be unfairly rejected?

“We do not yet have real, consented demographic attributes or mature repayment outcomes, so we cannot say who is unfairly rejected in practice. We use a synthetic proxy stress test to see how approval estimates move under disclosed cash-flow shifts. Before any pilot, we would audit selection and error rates across appropriately governed gender and region groups, examine affordability and terms, and investigate gaps.”

### What happens in a bad month?

“The current indicative loan terms are fixed monthly estimates. The Fairness tab also demonstrates a proposed sales-linked schedule that pauses collection on zero-sales days and protects a minimum daily cash floor, with a repayment cap. It is a simplified arithmetic simulation; it is not connected to payments and does not implement hardship operations or term extensions.”

### Where would data come from, with consent?

“The scoring dashboard uses generated profiles only. We added an optional Setu sandbox CLI that requests narrowly scoped consent, redirects the owner to Setu's approval journey, and fetches only after provider confirmation. It has not been run because our team still needs its Setu sandbox credentials. Finvu is not connected. GST data would require an authorized consented route; the generated GST-like records are only sample data.”

### What about applicants rejected by the model?

“Their repayment outcomes are unknown. We do not claim to perform reject inference. The sensitivity script shows how portfolio estimates change across assumed reject default rates, without treating any assumption as an observed outcome. A pilot needs careful outcome collection, review access, and small affordable starter facilities where appropriate.”

## Claims to avoid

- Do not quote fabricated disparate-impact ratios, equal-opportunity gaps, or regulatory thresholds as CashFlowScore results.
- Do not claim pseudo-outcome parceling, reject inference, or real repayment prediction.
- Do not claim the Setu sandbox client has been activated or that Setu production, Finvu, GSTN, SMS parsing, AutoPay, e-NACH, ULI, or a payment rail is connected.
- Do not claim GST filing is mandatory for every small business; missing GST evidence should be treated as unavailable evidence and handled with alternatives.
- Do not call SHAP values causal explanations.
