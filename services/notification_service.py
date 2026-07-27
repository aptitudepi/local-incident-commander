#!/usr/bin/env python3
"""Notification microservice for Local Incident Commander demo."""
import json, time, random, logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("notification-service")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(random.uniform(0.005, 0.01))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status":"ok","service":"notification"}')
        logger.info("GET %s -> 200", self.path)
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b"{}"
        logger.info("POST %s body=%s", self.path, body[:200])
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status":"ok","notifications_sent":1}')
    def log_message(self, fmt, *args):
        logger.debug(fmt, *args)

if __name__ == "__main__":
    port = int(__import__("os").environ.get("PORT", 5005))
    server = HTTPServer(("0.0.0.0", port), Handler)
    logger.info("notification-service listening on :%d", port)
    server.serve_forever()
