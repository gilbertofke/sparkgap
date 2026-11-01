"""SPIKE: token fetch experiment. Not production code.

Calls the Daraja OAuth endpoint in five deliberate ways and records what comes
back, so checks SG-101 and SG-102 rest on observed behavior. Reads credentials
from .env, never prints secrets and masks any token it receives.
"""

import base64
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from sparkgap.masking import mask

# Unverified: confirm the path and base URL against the current Daraja docs.
PATH = "/oauth/v1/generate?grant_type=client_credentials"
OUT = Path("docs/research/experiments/token-fetch.raw")


def load_env(path: str = ".env") -> dict[str, str]:
    """Minimal parser. Keeps quotes, so a stray quote is sent exactly as written."""
    env: dict[str, str] = {}
    for line in Path(path).read_text().splitlines():
        if line.strip() and not line.lstrip().startswith("#") and "=" in line:
            name, _, value = line.partition("=")
            env[name.strip()] = value.strip()
    return env


def basic(key: str, secret: str) -> str:
    return "Basic " + base64.b64encode(f"{key}:{secret}".encode()).decode()


def redact(body: str) -> str:
    try:
        data = json.loads(body)
    except ValueError:
        return body[:300]
    if isinstance(data, dict) and "access_token" in data:
        data["access_token"] = mask(str(data["access_token"]))
    return json.dumps(data)[:300]


def call(base: str, path: str, auth: str | None) -> dict[str, object]:
    request = urllib.request.Request(base + path)
    if auth:
        request.add_header("Authorization", auth)
    started = time.monotonic()
    status: int | None = None
    body = ""
    error = ""
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            status = response.status
            body = response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        status = exc.code
        body = exc.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError) as exc:
        error = f"{type(exc).__name__}: {exc}"
    return {
        "status": status,
        "elapsed_s": round(time.monotonic() - started, 2),
        "body": redact(body),
        "error": error,
    }


def main() -> None:
    env = load_env()
    key = env.get("DARAJA_CONSUMER_KEY", "")
    secret = env.get("DARAJA_CONSUMER_SECRET", "")
    base = env.get("DARAJA_BASE_URL", "")
    print(f"key set: {bool(key)}, secret set: {bool(secret)}, base url: {base or 'missing'}")
    if not (key and secret and base):
        raise SystemExit("Fill DARAJA_CONSUMER_KEY, DARAJA_CONSUMER_SECRET and DARAJA_BASE_URL.")

    good = basic(key, secret)
    cases: list[tuple[str, str, str, str | None]] = [
        ("valid", base, PATH, good),
        ("wrong-secret", base, PATH, basic(key, secret + "x")),
        ("no-auth-header", base, PATH, None),
        ("wrong-path", base, "/oauth/v1/generat?grant_type=client_credentials", good),
        ("unresolvable-host", "https://sandbox.safaricom.invalid", PATH, good),
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    for name, case_base, path, auth in cases:
        result = {
            "case": name,
            "at_utc": datetime.now(timezone.utc).isoformat(),
            **call(case_base, path, auth),
        }
        with OUT.open("a") as f:
            f.write(json.dumps(result) + "\n")
        print(
            f"{name:<18} status={result['status']} {result['elapsed_s']}s "
            f"body={result['body']} error={result['error']}"
        )


if __name__ == "__main__":
    main()
