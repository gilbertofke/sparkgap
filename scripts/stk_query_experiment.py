"""SPIKE: STK push query experiment. Not production code.

Asks Daraja for the status of one earlier STK push, by CheckoutRequestID.
Reuses the helpers from stk_push_experiment.py. The CheckoutRequestID embeds
digits of the phone number, so it is masked in everything saved or printed.

Usage: uv run python scripts/stk_query_experiment.py <CheckoutRequestID>
"""

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from stk_push_experiment import NAIROBI, get_token, load_env, make_password, send

QUERY_PATH = "/mpesa/stkpushquery/v1/query"
OUT = Path("docs/research/experiments/stk-query.raw")


def mask_ids(text: str) -> str:
    """Keep 'ws_CO_' and the 14-digit date part; hide the phone-bearing tail."""
    return re.sub(r"(ws_CO_\d{14})\d+", r"\1<masked>", text)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: stk_query_experiment.py <CheckoutRequestID>")
    checkout_id = sys.argv[1]

    env = load_env()
    base = env["DARAJA_BASE_URL"]
    shortcode = env["DARAJA_SHORTCODE"]
    token = get_token(base, env["DARAJA_CONSUMER_KEY"], env["DARAJA_CONSUMER_SECRET"])
    timestamp = datetime.now(NAIROBI).strftime("%Y%m%d%H%M%S")
    payload = {
        "BusinessShortCode": shortcode,
        "Password": make_password(shortcode, env["DARAJA_PASSKEY"], timestamp),
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_id,
    }

    sent_at = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    status, body, error = send(
        base + QUERY_PATH,
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        payload,
    )
    elapsed = round(time.monotonic() - started, 2)

    record = {
        "case": "stk-query",
        "sent_at_utc": sent_at,
        "timestamp_used": timestamp,
        "checkout_request_id": mask_ids(checkout_id),
        "status": status,
        "elapsed_s": elapsed,
        "body": mask_ids(body[:600]),
        "error": error,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("a") as f:
        f.write(json.dumps(record) + "\n")
    print(f"queried {record['checkout_request_id']} at {sent_at}")
    print(f"status={status} {elapsed}s error={error}")
    print(f"body={record['body']}")


if __name__ == "__main__":
    main()
