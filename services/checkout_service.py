#!/usr/bin/env python3
"""Checkout microservice for Local Incident Commander demo."""
import json, time, random, logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("checkout-service")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(random.uniform(0.01, 0.05))
        if random.random() < 0.02:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"error":"internal_error"}')
            logger.warning("GET %s -> 500", self.path)
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok","service":"checkout"}')
            logger.info("GET %s -> 200", self.path)
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b"{}"
        logger.info("POST %s body=%s", self.path, body[:200])
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status":"ok","processed":true}')
    def log_message(self, fmt, *args):
        logger.debug(fmt, *args)

if __name__ == "__main__":
    port = int(__import__("os").environ.get("PORT", 5001))
    server = HTTPServer(("0.0.0.0", port), Handler)
    logger.info("checkout-service listening on :%d", port)
    server.serve_forever()
