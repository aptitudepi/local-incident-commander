from typing import Dict, Optional
from src.llm_brief import call_llm


def triage(incident: Dict) -> Dict:
    severity = incident.get("severity", "Medium")
    service = incident.get("service", "unknown")
    events = incident.get("correlated_events", incident.get("events", []))

    prompt = _build_triage_prompt(incident)

    try:
        response = call_llm(prompt, max_tokens=500)
        fix_command = _extract_fix_command(response, service)
        reasoning = response
    except (ConnectionError, TimeoutError, ImportError):
        fix_command = _fallback_fix_command(incident)
        reasoning = "LLM unavailable. Using deterministic fallback."

    result = {
        "incident_id": incident.get("incident_id"),
        "service": service,
        "severity": severity,
        "llm_reasoning": reasoning,
        "fix_command": fix_command,
        "escalated": _should_escalate(incident, fix_command),
        "escalation_reason": "",
    }

    if result["escalated"]:
        result["escalation_reason"] = _escalation_reason(incident, fix_command)

    return result


def _build_triage_prompt(incident: Dict) -> str:
    events_summary = []
    for e in incident.get("correlated_events", incident.get("events", [])):
        events_summary.append(f"- [{e.get('event_type', 'log')}] {e.get('summary', '')}")

    return f"""You are an SRE triage engineer. Given the following incident summary, determine the root cause and recommend an exact fix command.

Incident: {incident.get('incident_id')}
Service: {incident.get('service')}
Severity: {incident.get('severity')}
Events:
{chr(10).join(events_summary)}

Respond with:
1. Root cause (1-2 sentences)
2. Exact fix command to resolve (e.g., 'docker restart payment-01', 'kubectl rollout undo deployment/checkout')
3. Verification command (how to confirm the fix worked)

Fix command must use: docker, kubectl, systemctl, service, or curl."""


def _extract_fix_command(response: str, service: str) -> str:
    for line in response.splitlines():
        line = line.strip()
        if line.startswith("docker ") or line.startswith("kubectl ") or line.startswith("systemctl "):
            return line
        if "restart" in line.lower() and service.lower() in line.lower():
            return f"docker restart {service}-01"
    return _fallback_fix_command({"service": service})


def _fallback_fix_command(incident: Dict) -> str:
    service = incident.get("service", "unknown")
    events = incident.get("events", [])
    has_deploy = incident.get("has_deploy", False)
    payloads = [e.get("payload", {}) for e in events if isinstance(e.get("payload"), dict)]
    has_security = incident.get("has_security", False)

    if has_security:
        return f"docker stop {service}-01 && iptables -A INPUT -s 0.0.0.0/0 -j DROP"
    if has_deploy:
        return f"kubectl rollout undo deployment/{service}"
    if any(p.get("db_connections", 0) > 80 for p in payloads):
        return f"docker restart {service}-01"
    if any(p.get("cpu_percent", 0) > 80 for p in payloads):
        return f"docker restart {service}-01"
    if any(p.get("latency_ms", 0) > 300 for p in payloads):
        return f"docker restart {service}-01"
    return f"docker restart {service}-01"


def _should_escalate(incident: Dict, fix_command: str) -> bool:
    if incident.get("has_security"):
        return True
    if incident.get("severity") == "Critical" and "restart" in fix_command and "rollback" not in fix_command:
        return True
    return False


def _escalation_reason(incident: Dict, fix_command: str) -> str:
    if incident.get("has_security"):
        return "Security incident requires human investigation before containment."
    if incident.get("severity") == "Critical":
        return f"Critical incident. Recommended fix '{fix_command}' requires human approval at autonomy level {incident.get('autonomy_level', 3)}."
    return "Manual intervention required."
