"""Transparent cash-flow repayment design calculations for the F2 prototype."""

from typing import Iterable


def simulate_sales_linked_repayment(
    daily_sales: Iterable[float],
    principal_inr: float,
    monthly_rate_pct: float = 1.25,
    sales_share_pct: float = 8.0,
    protected_daily_cash_inr: float = 500.0,
    total_repayment_cap_multiple: float = 1.25,
) -> dict:
    """Simulate daily collections with a floor, total cap, and bad-day pause.

    This is an educational product scenario, not a payment instruction or quote.
    """
    sales = [float(value) for value in daily_sales]
    if not sales or any(value < 0 for value in sales):
        raise ValueError("Provide at least one non-negative daily sales value.")
    if principal_inr <= 0 or not 0 < sales_share_pct <= 100:
        raise ValueError("Principal must be positive and sales share must be 1–100%.")
    if monthly_rate_pct < 0 or protected_daily_cash_inr < 0 or total_repayment_cap_multiple < 1:
        raise ValueError("Rate/floor/cap settings are outside allowed ranges.")

    outstanding = float(principal_inr)
    cap = float(principal_inr) * float(total_repayment_cap_multiple)
    repaid = 0.0
    daily_rows = []
    for day, gross_sales in enumerate(sales, start=1):
        interest = outstanding * (monthly_rate_pct / 100.0) / 30.0
        available_after_floor = max(0.0, gross_sales - protected_daily_cash_inr)
        proposed = min(available_after_floor * sales_share_pct / 100.0, outstanding + interest)
        collection = min(proposed, max(0.0, cap - repaid))
        outstanding = max(0.0, outstanding + interest - collection)
        repaid += collection
        daily_rows.append({
            "day": day,
            "sales_inr": round(gross_sales, 2),
            "protected_floor_inr": round(min(gross_sales, protected_daily_cash_inr), 2),
            "collection_inr": round(collection, 2),
            "outstanding_inr": round(outstanding, 2),
            "paused": collection == 0.0,
        })

    return {
        "status": "illustrative_simulation_only",
        "principal_inr": round(float(principal_inr), 2),
        "sales_share_pct": float(sales_share_pct),
        "protected_daily_cash_inr": float(protected_daily_cash_inr),
        "total_repayment_cap_inr": round(cap, 2),
        "collected_inr": round(repaid, 2),
        "remaining_balance_inr": round(outstanding, 2),
        "days_simulated": len(sales),
        "days_with_no_collection": sum(row["paused"] for row in daily_rows),
        "schedule": daily_rows,
        "warning": "Interest accrual, hardship handling, legal terms, and affordability need lender review; this is not a live payment feature.",
    }
