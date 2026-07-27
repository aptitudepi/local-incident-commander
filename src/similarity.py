import json
from typing import List, Dict
from pathlib import Path


INCIDENTS_DIR = "reports/incidents"


def find_similar(incident: Dict, top_k: int = 3) -> List[Dict]:
    past_incidents = _load_past_incidents()
    if not past_incidents:
        return []

    current_service = incident.get("service", "")
    current_severity = incident.get("severity", "")
    current_type = _incident_signature(incident)

    scored = []
    for past in past_incidents:
        pid = past.get("incident_id", "")
        if pid == incident.get("incident_id"):
            continue
        score = 0
        if past.get("service") == current_service:
            score += 40
        if past.get("severity") == current_severity:
            score += 20
        if _incident_signature(past) == current_type:
            score += 30
        if past.get("recommended_action") == incident.get("recommended_action"):
            score += 10
        scored.append((score, past))

    scored.sort(key=lambda x: -x[0])
    return [
        {
            "incident_id": past["incident_id"],
            "service": past.get("service"),
            "severity": past.get("severity"),
            "similarity_score": score,
            "previous_action": past.get("recommended_action"),
            "previous_resolution": past.get("probable_root_cause", ""),
        }
        for score, past in scored[:top_k]
        if score > 20
    ]


def _load_past_incidents() -> List[Dict]:
    incidents = []
    path = Path(INCIDENTS_DIR)
    if path.exists():
        for f in sorted(path.iterdir()):
            if f.suffix == ".json":
                try:
                    with open(f) as fh:
                        incidents.append(json.load(fh))
                except json.JSONDecodeError:
                    pass
    return incidents


def _incident_signature(incident: Dict) -> str:
    events = incident.get("events", incident.get("correlated_events", []))
    event_types = sorted(set(
        e.get("event_type", "") for e in events
        if isinstance(e, dict)
    ))
    return "+".join(event_types)
