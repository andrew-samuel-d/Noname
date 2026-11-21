"""Interactive local Setu AA sandbox consent and FI-data demo.

Configuration: SETU_AA_ACCESS_TOKEN and SETU_AA_PRODUCT_INSTANCE_ID.
This contacts only Setu's sandbox; it does not request or print raw account data.
"""

import sys
import time
import webbrowser
from datetime import date, timedelta
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from services.setu_aa import (
    create_consent,
    create_session,
    get_consent,
    get_session,
    revoke_consent,
    summarize_fi_data,
)


def _wait_for_consent(consent_id):
    print("Complete or reject the consent request in the provider page.")
    input("Press Enter after you finish the owner consent step: ")
    for _ in range(24):
        result = get_consent(consent_id)
        status = str(result.get("status", "UNKNOWN")).upper()
        print(f"Consent status: {status}")
        if status in {"ACTIVE", "APPROVED"}:
            return True
        if status in {"REJECTED", "REVOKED", "EXPIRED", "FAILED"}:
            return False
        time.sleep(5)
    raise TimeoutError("Consent is not active yet. Re-run status check later with your provider dashboard.")


def run_flow():
    vua = input("Owner's Setu sandbox VUA/mobile handle (as provided by sandbox): ").strip()
    if not vua:
        raise ValueError("A sandbox VUA is required to create a consent request.")
    start = (date.today() - timedelta(days=90)).isoformat() + "T00:00:00Z"
    end = date.today().isoformat() + "T23:59:59Z"
    consent = create_consent(vua, start, end, "http://localhost:8000/")
    consent_id = consent.get("id")
    consent_url = consent.get("url")
    if not consent_id or not consent_url:
        raise RuntimeError("Setu response did not include a consent ID and review URL.")
    print(f"Consent request created: {consent_id}")
    print("The owner must review the scope and approve it on the provider screen.")
    print(f"Review URL: {consent_url}")
    webbrowser.open(consent_url)
    if not _wait_for_consent(consent_id):
        print("Consent was not approved. No FI data was requested.")
        return

    session = create_session(consent_id, start, end)
    session_id = session.get("id")
    if not session_id:
        raise RuntimeError("Setu response did not include a data-session ID.")
    print(f"Data session started: {session_id}")
    for _ in range(24):
        result = get_session(session_id)
        status = str(result.get("status", "UNKNOWN")).upper()
        print(f"Data session status: {status}")
        if status in {"COMPLETED", "PARTIAL"}:
            print("Cash-flow summary (provider payload held in memory only):")
            import json
            print(json.dumps(summarize_fi_data(result), indent=2))
            return
        if status in {"FAILED", "EXPIRED"}:
            raise RuntimeError(f"Setu data session ended with status {status}.")
        time.sleep(5)
    raise TimeoutError("Data session is still pending. Check the Setu sandbox and try fetching again later.")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "revoke":
        print(revoke_consent(sys.argv[2]))
        return
    if len(sys.argv) != 1:
        raise SystemExit("Usage: python scripts/setu_aa_sandbox.py [revoke CONSENT_ID]")
    run_flow()


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, TimeoutError) as exc:
        raise SystemExit(str(exc)) from exc
