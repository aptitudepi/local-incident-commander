import json
import subprocess
import uuid
import yaml
from datetime import datetime, timezone
from typing import List, Dict, Optional
from pathlib import Path


INCIDENTS_DIR = "reports/incidents"


def _parse_ts(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


def load_topology(topology_path: str = "config.yaml") -> Dict:
    try:
        with open(topology_path) as f:
            cfg = yaml.safe_load(f) or {}
        return cfg.get("topology", {})
    except (FileNotFoundError, yaml.YAMLError):
        return {}


def _discover_docker_topology() -> Dict:
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=5
        )
        containers = [n.strip() for n in result.stdout.splitlines() if n.strip()]
        discovered = {}
        for name in containers:
            discovered[name] = {"depends_on": [], "port": None}
        return discovered
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return {}


def get_topology() -> Dict:
    auto = _discover_docker_topology()
    manual = load_topology()
    merged = dict(auto)
    for svc, cfg in manual.items():
        if svc in merged:
            merged[svc].update(cfg)
        else:
            merged[svc] = cfg
    return merged


def correlate(events: List[Dict], time_window_minutes: int = 15) -> List[Dict]:
    topology = get_topology()
    by_service: Dict[str, List[Dict]] = {}
    for ev in events:
        svc = ev.get("service", "unknown")
        by_service.setdefault(svc, []).append(ev)

    incidents = []
    for svc, evts in by_service.items():
        evts.sort(key=lambda e: _parse_ts(e.get("timestamp", "")))
        _correlate_service(svc, evts, time_window_minutes, topology, incidents)

    return incidents


def _correlate_service(
    svc: str, evts: List[Dict], window: int, topology: Dict, incidents: List
):
    i = 0
    while i < len(evts):
        window_start = _parse_ts(evts[i].get("timestamp", ""))
        group = []
        j = i
        while j < len(evts):
            ts = _parse_ts(evts[j].get("timestamp", ""))
            if (ts - window_start).total_seconds() / 60 <= window:
                group.append(evts[j])
                j += 1
            else:
                break

        has_deploy = any(e.get("event_type") == "deploy" for e in group)
        has_alert = any(e.get("event_type") == "alert" for e in group)
        has_security = any(
            "brute" in str(e.get("payload", {})).lower()
            or "ssh" in str(e.get("payload", {})).lower()
            for e in group
        )

        if has_deploy or has_alert or has_security:
            deps = topology.get(svc, {}).get("depends_on", [])
            incident = {
                "incident_id": f"INC-{uuid.uuid4().hex[:8].upper()}",
                "service": svc,
                "events": group,
                "event_count": len(group),
                "time_range": {
                    "start": group[0].get("timestamp"),
                    "end": group[-1].get("timestamp"),
                },
                "has_deploy": has_deploy,
                "has_alert": has_alert,
                "has_security": has_security,
                "dependencies": deps,
                "topology": topology.get(svc, {}),
            }
            incidents.append(incident)
        i = j


def correlate_from_directory(input_dir: str = "inbox") -> List[Dict]:
    from src.watcher import scan_directory
    events = scan_directory(input_dir)
    return correlate(events)


def save_incident(incident: Dict):
    path = Path(INCIDENTS_DIR) / f"{incident['incident_id']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(incident, f, indent=2, default=str)


def load_incident(incident_id: str) -> Optional[Dict]:
    path = Path(INCIDENTS_DIR) / f"{incident_id}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def list_incidents() -> List[Dict]:
    incidents = []
    path = Path(INCIDENTS_DIR)
    if path.exists():
        for f in sorted(path.iterdir()):
            if f.suffix == ".json":
                with open(f) as fh:
                    incidents.append(json.load(fh))
    return incidents
