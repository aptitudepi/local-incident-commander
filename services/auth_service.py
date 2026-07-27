#!/usr/bin/env python3
"""Auth microservice for Local Incident Commander demo."""
import json, time, random, logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("auth-service")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(random.uniform(0.005, 0.02))
        if random.random() < 0.005:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error":"unauthorized"}')
            logger.warning("GET %s -> 401", self.path)
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok","service":"auth"}')
            logger.info("GET %s -> 200", self.path)
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b"{}"
        logger.info("POST %s body=%s", self.path, body[:200])
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status":"ok","token":"eyJdemo.eyJ0eXAiOiJKV1QifQ.fake"}')
    def log_message(self, fmt, *args):
        logger.debug(fmt, *args)

if __name__ == "__main__":
    port = int(__import__("os").environ.get("PORT", 5003))
    server = HTTPServer(("0.0.0.0", port), Handler)
    logger.info("auth-service listening on :%d", port)
    server.serve_forever()
