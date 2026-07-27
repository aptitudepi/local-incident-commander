#!/usr/bin/env python3
"""Inventory microservice for Local Incident Commander demo."""
import json, time, random, logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("inventory-service")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(random.uniform(0.01, 0.03))
        if random.random() < 0.01:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error":"not_found"}')
            logger.warning("GET %s -> 404", self.path)
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok","service":"inventory","items":1024}')
            logger.info("GET %s -> 200", self.path)
    def log_message(self, fmt, *args):
        logger.debug(fmt, *args)

if __name__ == "__main__":
    port = int(__import__("os").environ.get("PORT", 5004))
    server = HTTPServer(("0.0.0.0", port), Handler)
    logger.info("inventory-service listening on :%d", port)
    server.serve_forever()
