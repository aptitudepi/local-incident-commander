import json
import os
import time
from typing import Dict, List
from pathlib import Path
from datetime import datetime, timezone
import subprocess


HEALTH_FILE = "reports/metrics/health.json"


def collect_health() -> Dict:
    health = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pipeline": {
            "watcher": _check_watcher(),
            "correlator": _check_correlator(),
            "llm_endpoint": _check_llm_endpoint(),
            "last_event_time": _last_event_time(),
        },
        "model": {
            "vllm_running": _check_vllm(),
            "model_loaded": _check_vllm(),
            "fallback_available": _check_transformers(),
        },
        "queue": {
            "inbox_count": _count_inbox(),
            "unprocessed_events": _count_inbox(),
        },
        "performance": {
            "fix_success_rate": _fix_success_rate(),
            "total_fixes_attempted": _count_fixes("executed") + _count_fixes("verified"),
            "total_fixes_succeeded": _count_fixes("verified"),
            "incidents_resolved_today": _count_incidents_today(),
        },
        "system": {
            "uptime": _system_uptime(),
            "disk_usage": _disk_usage(),
            "memory_available": _memory_available(),
        },
    }
    _save_health(health)
    return health


def _check_watcher() -> str:
    inbox = Path("inbox")
    if inbox.exists() and any(inbox.iterdir()):
        return "active"
    return "idle"


def _check_correlator() -> str:
    incidents = Path("reports/incidents")
    if incidents.exists() and any(incidents.iterdir()):
        return "active"
    return "idle"


def _check_llm_endpoint() -> str:
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "http://localhost:8000/v1/models"],
            capture_output=True, text=True, timeout=5,
        )
        return "up" if r.stdout.strip() == "200" else "down"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "unknown"


def _check_vllm() -> bool:
    try:
        r = subprocess.run(
            ["pgrep", "-f", "vllm"],
            capture_output=True, text=True, timeout=5,
        )
        return r.returncode == 0
    except FileNotFoundError:
        return False


def _check_transformers() -> bool:
    try:
        from src.local_model import TRANSFORMERS_AVAILABLE
        return TRANSFORMERS_AVAILABLE
    except ImportError:
        return False


def _last_event_time() -> str:
    log = Path("reports/events/events.jsonl")
    if log.exists() and log.stat().st_size > 0:
        with open(log) as f:
            for line in f:
                pass
            try:
                event = json.loads(line)
                return event.get("timestamp", "unknown")
            except json.JSONDecodeError:
                return "unknown"
    return "never"


def _count_inbox() -> int:
    inbox = Path("inbox")
    if inbox.exists():
        return len([f for f in inbox.iterdir() if f.is_file() and not f.name.startswith(".")])
    return 0


def _fix_success_rate() -> float:
    log = Path("reports/metrics/remediation_log.jsonl")
    if log.exists() and log.stat().st_size > 0:
        total = 0
        success = 0
        with open(log) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    total += 1
                    if entry.get("status") == "verified":
                        success += 1
                except json.JSONDecodeError:
                    pass
        return round(success / total * 100, 1) if total > 0 else 0.0
    return 0.0


def _count_fixes(status: str) -> int:
    log = Path("reports/metrics/remediation_log.jsonl")
    if log.exists() and log.stat().st_size > 0:
        count = 0
        with open(log) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("status") == status:
                        count += 1
                except json.JSONDecodeError:
                    pass
        return count
    return 0


def _count_incidents_today() -> int:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    count = 0
    incidents = Path("reports/incidents")
    if incidents.exists():
        for f in incidents.iterdir():
            if f.suffix == ".json":
                try:
                    with open(f) as fh:
                        inc = json.load(fh)
                    if inc.get("timestamp", "").startswith(today):
                        count += 1
                except (json.JSONDecodeError, OSError):
                    pass
    return count


def _system_uptime() -> float:
    try:
        with open("/proc/uptime") as f:
            return float(f.read().split()[0])
    except (FileNotFoundError, OSError):
        return 0.0


def _disk_usage() -> Dict:
    import shutil
    usage = shutil.disk_usage(".")
    return {
        "total_gb": round(usage.total / (1024**3), 1),
        "used_gb": round(usage.used / (1024**3), 1),
        "free_gb": round(usage.free / (1024**3), 1),
        "percent": round(usage.used / usage.total * 100, 1),
    }


def _memory_available() -> Dict:
    try:
        with open("/proc/meminfo") as f:
            data = {}
            for line in f:
                parts = line.split()
                if parts[0].rstrip(":") in ("MemTotal", "MemAvailable", "MemFree"):
                    data[parts[0].rstrip(":")] = int(parts[1])
        return {
            "total_mb": round(data.get("MemTotal", 0) / 1024, 1),
            "available_mb": round(data.get("MemAvailable", 0) / 1024, 1),
            "free_mb": round(data.get("MemFree", 0) / 1024, 1),
        }
    except (FileNotFoundError, OSError):
        return {"error": "unable to read memory info"}


def _save_health(health: Dict):
    path = Path(HEALTH_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(health, f, indent=2)
