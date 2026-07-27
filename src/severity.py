from typing import Dict, List, Optional


def classify_severity(incident: Dict) -> str:
    events = incident.get("events", [])
    has_deploy = incident.get("has_deploy", False)
    payloads = _extract_payloads(events)

    max_latency = max(p.get("latency_ms", 0) for p in payloads)
    max_error_rate = max(p.get("error_rate", 0) for p in payloads)
    max_db_connections = max(p.get("db_connections", 0) for p in payloads)
    max_cpu = max(p.get("cpu_percent", 0) for p in payloads)
    has_security = incident.get("has_security", False)

    if has_security:
        return "Critical"

    if has_deploy:
        if max_latency > 1000 or max_error_rate > 10 or max_db_connections > 90 or max_cpu > 90:
            return "Critical"
        if max_latency > 500 or max_error_rate > 5 or max_db_connections > 80 or max_cpu > 80:
            return "High"
        return "Medium"

    if max_latency > 1000 or max_error_rate > 10 or max_db_connections > 90 or max_cpu > 90:
        return "High"

    if max_latency > 300 or max_error_rate > 3 or max_db_connections > 70:
        return "Medium"

    return "Low"


def _extract_payloads(events: List[Dict]) -> List[Dict]:
    payloads = []
    for ev in events:
        p = ev.get("payload", {})
        if isinstance(p, dict):
            payloads.append(p)
    return payloads


def classify_from_incident_id(incident_id: str) -> Optional[str]:
    from src.correlator import load_incident
    incident = load_incident(incident_id)
    if incident is None:
        return None
    return classify_severity(incident)
