"""Minimal Setu AA sandbox client; all requests require an approved owner flow."""

import json
import os
import time
import urllib.error
import urllib.request

SANDBOX_BASE = "https://fiu-sandbox.setu.co"
TOKEN_URL = "https://uat.setu.co/api/v2/auth/token"
_cached_token = None
_token_expiry = 0.0


def _config():
    global _cached_token, _token_expiry
    product_id = os.environ.get("SETU_AA_PRODUCT_INSTANCE_ID", "").strip()
    token = os.environ.get("SETU_AA_ACCESS_TOKEN", "").strip()
    client_id = os.environ.get("SETU_AA_CLIENT_ID", "").strip()
    client_secret = os.environ.get("SETU_AA_CLIENT_SECRET", "").strip()
    if not product_id:
        raise RuntimeError("Set SETU_AA_PRODUCT_INSTANCE_ID from your Setu sandbox product configuration.")
    if token:
        return token, product_id
    if not client_id or not client_secret:
        raise RuntimeError("Set SETU_AA_CLIENT_ID, SETU_AA_CLIENT_SECRET, and SETU_AA_PRODUCT_INSTANCE_ID.")
    if _cached_token and time.monotonic() < _token_expiry:
        return _cached_token, product_id

    auth_request = urllib.request.Request(
        TOKEN_URL,
        data=json.dumps({"clientID": client_id, "secret": client_secret}).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(auth_request, timeout=30) as response:
            auth_response = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        raise RuntimeError("Could not authenticate with Setu sandbox. Check your test OAuth credentials.") from exc
    token = (auth_response.get("data") or {}).get("token")
    if not token:
        raise RuntimeError("Setu token response did not include a token. Check that your OAuth key has sandbox access.")
    _cached_token = token
    expires_in = int((auth_response.get("data") or {}).get("expiresIn", 1800))
    _token_expiry = time.monotonic() + max(60, expires_in - 60)
    return token, product_id


def _request(method, path, payload=None):
    token, product_id = _config()
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        SANDBOX_BASE + path,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "x-product-instance-id": product_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"Setu sandbox returned HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach the Setu sandbox: {exc.reason}") from exc


def create_consent(vua, start_date, end_date, redirect_url):
    """Create a one-time deposit-transaction consent for owner review."""
    payload = {
        "consentDuration": {"unit": "DAY", "value": "30"},
        "consentMode": "STORE",
        "fetchType": "ONETIME",
        "consentTypes": ["TRANSACTIONS"],
        "fiTypes": ["DEPOSIT"],
        "vua": vua,
        "purpose": {
            "category": {"type": "string"},
            "refUri": "https://api.rebit.org.in/aa/purpose/105.xml",
            "code": "105",
            "text": "One-time cash-flow review for an MSME credit assessment",
        },
        "dataRange": {"from": start_date, "to": end_date},
        "dataLife": {"unit": "DAY", "value": "30"},
        "frequency": {"unit": "MONTHLY", "value": 1},
        "redirectUrl": redirect_url,
        "context": [{"key": "purposeDescription", "value": "MSME cash-flow assessment"}],
    }
    return _request("POST", "/consents", payload)


def get_consent(consent_id):
    return _request("GET", f"/consents/{consent_id}")


def create_session(consent_id, start_date, end_date):
    return _request("POST", "/sessions", {
        "consentId": consent_id,
        "dataRange": {"from": start_date, "to": end_date},
        "format": "json",
    })


def get_session(session_id):
    return _request("GET", f"/sessions/{session_id}")


def revoke_consent(consent_id):
    return _request("POST", f"/v2/consents/{consent_id}/revoke")


def summarize_fi_data(payload):
    """Return cash-flow aggregates only; do not persist or print raw FI data."""
    transactions = []
    for fip in payload.get("fips", []) or []:
        accounts = list(fip.get("accounts", []) or [])
        for item in fip.get("data", []) or []:
            if isinstance(item, dict):
                accounts.append(item)
        for account in accounts:
            if str(account.get("status", account.get("FIstatus", ""))).upper() not in {"DELIVERED", "READY", ""}:
                continue
            root = account.get("data") or account.get("decryptedFI") or {}
            if isinstance(root, dict):
                root = root.get("decryptedFI") or root
            account_data = root.get("account", root) if isinstance(root, dict) else {}
            txn_root = account_data.get("transactions", {}) if isinstance(account_data, dict) else {}
            rows = txn_root.get("transaction", []) if isinstance(txn_root, dict) else []
            if isinstance(rows, dict):
                rows = [rows]
            transactions.extend(row for row in rows if isinstance(row, dict))

    monthly_upi = 0.0
    monthly_other_credit = 0.0
    balances = []
    monthly_inflows = {}
    observed_months = set()
    bounce_count = 0
    for row in transactions:
        amount = abs(float(row.get("amount") or 0))
        kind = str(row.get("type", "")).upper()
        mode = str(row.get("mode", "")).upper()
        narration = str(row.get("narration", "")).upper()
        date = str(row.get("transactionTimestamp", row.get("valueDate", "")))[:7]
        if date:
            observed_months.add(date)
        if kind == "CREDIT":
            if mode.startswith("UPI"):
                monthly_upi += amount
            else:
                monthly_other_credit += amount
            if date:
                monthly_inflows[date] = monthly_inflows.get(date, 0.0) + amount
        if row.get("currentBalance") not in (None, ""):
            balances.append(float(row["currentBalance"]))
        if kind == "DEBIT" and any(term in narration for term in ("BOUNCE", "RETURN", "NACH RTN", "CHEQUE RTN")):
            bounce_count += 1

    months = max(1, len(observed_months))
    monthly_values = [monthly_inflows.get(month, 0.0) for month in sorted(observed_months)]
    mean = sum(monthly_values) / len(monthly_values) if monthly_values else 0.0
    cv = (sum((value - mean) ** 2 for value in monthly_values) / len(monthly_values)) ** 0.5 / mean if mean else 1.0
    return {
        "source": "Setu AA sandbox FI data",
        "transaction_count": len(transactions),
        "monthly_upi_credit_inr_estimate": round(monthly_upi / months, 2),
        "monthly_non_upi_credit_inr_estimate": round(monthly_other_credit / months, 2),
        "average_observed_balance_inr": round(sum(balances) / len(balances), 2) if balances else None,
        "observed_return_or_bounce_count": bounce_count,
        "monthly_inflow_stability_index_estimate": round(max(0, min(100, 100 * (1 - cv))), 1),
        "gst_fields": None,
        "cash_sales": None,
        "business_age": None,
        "limitations": [
            "Sandbox FI data may be synthetic provider test data, not a real bank statement.",
            "UPI/bounce classification uses transaction mode and narration heuristics; review before use.",
            "GST, cash sales, business age, expenses, and loan obligations are not inferred here.",
            "This summary is not sufficient by itself for a lending decision.",
        ],
    }
