import json
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timezone
from pathlib import Path
from src.scoring import compute_score


def build_incident_report(incident: Dict, severity: str) -> Dict:
    events = incident.get("events", [])
    service = incident.get("service", "unknown")
    incident_id = incident.get("incident_id", f"INC-{uuid.uuid4().hex[:8].upper()}")

    root_cause = _determine_root_cause(events, service)
    action = _recommend_action(events, root_cause, service)
    evidence = _build_evidence(events)

    score = compute_score(incident, "restart", "hardened")

    report = {
        "incident_id": incident_id,
        "service": service,
        "severity": severity,
        "status": "open",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlated_events": [
            {
                "event_type": e.get("event_type"),
                "source": e.get("_source", ""),
                "timestamp": e.get("timestamp"),
                "summary": _event_summary(e),
            }
            for e in events
        ],
        "event_count": len(events),
        "probable_root_cause": root_cause,
        "evidence": evidence,
        "recommended_action": action,
        "auto_fix_command": "",
        "manual_fix_command": action,
        "score": score,
        "auto_remediate": score >= 0,
        "remediation_status": "pending_triage",
        "requires_human_approval": severity in ("Critical", "High"),
        "autonomy_level": _autonomy_level(severity, incident.get("has_security", False)),
        "escalated": False,
        "ticket_id": None,
    }
    return report


def _determine_root_cause(events: List[Dict], service: str) -> str:
    has_deploy = any(e.get("event_type") == "deploy" for e in events)
    has_security = any(
        "brute" in str(e.get("payload", {})).lower()
        or "ssh" in str(e.get("payload", {})).lower()
        for e in events
    )
    latency_events = [e for e in events if e.get("payload", {}).get("latency_ms", 0) > 0]
    db_events = [e for e in events if e.get("payload", {}).get("db_connections", 0) > 0]
    cpu_events = [e for e in events if e.get("payload", {}).get("cpu_percent", 0) > 0]

    if has_security:
        return f"Suspicious access pattern detected on {service}. Possible brute force attack."

    if has_deploy and (latency_events or db_events or cpu_events):
        version = ""
        for e in events:
            p = e.get("payload", {})
            if isinstance(p, dict) and p.get("version"):
                version = f" v{p['version']}"
                break
        return f"Recent deployment{version} to {service} likely introduced a regression causing resource exhaustion."

    if latency_events and db_events:
        return f"Database connection pool exhaustion on {service} causing cascading latency increases."

    if cpu_events:
        return f"CPU saturation on {service} likely due to traffic spike or inefficient query."

    if latency_events:
        return f"Increased latency on {service}. Possible upstream dependency degradation."

    return f"No obvious root cause identified for {service} anomalies."


def _recommend_action(events: List[Dict], root_cause: str, service: str) -> str:
    has_deploy = any(e.get("event_type") == "deploy" for e in events)
    has_security = any(
        "brute" in str(e.get("payload", {})).lower()
        or "ssh" in str(e.get("payload", {})).lower()
        for e in events
    )
    payloads = [e.get("payload", {}) for e in events if isinstance(e.get("payload"), dict)]

    if has_security:
        return f"Isolate {service} container, block originating IPs, investigate auth logs."

    if has_deploy:
        version = ""
        for p in payloads:
            if p.get("version"):
                version = f" to v{p['version']}"
                break
        return f"Roll back deployment{version} on {service} and monitor."

    if any(p.get("db_connections", 0) > 80 for p in payloads):
        return f"Scale database connection pool for {service}."

    if any(p.get("cpu_percent", 0) > 80 for p in payloads):
        return f"Restart {service} to clear CPU spike and investigate root cause."

    if any(p.get("latency_ms", 0) > 300 for p in payloads):
        return f"Investigate {service} logs for slow queries or upstream dependency issues."

    return f"Investigate {service} for anomalous behavior."


def _build_evidence(events: List[Dict]) -> List[Dict]:
    evidence = []
    for e in events:
        p = e.get("payload", {})
        if isinstance(p, dict):
            for metric in ("latency_ms", "error_rate", "db_connections", "cpu_percent", "memory_percent", "disk_percent"):
                if metric in p:
                    evidence.append({
                        "metric": metric,
                        "value": p[metric],
                        "source": e.get("_source", ""),
                        "timestamp": e.get("timestamp"),
                    })
    return evidence


def _event_summary(event: Dict) -> str:
    etype = event.get("event_type", "log")
    payload = event.get("payload", {})
    if isinstance(payload, dict):
        parts = [f"{k}={v}" for k, v in payload.items()]
        return f"[{etype}] {' '.join(parts)}"
    return f"[{etype}]"


def _autonomy_level(severity: str, has_security: bool) -> int:
    if has_security:
        return 2
    if severity == "Critical":
        return 3
    if severity == "High":
        return 3
    if severity == "Medium":
        return 2
    return 1


def save_report(report: Dict):
    path = Path("reports/incidents") / f"{report['incident_id']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(report, f, indent=2, default=str)
