#!/usr/bin/env python3
"""Payment microservice for Local Incident Commander demo."""
import json, time, random, logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("payment-service")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(random.uniform(0.02, 0.08))
        if random.random() < 0.01:
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b'{"error":"service_unavailable"}')
            logger.warning("GET %s -> 503", self.path)
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok","service":"payment"}')
            logger.info("GET %s -> 200", self.path)
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b"{}"
        logger.info("POST %s body=%s", self.path, body[:200])
        time.sleep(random.uniform(0.05, 0.15))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status":"ok","transaction_id":"txn_' + str(random.randint(10000,99999)).encode() + b'"}')
    def log_message(self, fmt, *args):
        logger.debug(fmt, *args)

if __name__ == "__main__":
    port = int(__import__("os").environ.get("PORT", 5002))
    server = HTTPServer(("0.0.0.0", port), Handler)
    logger.info("payment-service listening on :%d", port)
    server.serve_forever()
