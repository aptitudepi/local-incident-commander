import json
import subprocess
import time
import os
from typing import Dict, Optional
from pathlib import Path
from src.safeguards import validate_command
from src.policy import evaluate as policy_evaluate
from src.runbook_engine import load_runbooks, match_runbook
from src.openclaw_adapter import is_available as openclaw_available, set_exec_policy


REMEDIATION_LOG = "reports/metrics/remediation_log.jsonl"


def execute(incident: Dict, triage_result: Dict, profile: str = "hardened") -> Dict:
    result = {
        "incident_id": incident.get("incident_id"),
        "status": "pending",
        "fix_command": triage_result.get("fix_command", ""),
        "safeguards": [],
        "policy_decision": None,
        "verification": None,
        "error": None,
        "rollback_executed": False,
        "timestamp": time.time(),
    }

    fix_command = triage_result.get("fix_command", "")
    service = incident.get("service", "unknown")
    autonomy_level = incident.get("autonomy_level", 3)

    safeguard_result = validate_command(fix_command, service)
    result["safeguards"] = safeguard_result.get("checks", [])

    if not safeguard_result["allowed"]:
        result["status"] = "blocked_by_safeguards"
        result["error"] = safeguard_result.get("blocked_by", "unknown")
        _log_remediation(result)
        return result

    action_name = fix_command.split()[0]
    policy_decision = policy_evaluate(action_name, service, profile, autonomy_level)
    result["policy_decision"] = policy_decision

    if not policy_decision["allowed"]:
        result["status"] = "blocked_by_policy"
        result["policy_source"] = policy_decision.get("source", "local")
        _log_remediation(result)
        return result

    if openclaw_available():
        result["openclaw_sandbox"] = "available"
        set_exec_policy("cautious" if profile == "hardened" else "yolo")

    try:
        proc = subprocess.run(
            fix_command.split(),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode == 0:
            result["status"] = "executed"
            result["stdout"] = proc.stdout
            health_result = _verify_health(service)
            result["verification"] = health_result
            if health_result.get("healthy"):
                result["status"] = "verified"
            else:
                result["status"] = "fix_applied_but_unhealthy"
                _execute_rollback(incident, fix_command, result)
        else:
            result["status"] = "execution_failed"
            result["error"] = proc.stderr
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = "Fix command timed out after 30s"
    except FileNotFoundError:
        result["status"] = "command_not_found"
        result["error"] = f"Command '{action_name}' not found on system"

    _log_remediation(result)
    return result


def _verify_health(service: str, timeout: float = 10.0) -> Dict:
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={service}", "--format", "{{.Status}}"],
            capture_output=True, text=True, timeout=timeout,
        )
        status = result.stdout.strip()
        if "Up" in status or "healthy" in status:
            return {"healthy": True, "status": status, "checked_at": time.time()}
        return {"healthy": False, "status": status or "not found", "checked_at": time.time()}
    except (FileNotFoundError, subprocess.TimeoutExpired):
        try:
            r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                                f"http://localhost:5001/health"], capture_output=True, text=True, timeout=5)
            healthy = r.stdout.strip() == "200"
            return {"healthy": healthy, "status": f"HTTP {r.stdout.strip()}", "checked_at": time.time()}
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {"healthy": False, "status": "health check failed", "checked_at": time.time()}


def _execute_rollback(incident: Dict, fix_command: str, result: Dict):
    runbooks = load_runbooks()
    rb = match_runbook(incident, runbooks)
    rollback_cmd = None
    if rb and rb.get("rollback"):
        rollback_cmd = rb["rollback"].get("steps", [{}])[0].get("action")
    if not rollback_cmd:
        parts = fix_command.split()
        if "restart" in parts:
            rollback_cmd = " ".join(parts)
        elif "rollout" in parts and "undo" in parts:
            rollback_cmd = fix_command
        else:
            rollback_cmd = f"docker restart {incident.get('service', 'unknown')}-01"

    try:
        subprocess.run(rollback_cmd.split(), capture_output=True, text=True, timeout=30)
        result["rollback_executed"] = True
        result["rollback_command"] = rollback_cmd
    except (subprocess.TimeoutExpired, FileNotFoundError):
        result["rollback_executed"] = False
        result["rollback_error"] = "Rollback failed"


def _log_remediation(result: Dict):
    path = Path(REMEDIATION_LOG)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(result, default=str) + "\n")
