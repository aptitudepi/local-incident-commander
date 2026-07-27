from typing import Dict
from src.ticketing import create_ticket


def escalate(incident: Dict, triage_result: Dict, remediation_result: Dict = None) -> Dict:
    if remediation_result is None:
        remediation_result = {"status": "not_attempted"}

    ticket = create_ticket(incident, triage_result, remediation_result)

    escalation = {
        "incident_id": incident.get("incident_id"),
        "ticket_id": ticket.get("ticket_id"),
        "escalated_at": ticket.get("created_at"),
        "reason": triage_result.get("escalation_reason", "Manual escalation required"),
        "status": "escalated",
        "ticket": ticket,
    }

    _update_incident_escalation_status(incident.get("incident_id"), escalation)
    return escalation


def _update_incident_escalation_status(incident_id: str, escalation: Dict):
    import json
    from pathlib import Path

    path = Path("reports/incidents") / f"{incident_id}.json"
    if path.exists():
        with open(path) as f:
            report = json.load(f)
        report["escalated"] = True
        report["ticket_id"] = escalation["ticket_id"]
        report["status"] = "escalated"
        with open(path, "w") as f:
            json.dump(report, f, indent=2, default=str)
