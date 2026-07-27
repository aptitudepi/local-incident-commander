#!/usr/bin/env python3
"""API Gateway microservice for Local Incident Commander demo."""
import json, time, random, logging, urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("api-gateway")

SERVICES = {
    "/checkout":  ("http://localhost:5001", 5001),
    "/payment":   ("http://localhost:5002", 5002),
    "/auth":      ("http://localhost:5003", 5003),
    "/inventory": ("http://localhost:5004", 5004),
    "/notify":    ("http://localhost:5005", 5005),
}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        for prefix, (url, port) in SERVICES.items():
            if self.path.startswith(prefix):
                try:
                    req = urllib.request.Request(url + self.path, method="GET")
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        data = resp.read()
                    self.send_response(resp.status)
                    self.end_headers()
                    self.wfile.write(data)
                    logger.info("Proxied GET %s -> %s%s -> %d", self.path, url, self.path, resp.status)
                except Exception as e:
                    self.send_response(502)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
                    logger.error("Proxy error GET %s -> %s: %s", self.path, url, e)
                return
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'{"error":"route_not_found"}')
    def do_POST(self):
        for prefix, (url, port) in SERVICES.items():
            if self.path.startswith(prefix):
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length) if content_length else b"{}"
                try:
                    req = urllib.request.Request(url + self.path, data=body, headers={"Content-Type": "application/json"}, method="POST")
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        data = resp.read()
                    self.send_response(resp.status)
                    self.end_headers()
                    self.wfile.write(data)
                    logger.info("Proxied POST %s -> %s%s -> %d", self.path, url, self.path, resp.status)
                except Exception as e:
                    self.send_response(502)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
                    logger.error("Proxy error POST %s -> %s: %s", self.path, url, e)
                return
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'{"error":"route_not_found"}')
    def log_message(self, fmt, *args):
        logger.debug(fmt, *args)

if __name__ == "__main__":
    port = int(__import__("os").environ.get("PORT", 5000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    logger.info("api-gateway listening on :%d", port)
    server.serve_forever()
