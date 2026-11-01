"""SPIKE: callback capture server. Not production code.

Records every POST (path, headers, body, source IP candidates) as one JSON
line, so we can study what Daraja really sends. Exempt from test-first under
ADR-0003. Never import this module from src/.
"""

import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HOST = "127.0.0.1"
PORT = 3000
MAX_BODY_BYTES = 1_000_000
OUT = Path("docs/research/experiments/callbacks.raw")

# Unverified: this is what we expect Daraja wants back. Confirm in experiments.
ACK = b'{"ResultCode":0,"ResultDesc":"Accepted"}'


class Handler(BaseHTTPRequestHandler):
    def _reply(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        self._reply(200, b"capture server is running\n", "text/plain")

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_BODY_BYTES:
            self._reply(413, b'{"error":"too large"}', "application/json")
            return
        body = self.rfile.read(length).decode("utf-8", "replace")
        record = {
            "received_at_utc": datetime.now(timezone.utc).isoformat(),
            "path": self.path,
            "socket_ip": self.client_address[0],
            "x_forwarded_for": self.headers.get("X-Forwarded-For"),
            "cf_connecting_ip": self.headers.get("CF-Connecting-IP"),
            "headers": dict(self.headers),
            "body": body,
        }
        with OUT.open("a") as f:
            f.write(json.dumps(record) + "\n")
        sender = record["cf_connecting_ip"] or record["socket_ip"]
        print(f"{record['received_at_utc']} POST {self.path} from {sender} ({length} bytes)")
        self._reply(200, ACK, "application/json")

    def log_message(self, format: str, *args: object) -> None:
        pass


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"capture server listening on http://{HOST}:{PORT}")
    HTTPServer((HOST, PORT), Handler).serve_forever()
