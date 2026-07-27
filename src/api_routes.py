import json
import os
import glob
import shutil
import subprocess
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api")

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"
INBOX_DIR = BASE_DIR / "inbox"


def _load_json_files(pattern: str) -> list:
    files = sorted(glob.glob(str(REPORTS_DIR / pattern)), key=os.path.getmtime, reverse=True)
    results = []
    for f in files:
        try:
            with open(f) as fh:
                results.append(json.load(fh))
        except (json.JSONDecodeError, OSError):
            pass
    return results


@router.get("/incidents")
async def get_incidents():
    files = sorted(glob.glob(str(REPORTS_DIR / "incidents" / "*.json")), key=os.path.getmtime, reverse=True)
    results = []
    for f in files:
        try:
            with open(f) as fh:
                results.append(json.load(fh))
        except (json.JSONDecodeError, OSError):
            pass
    return results


@router.get("/reports")
async def get_reports():
    return _load_json_files("report_*.json")


@router.get("/triages")
async def get_triages():
    return _load_json_files("triage_*.json")


@router.get("/costs")
async def get_costs():
    cost_file = REPORTS_DIR / "metrics" / "costs.json"
    if cost_file.exists():
        try:
            with open(cost_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


@router.get("/health/system")
async def get_system_health():
    vllm_ok = False
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:8000/v1/models"],
                          capture_output=True, text=True, timeout=3)
        vllm_ok = r.stdout.strip() == "200"
    except Exception:
        pass

    model_loaded = os.path.exists("/home/dell/repos/Qwen3.6-35B-A3B-NVFP4")
    docker_ok = shutil.which("docker") is not None
    openclaw_ok = shutil.which("openclaw") is not None

    inbox_count = len(glob.glob(str(INBOX_DIR / "*")))

    return {
        "vllm": {"running": vllm_ok, "port": 8000},
        "model": {"loaded": model_loaded, "path": "/home/dell/repos/Qwen3.6-35B-A3B-NVFP4"},
        "openclaw": {"available": openclaw_ok},
        "docker": {"available": docker_ok},
        "api": {"status": "ok", "port": 8081},
        "queue": {"inbox_count": inbox_count},
    }


@router.get("/events")
async def get_events():
    files = sorted(glob.glob(str(INBOX_DIR / "*.json")), key=os.path.getmtime, reverse=True)[:50]
    events = []
    for f in files:
        try:
            with open(f) as fh:
                events.append(json.load(fh))
        except (json.JSONDecodeError, OSError):
            pass
    return events


@router.get("/stats")
async def get_stats():
    incidents = _load_json_files("incidents/*.json")
    reports = _load_json_files("report_*.json")
    triages = _load_json_files("triage_*.json")

    total = len(incidents)
    critical = sum(1 for i in incidents if i.get("severity", "").lower() == "critical")
    high = sum(1 for i in incidents if i.get("severity", "").lower() == "high")

    cost_file = REPORTS_DIR / "metrics" / "costs.json"
    total_saved = 0
    if cost_file.exists():
        try:
            with open(cost_file) as f:
                costs = json.load(f)
                total_saved = costs.get("total_saved", 0)
        except (json.JSONDecodeError, OSError):
            pass

    inbox_files = len(glob.glob(str(INBOX_DIR / "*.json")))
    report_files = len(glob.glob(str(REPORTS_DIR / "*.json")))

    return {
        "total_incidents": total,
        "critical_count": critical,
        "high_count": high,
        "total_saved": total_saved,
        "inbox_count": inbox_files,
        "report_count": report_files,
        "triage_count": len(triages),
        "report_count_detail": len(reports),
    }
