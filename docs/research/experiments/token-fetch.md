# Token fetch experiment

Date run: 2026-11-01. Environment: Daraja sandbox. Script: `scripts/token_experiment.py` (spike, ADR-0003).
Raw output is gitignored (`docs/research/experiments/token-fetch.raw`). Tokens are masked.

## Purpose

Observe what the Daraja OAuth endpoint actually returns for five deliberate cases, so checks SG-101 (can a token be fetched) and SG-102 (why did it fail) rest on observed behavior and not on assumptions.

## Method

Five requests, run twice, one minute apart. The base URL and credentials came from `.env`. The `.invalid` host case never leaves the machine.

## Predictions vs observed

| Case | Predicted | Observed (both runs identical) |
|---|---|---|
| valid | 200, JSON | 200, JSON with `access_token` and `expires_in` |
| wrong-secret | 401, error | 400, empty body |
| no-auth-header | 401, error | 400, JSON, `errorCode 400.008.01`, "Invalid Authentication passed" |
| wrong-path (`generat`) | 400, error | 200, empty body |
| unresolvable-host | 400, error | no status, `URLError: Name or service not known`, about 0.01 to 0.15 s |

Score: 1 of 5 predicted correctly. The gaps are the useful part.

## Findings

1. A 200 status does not prove success. A misspelled path returned 200 with an empty body. SG-101 must require an `access_token` in the body.
2. Bad credentials return 400, not 401. Both a wrong secret and a missing header gave 400.
3. Wrong secret and missing header differ only in the body. Missing header returns JSON with `errorCode 400.008.01`. Wrong secret returns an empty body. SG-102 cannot separate them by status code.
4. No network gives no status code. A `URLError` means Daraja was never reached. This is the clean signal for "unreachable".
5. `expires_in` came back as a string (`"3599"`), while the official page shows a number. Do not assume a type.
6. A fresh token and a fresh `requestId` were issued on every call. Match on `errorCode`, not `requestId`.

## Verified against official documentation

Source: Safaricom Developer Portal, Authorization API page (`https://developer.safaricom.co.ke/apis/Authorization`), content pasted by Tangus on 2026-11-01.

- Sandbox URL and path: `https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials`. Matches `.env` and the script.
- Auth: Basic, with consumer key and secret. Token expiry 3600 s.
- Documented errors: `400.008.01` invalid authentication type, `400.008.02` invalid grant type.
- Consumer key and secret come from the Daraja My Apps page.

The docs do not describe the wrong-secret empty-body 400 or the wrong-path 200. Those two are observation only.

## Provenance of other facts

- Sandbox shortcode and passkey were found in the portal at `https://developer.safaricom.co.ke/dashboard/myapps` (stated by Tangus). Our earlier guess of the Test Credentials page was wrong.

## Not yet tested

- `400.008.02` (invalid grant type): documented, not triggered.
- Whether a new token invalidates the previous one: documented, not tested.
- Whether other wrong paths also return 200 with an empty body.
- Whether the empty-body 400 for a wrong secret is stable over time. Two runs agree.
