import json
import os
import re
from typing import Dict, List, Optional
from pathlib import Path


INCIDENTS_DIR = Path("reports/incidents")
RUNBOOKS_DIR = Path("runbooks")
LEARNED_RULES_FILE = Path("learned_rules.yaml")

PATTERN_THRESHOLD = 2
ACTION_WEIGHTS = {
    "restart": 2,
    "clear-cache": 2,
    "drain": 1,
    "rollback": 3,
    "isolate": 3,
    "scale": 2,
    "deploy": -5,
}


def _load_incidents() -> List[Dict]:
    if not INCIDENTS_DIR.exists():
        return []
    incidents = []
    for f in sorted(INCIDENTS_DIR.glob("*.json"), key=os.path.getmtime):
        try:
            with open(f) as fh:
                incidents.append(json.load(fh))
        except (json.JSONDecodeError, OSError):
            continue
    return incidents


def _load_learned_rules() -> Dict:
    if LEARNED_RULES_FILE.exists():
        import yaml
        with open(LEARNED_RULES_FILE) as f:
            return yaml.safe_load(f) or {}
    return {"rules": [], "suggestions": []}


def _save_learned_rules(data: Dict):
    import yaml
    LEARNED_RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LEARNED_RULES_FILE, "w") as f:
        yaml.dump(data, f, default_flow_style=False)


def _pattern_key(incident: Dict) -> str:
    service = incident.get("service", "unknown")
    events = incident.get("correlated_events", incident.get("events", []))
    event_types = sorted(set(
        e.get("event_type", e.get("type", "unknown"))
        for e in (events or [])
    ))
    return f"{service}:{','.join(event_types)}"


def _suggest_action(incident: Dict) -> str:
    severity = incident.get("severity", "Medium")
    service = incident.get("service", "")
    has_security = incident.get("has_security", False)
    has_deploy = incident.get("has_deploy", False)

    if has_security:
        return "isolate"
    if has_deploy:
        return "rollback"
    if severity == "Critical":
        return "restart"
    return "restart"


def detect_patterns() -> List[Dict]:
    incidents = _load_incidents()
    patterns: Dict[str, List[Dict]] = {}

    for inc in incidents:
        key = _pattern_key(inc)
        if key not in patterns:
            patterns[key] = []
        patterns[key].append(inc)

    suggestions = []
    for key, group in patterns.items():
        if len(group) >= PATTERN_THRESHOLD:
            latest = group[-1]
            action = _suggest_action(latest)
            severity = latest.get("severity", "Medium")
            suggestions.append({
                "pattern_key": key,
                "service": latest.get("service", "unknown"),
                "event_types": key.split(":", 1)[1] if ":" in key else "",
                "occurrences": len(group),
                "action": action,
                "profile": "hardened",
                "autonomy_level": 2,
                "score_threshold": 0,
                "suggested_rule": {
                    "if": f"service is '{latest.get('service','')}' and severity is '{severity}'",
                    "then": f"recommend action '{action}'",
                    "require_human_approval": True,
                    "policy_id": f"learned-{key[:8].lower()}" if len(key) > 8 else f"learned-{key.lower()}",
                },
                "last_incident_id": latest.get("incident_id", latest.get("id", "unknown")),
            })
    return suggestions


def get_learned_rules() -> Dict:
    data = _load_learned_rules()
    suggestions = detect_patterns()
    existing_keys = {r.get("pattern_key", "") for r in data.get("rules", [])}
    new_suggestions = [s for s in suggestions if s["pattern_key"] not in existing_keys]
    data["suggestions"] = new_suggestions
    _save_learned_rules(data)
    return data


def adopt_rule(pattern_key: str) -> bool:
    data = _load_learned_rules()
    for s in data.get("suggestions", []):
        if s["pattern_key"] == pattern_key:
            rule = {
                "pattern_key": pattern_key,
                "service": s["service"],
                "action": s["action"],
                "profile": s["profile"],
                "autonomy_level": s["autonomy_level"],
                "score_threshold": s["score_threshold"],
                "policy_id": s["suggested_rule"]["policy_id"],
                "status": "active",
            }
            data.setdefault("rules", []).append(rule)
            data["suggestions"] = [x for x in data["suggestions"] if x["pattern_key"] != pattern_key]
            _save_learned_rules(data)
            _write_runbook_rule(rule)
            return True
    return False


def reject_suggestion(pattern_key: str) -> bool:
    data = _load_learned_rules()
    data["suggestions"] = [x for x in data.get("suggestions", []) if x["pattern_key"] != pattern_key]
    _save_learned_rules(data)
    return True


def _write_runbook_rule(rule: Dict):
    name = f"learned-{rule['pattern_key'][:20].lower().replace(':', '-')}"
    path = RUNBOOKS_DIR / f"{name}.yaml"
    RUNBOOKS_DIR.mkdir(parents=True, exist_ok=True)

    content = f"""# Auto-learned rule — generated by Local Incident Commander
# Pattern: {rule['pattern_key']}
# Policy ID: {rule['policy_id']}
#
# To override: edit this file and set `override: true`

name: {name}
service: {rule['service']}
action: {rule['action']}
policy_profile: {rule['profile']}
autonomy_level: {rule['autonomy_level']}
score_threshold: {rule['score_threshold']}
policy_id: {rule['policy_id']}
status: {rule['status']}
override: false
"""
    with open(path, "w") as f:
        f.write(content)


def reset_learned_rules():
    _save_learned_rules({"rules": [], "suggestions": []})
