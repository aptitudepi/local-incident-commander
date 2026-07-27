import json
import os
import socket
import threading
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.api_routes import router as api_router

app = FastAPI(title="Local Incident Commander API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

INBOX_DIR = "inbox"
SYSLOG_PORT = 5514
_udp_server = None


@app.get("/health")
async def health():
    return {"status": "ok", "service": "local-incident-commander"}


@app.post("/webhook")
async def webhook(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = await request.body()
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return JSONResponse({"error": "invalid JSON"}, status_code=400)

    if not isinstance(body, dict):
        body = {"payload": body}

    if "service" not in body:
        body["service"] = "webhook"
    if "timestamp" not in body:
        body["timestamp"] = datetime.now(timezone.utc).isoformat()
    if "event_type" not in body:
        body["event_type"] = body.get("type", "webhook")

    filename = f"webhook_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}.json"
    path = Path(INBOX_DIR) / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(body, f, default=str)

    return JSONResponse({"status": "accepted", "file": filename}, status_code=202)


@app.post("/hec")
async def splunk_hec(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON"}, status_code=400)

    events = body if isinstance(body, list) else [body]
    accepted = []
    for event in events:
        data = event.get("event", event)
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = {"message": data}

        if not isinstance(data, dict):
            data = {"message": str(data)}

        lic_event = {
            "service": data.get("service", event.get("host", "splunk")),
            "event_type": data.get("event_type", "alert"),
            "severity": data.get("severity", data.get("severity", "Medium")),
            "timestamp": data.get("timestamp", event.get("time", datetime.now(timezone.utc).isoformat())),
            "payload": data.get("payload", data),
            "_source": f"splunk_hec:{event.get('host', 'unknown')}",
        }

        filename = f"splunk_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}.json"
        path = Path(INBOX_DIR) / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(lic_event, f, default=str)
        accepted.append(filename)

    return JSONResponse({"status": "accepted", "files": accepted}, status_code=202)


def _syslog_listener(port: int = 5514):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("0.0.0.0", port))
    except OSError:
        port = 15514
        sock.bind(("0.0.0.0", port))

    sock.settimeout(1.0)
    global SYSLOG_PORT
    SYSLOG_PORT = port

    while True:
        try:
            data, addr = sock.recvfrom(65535)
            message = data.decode("utf-8", errors="replace").strip()
            event = _parse_syslog_message(message, addr)
            if event:
                filename = f"syslog_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}.json"
                path = Path(INBOX_DIR) / filename
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w") as f:
                    json.dump(event, f, default=str)
        except socket.timeout:
            continue
        except Exception:
            continue


def _parse_syslog_message(message: str, addr) -> dict:
    event = {
        "service": "syslog",
        "event_type": "log",
        "severity": "info",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": {"raw": message[:1000]},
        "_source": f"syslog:{addr[0]}",
    }

    for line in message.splitlines():
        line = line.strip()
        if "service=" in line.lower() or "service:" in line.lower():
            for sep in ("=", ":"):
                parts = line.lower().split(f"service{sep}")
                if len(parts) > 1:
                    svc = parts[1].split()[0].strip(",;\"'")
                    event["service"] = svc
                    break

        if "deploy" in line.lower():
            event["event_type"] = "deploy"
        elif "alert" in line.lower() or "critical" in line.lower() or "error" in line.lower():
            event["event_type"] = "alert"
            if "critical" in line.lower():
                event["severity"] = "critical"
            elif "error" in line.lower():
                event["severity"] = "high"

        for metric in ("latency", "cpu", "memory", "disk", "error_rate", "db_connections"):
            for sep in ("=", ":"):
                if f"{metric}{sep}" in line.lower():
                    try:
                        val_str = line.lower().split(f"{metric}{sep}")[1].split()[0]
                        val_str = val_str.strip(",;\"'ms%")
                        event["payload"][metric] = float(val_str) if "." in val_str else int(val_str)
                    except (ValueError, IndexError):
                        pass

    return event


def _mount_dashboard(app: FastAPI):
    dashboard_dir = Path(__file__).resolve().parent.parent / "dashboard" / "dist"
    if dashboard_dir.exists() and (dashboard_dir / "index.html").exists():
        app.mount("/", StaticFiles(directory=str(dashboard_dir), html=True), name="dashboard")
        print(f"  Dashboard UI: serving static files from {dashboard_dir}")
    else:
        print(f"  Dashboard UI: build not found at {dashboard_dir} (run 'npm run build' in dashboard/)")


def run_api_server(host: str = "0.0.0.0", http_port: int = 8080, syslog_port: int = 5514):
    import uvicorn

    t = threading.Thread(target=_syslog_listener, args=(syslog_port,), daemon=True)
    t.start()

    _mount_dashboard(app)

    print(f"Syslog listener started on UDP port {SYSLOG_PORT}")
    print(f"HTTP API server starting on http://{host}:{http_port}")
    print(f"  POST /webhook - receive JSON events")
    print(f"  POST /hec - Splunk HEC compatible")
    print(f"  GET  /health - health check")
    print(f"  GET  /api/incidents - list incidents")
    print(f"  GET  /api/reports - list reports")
    print(f"  GET  /api/triages - list triages")
    print(f"  GET  /api/costs - cost tracking data")
    print(f"  GET  /api/health/system - system health")
    print(f"  GET  /api/events - inbox events")
    print(f"  GET  /api/stats - aggregate statistics")
    print(f"  GET  / - dashboard UI")

    uvicorn.run(app, host=host, port=http_port, log_level="warning")


if __name__ == "__main__":
    run_api_server()
