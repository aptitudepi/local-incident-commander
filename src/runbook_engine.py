import yaml
from typing import Dict, List, Optional
from pathlib import Path


RUNBOOKS_DIR = "runbooks"


def load_runbooks() -> List[Dict]:
    runbooks = []
    path = Path(RUNBOOKS_DIR)
    if not path.exists():
        return runbooks
    for f in sorted(path.iterdir()):
        if f.suffix in (".yaml", ".yml"):
            try:
                with open(f) as fh:
                    rb = yaml.safe_load(fh)
                    if rb and "id" in rb:
                        rb["_source"] = str(f)
                        runbooks.append(rb)
            except yaml.YAMLError:
                pass
    return runbooks


def match_runbook(incident: Dict, runbooks: List[Dict]) -> Optional[Dict]:
    best = None
    best_score = 0
    incident_type = _incident_type(incident)
    incident_service = incident.get("service", "")

    for rb in runbooks:
        score = 0
        rb_type = rb.get("triggers", {}).get("event_types", [])
        rb_services = rb.get("triggers", {}).get("services", [])

        if incident_type in rb_type:
            score += 10
        if incident_service in rb_services:
            score += 5
        if not rb_services:
            score += 2

        sev = incident.get("severity", "")
        rb_sev = rb.get("triggers", {}).get("severities", [])
        if sev in rb_sev:
            score += 3

        if score > best_score:
            best_score = score
            best = rb

    return best if best_score >= 5 else None


def _incident_type(incident: Dict) -> str:
    if incident.get("has_security"):
        return "security"
    if incident.get("has_deploy"):
        return "deploy"
    if any("db_connections" in str(e.get("payload", {})) for e in incident.get("events", [])):
        return "database"
    if any("latency_ms" in str(e.get("payload", {})) for e in incident.get("events", [])):
        return "latency"
    if any("cpu_percent" in str(e.get("payload", {})) for e in incident.get("events", [])):
        return "cpu"
    return "generic"


def generate_runbook_from_fix(incident: Dict, fix_command: str, human_notes: str = "") -> Dict:
    incident_type = _incident_type(incident)
    service = incident.get("service", "unknown")

    runbook = {
        "id": f"auto-{incident.get('incident_id', 'unknown').lower()}",
        "name": f"Auto-generated: {incident_type} fix for {service}",
        "description": f"Auto-generated from human resolution of {incident.get('incident_id', 'unknown')}",
        "auto_generated": True,
        "source_incident": incident.get("incident_id"),
        "triggers": {
            "event_types": [incident_type],
            "services": [service],
            "severities": [incident.get("severity", "Medium")],
        },
        "steps": [
            {
                "action": fix_command,
                "description": human_notes or f"Auto-generated fix for {incident_type} on {service}",
                "safeguards": {
                    "allowed_commands": [fix_command.split()[0]],
                    "requires_approval": incident.get("requires_human_approval", True),
                }
            }
        ],
        "rollback": {
            "description": f"Monitor {service} after fix, revert if health check fails",
        }
    }
    return runbook


def save_runbook(runbook: Dict):
    rid = runbook.get("id", "unknown")
    path = Path(RUNBOOKS_DIR) / f"{rid}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(runbook, f, default_flow_style=False, sort_keys=False)
