"""SPIKE: STK push experiment. Not production code.

Sends one valid STK push to the Daraja sandbox and records the immediate reply.
The real payment result arrives later as a callback on DARAJA_CALLBACK_URL, which
scripts/capture_server.py records. Reads credentials from .env, never prints the
passkey, the password or the token, and masks the phone number in saved output.

Usage: uv run python scripts/stk_push_experiment.py <phone> [amount]
"""

import base64
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sparkgap.masking import mask

TOKEN_PATH = "/oauth/v1/generate?grant_type=client_credentials"
PUSH_PATH = "/mpesa/stkpush/v1/processrequest"
OUT = Path("docs/research/experiments/stk-push.raw")
# Kenya has no daylight saving, so a fixed UTC+3 offset equals Nairobi time.
NAIROBI = timezone(timedelta(hours=3))


def load_env(path: str = ".env") -> dict[str, str]:
    env: dict[str, str] = {}
    for line in Path(path).read_text().splitlines():
        if line.strip() and not line.lstrip().startswith("#") and "=" in line:
            name, _, value = line.partition("=")
            env[name.strip()] = value.strip()
    return env


def send(
    url: str, headers: dict[str, str], payload: dict[str, object] | None = None
) -> tuple[int | None, str, str]:
    """Return (status, body, error). A missing status means no answer was received."""
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.status, response.read().decode("utf-8", "replace"), ""
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace"), ""
    except (urllib.error.URLError, TimeoutError) as exc:
        return None, "", f"{type(exc).__name__}: {exc}"


def get_token(base: str, key: str, secret: str) -> str:
    basic = base64.b64encode(f"{key}:{secret}".encode()).decode()
    status, body, error = send(base + TOKEN_PATH, {"Authorization": f"Basic {basic}"})
    try:
        token = str(json.loads(body)["access_token"])
    except (ValueError, KeyError, TypeError):
        message = f"No token (status={status}, error={error}). Run the token experiment."
        raise SystemExit(message) from None
    return token


def make_password(shortcode: str, passkey: str, timestamp: str) -> str:
    return base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: stk_push_experiment.py <phone> [amount]")
    phone = sys.argv[1]
    amount = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    env = load_env()
    names = ["DARAJA_CONSUMER_KEY", "DARAJA_CONSUMER_SECRET", "DARAJA_SHORTCODE"]
    names += ["DARAJA_PASSKEY", "DARAJA_CALLBACK_URL", "DARAJA_BASE_URL"]
    missing = [name for name in names if not env.get(name)]
    if missing:
        raise SystemExit(f"Missing in .env: {', '.join(missing)}")
    base = env["DARAJA_BASE_URL"]
    shortcode = env["DARAJA_SHORTCODE"]

    token = get_token(base, env["DARAJA_CONSUMER_KEY"], env["DARAJA_CONSUMER_SECRET"])
    timestamp = datetime.now(NAIROBI).strftime("%Y%m%d%H%M%S")
    payload: dict[str, object] = {
        "BusinessShortCode": shortcode,
        "Password": make_password(shortcode, env["DARAJA_PASSKEY"], timestamp),
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": env["DARAJA_CALLBACK_URL"],
        "AccountReference": "SparkgapTest",
        "TransactionDesc": "Sparkgap Day 0",
    }

    sent_at = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    status, body, error = send(
        base + PUSH_PATH,
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        payload,
    )
    elapsed = round(time.monotonic() - started, 2)

    saved_request = {**payload, "Password": "<redacted>", "PartyA": mask(phone)}
    saved_request["PhoneNumber"] = mask(phone)
    record = {
        "case": "valid-push",
        "sent_at_utc": sent_at,
        "timestamp_used": timestamp,
        "request": saved_request,
        "status": status,
        "elapsed_s": elapsed,
        "body": body[:600],
        "error": error,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("a") as f:
        f.write(json.dumps(record) + "\n")
    print(f"sent at {sent_at}  timestamp used {timestamp}")
    print(f"status={status} {elapsed}s error={error}")
    print(f"body={body[:600]}")


if __name__ == "__main__":
    main()
