import json
import os
import requests
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime, timezone


TICKETS_DIR = "reports/tickets"
WEBHOOK_URL = None


def configure_webhook(url: Optional[str] = None):
    global WEBHOOK_URL
    WEBHOOK_URL = url


def create_ticket(incident: Dict, triage_result: Dict, remediation_result: Dict) -> Dict:
    ticket_id = f"TKT-{incident.get('incident_id', 'UNKNOWN').split('-')[1] if '-' in incident.get('incident_id', '') else '0000'}"

    ticket = {
        "ticket_id": ticket_id,
        "incident_id": incident.get("incident_id"),
        "title": f"[{incident.get('severity', 'INFO')}] {incident.get('service', 'unknown')} - {incident.get('probable_root_cause', '')[:100]}",
        "description": _build_description(incident, triage_result, remediation_result),
        "priority": _map_severity_to_priority(incident.get("severity", "Medium")),
        "status": "open",
        "assignee": "sre-team",
        "labels": ["lic", "auto-escalated", incident.get("severity", "info").lower()],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evidence": incident.get("evidence", []),
        "recommended_action": incident.get("recommended_action"),
        "fix_attempted": remediation_result.get("status") if remediation_result else None,
        "source": "Local Incident Commander",
    }

    _save_ticket(ticket)

    if WEBHOOK_URL:
        _send_webhook(ticket)

    return ticket


def _build_description(incident: Dict, triage_result: Dict, remediation_result: Dict) -> str:
    lines = [
        f"## Incident: {incident.get('incident_id')}",
        f"**Service:** {incident.get('service')}",
        f"**Severity:** {incident.get('severity')}",
        f"**Root Cause:** {incident.get('probable_root_cause', 'Not determined')}",
        f"",
        f"### Events ({incident.get('event_count', 0)})",
    ]
    for e in incident.get("correlated_events", []):
        lines.append(f"- [{e.get('event_type')}] {e.get('summary', '')}")
    lines.append("")
    lines.append(f"### Recommended Action")
    lines.append(f"{incident.get('recommended_action', 'None')}")
    if triage_result:
        lines.append("")
        lines.append(f"### Auto-Triage")
        lines.append(f"**Fix Command:** {triage_result.get('fix_command', 'None')}")
        lines.append(f"**Escalated:** {triage_result.get('escalated', False)}")
        lines.append(f"**Reason:** {triage_result.get('escalation_reason', 'N/A')}")
    if remediation_result:
        lines.append("")
        lines.append(f"### Auto-Remediation")
        lines.append(f"**Status:** {remediation_result.get('status', 'N/A')}")
        lines.append(f"**Verification:** {remediation_result.get('verification', 'N/A')}")
    return "\n".join(lines)


def _map_severity_to_priority(severity: str) -> str:
    mapping = {
        "Critical": "P1",
        "High": "P2",
        "Medium": "P3",
        "Low": "P4",
    }
    return mapping.get(severity, "P3")


def _save_ticket(ticket: Dict):
    path = Path(TICKETS_DIR) / f"{ticket['ticket_id']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(ticket, f, indent=2)


def _send_webhook(ticket: Dict):
    if not WEBHOOK_URL:
        return
    try:
        requests.post(
            WEBHOOK_URL,
            json=ticket,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
    except requests.RequestException:
        pass


def load_ticket(ticket_id: str) -> Optional[Dict]:
    path = Path(TICKETS_DIR) / f"{ticket_id}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def list_tickets() -> list:
    tickets = []
    path = Path(TICKETS_DIR)
    if path.exists():
        for f in sorted(path.iterdir()):
            if f.suffix == ".json":
                with open(f) as fh:
                    tickets.append(json.load(fh))
    return tickets
