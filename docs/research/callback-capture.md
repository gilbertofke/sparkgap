# Callback capture server

Status: spike. Exempt from test-first under ADR-0003 and never imported by `src/`.

## Purpose

Record exactly what arrives at a callback URL, so facts about Daraja callbacks
are observed instead of assumed. The raw capture is gitignored. Only cleaned,
redacted summaries belong in this directory.

## How to run

In one terminal, from the repository root:

    uv run python scripts/capture_server.py

In another terminal, open a temporary public HTTPS address:

    cloudflared tunnel --url http://localhost:3000

The tunnel prints an address of the form `https://<words>.trycloudflare.com`.
It changes on every restart and works only while cloudflared runs. Stop the
tunnel when you are not experimenting.

## What it records

One JSON line per POST in `docs/research/experiments/callbacks.raw`: UTC
receive time, path, three source address candidates (`socket_ip`,
`x_forwarded_for`, `cf_connecting_ip`), all headers and the body.

## Observations

Verified by our own test on 2026-11-01. The test was a `curl` through the
quick tunnel, not a Daraja callback, so it says nothing about Safaricom:

- `socket_ip` was `127.0.0.1`, because the final hop is the local tunnel client.
- Cloudflare set `CF-Connecting-IP` and `X-Forwarded-For` to the sender's
  public address.
- Cloudflare also added `Cf-Ipcountry`, `Cf-Ray`, `Cdn-Loop` and `Cf-Visitor`.
- `Cf-Visitor` reported the original scheme as `https`.

Not yet observed from Daraja, so all of this is unverified: the callback
payload shape, which source addresses Safaricom uses, which headers it sends,
whether failed deliveries are retried, what response it expects, and whether
failure payloads omit `CallbackMetadata`.

## Known limits

- It handles one request at a time.
- It trusts the `Content-Length` header. A request without it is read as empty,
  and a negative value could make the server wait until the connection closes.
- It accepts every POST on every path and answers with a fixed acknowledgment
  that has not been confirmed against Daraja.
- Behind a public tunnel, anyone who learns the address can post to it.
  Treat everything captured as untrusted input.
- The raw log can contain phone numbers and receipt data from sandbox runs.
