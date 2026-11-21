import os
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure repository root is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from api.scoring_service import score_business
from services.predictor import predict_score
from services.explainability import explain_prediction, get_global_feature_importance
from services.cache import get_cache, set_cache

def test_all():
    print("========================================")
    print("[TEST] RUNNING CASHFLOWSCORE-ML TEST SUITE")
    print("========================================")

    # 1. Full feature profile test
    full_sample = {
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
    }

    res = score_business(full_sample)
    print("\n[OK] Test 1: Full Healthy Business Scoring")
    print(f"  Score: {res['score']}/100 | Decision: {res['decision']} | Tier: {res['risk_tier']}")
    print(f"  Probability: {res['probability']} | Reasons: {res['top_reasons']}")
    assert res['score'] >= 50, "Healthy business should have score >= 50"
    assert res['decision'] == "Approved"

    # 2. High risk profile test
    risky_sample = {
        "business_age_years": 1,
        "monthly_upi_volume": 20000,
        "monthly_bank_volume": 100000,
        "monthly_cash_volume": 50000,
        "gst_filing_regularity": 60,
        "gst_turnover": 800000,
        "bounce_frequency": 6,
        "avg_monthly_balance": 15000,
        "income_stability": 45,
        "seasonality_score": 30,
        "loan_default_history": 1
    }

    res_risky = score_business(risky_sample)
    print("\n[OK] Test 2: High Risk Profile Scoring")
    print(f"  Score: {res_risky['score']}/100 | Decision: {res_risky['decision']} | Tier: {res_risky['risk_tier']}")
    print(f"  Probability: {res_risky['probability']} | Reasons: {res_risky['top_reasons']}")
    assert res_risky['score'] < 50, "High risk business should have score < 50"
    assert res_risky['decision'] == "Rejected"

    # 3. Partial / missing features test (Bug fix verification for KeyError)
    partial_sample = {
        "business_age_years": 5,
        "avg_monthly_balance": 300000
    }
    res_partial = score_business(partial_sample)
    print("\n[OK] Test 3: Partial Features (KeyError Resilience)")
    print(f"  Score: {res_partial['score']}/100 | Decision: {res_partial['decision']}")
    assert "error" not in res_partial, f"Should not error on partial features: {res_partial.get('error')}"

    # 4. Predictor service test
    s, p = predict_score(full_sample)
    print("\n[OK] Test 4: services.predictor")
    print(f"  Predict score: {s}, probability: {p:.4f}")
    assert 0 <= s <= 100 and 0.0 <= p <= 1.0

    # 5. Explainability test
    exp = explain_prediction(full_sample)
    print("\n[OK] Test 5: services.explainability")
    print(f"  Top 3 local drivers: {exp[:3]}")
    assert len(exp) == 11, f"Expected 11 feature explanations, got {len(exp)}"

    # 6. Global feature importance test
    global_imp = get_global_feature_importance()
    print("\n[OK] Test 6: Global Feature Importance")
    print(f"  Total ranked features: {len(global_imp)}")
    print(f"  Top feature: {global_imp[0]['feature']} ({global_imp[0]['importance'] * 100:.1f}%)")
    assert len(global_imp) == 11, f"Expected 11 features in importance list, got {len(global_imp)}"

    # 7. Cache test
    set_cache("test_biz_123", {"score": 85, "status": "Approved"})
    cached = get_cache("test_biz_123")
    print("\n[OK] Test 7: Cache Fallback (Redis / In-Memory)")
    print(f"  Cached value: {cached}")
    assert cached is not None and cached["score"] == 85

    # 8. F2 Underwriting Terms & Sizing Test (Who? How Much? What Terms?)
    print("\n[OK] Test 8: F2 Credit Sizing & Terms Verification")
    terms_healthy = res.get("credit_terms")
    assert terms_healthy is not None, "credit_terms must be present in score_business output"
    assert terms_healthy["eligible"] is True, "Healthy applicant must be eligible for credit"
    assert terms_healthy["max_credit_limit_inr"] > 0, "Credit limit must be > 0"
    assert terms_healthy["interest_rate_pct"] in [12.5, 14.5, 16.5, 19.0], "Interest rate must match risk tiers"
    assert terms_healthy["tenure_months"] in [9, 12, 18, 24], "Tenure must be valid"
    assert terms_healthy["monthly_emi_inr"] > 0, "Monthly EMI must be calculated"
    assert terms_healthy["daily_repayment_inr"] > 0, "Daily EDI must be calculated"
    print(f"  Approved Terms: Limit=Rs. {terms_healthy['max_credit_limit_inr']:,} | Rate={terms_healthy['interest_rate_pct']}% | EMI=Rs. {terms_healthy['monthly_emi_inr']:,}")

    terms_risky = res_risky.get("credit_terms")
    assert terms_risky is not None, "credit_terms must be present for rejected applicant"
    assert terms_risky["eligible"] is False, "High-risk applicant must not be eligible"
    assert terms_risky["max_credit_limit_inr"] == 0, "Rejected applicant limit must be 0"
    print(f"  Rejected Terms: Eligible={terms_risky['eligible']} | Limit=Rs. {terms_risky['max_credit_limit_inr']}")

    print("\n========================================")
    print("[SUCCESS] ALL 8 TESTS PASSED SUCCESSFULLY!")
    print("========================================")

if __name__ == "__main__":
    test_all()
