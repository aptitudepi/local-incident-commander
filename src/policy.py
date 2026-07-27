from typing import Dict, Optional
import uuid
import json
from pathlib import Path
from src.cost_tracker import record_action_blocked
from src.openclaw_adapter import exec_policy_check, set_exec_policy, is_available as openclaw_available
from src.scoring import compute_score, auto_remediate_summary


HARDENED_RULES = {
    "blocklisted_commands": [
        "rm", "dd", "mkfs", "fdisk", "format", "shutdown", "reboot", "init",
    ],
    "default_deny_network": True,
    "allowed_egress": [],
    "require_human_approval_for": [
        "rollback", "restart", "isolate", "scale", "deploy",
    ],
    "run_as_user": "nobody",
    "run_as_group": "nogroup",
    "max_fixes_per_hour": 3,
    "rate_limit_seconds": 300,
}

INSECURE_RULES = {
    "blocklisted_commands": [],
    "default_deny_network": False,
    "allowed_egress": [{"host": "*", "port": "*"}],
    "require_human_approval_for": [],
    "run_as_user": "root",
    "run_as_group": "root",
    "max_fixes_per_hour": 100,
    "rate_limit_seconds": 0,
}

PROFILES = {
    "hardened": HARDENED_RULES,
    "insecure": INSECURE_RULES,
}


_AUTO_REMEDIATE_CONFIG = {"enabled": True, "score_threshold": 0, "report_path": "reports/incidents/"}

def configure_auto_remediate(config: Dict):
    _AUTO_REMEDIATE_CONFIG.update(config)


def _load_incident_for_scoring(resource: str) -> Optional[Dict]:
    report_dir = Path(_AUTO_REMEDIATE_CONFIG["report_path"])
    if not report_dir.exists():
        return None
    for f in sorted(report_dir.glob("*.json"), reverse=True):
        try:
            with open(f) as fh:
                data = json.load(fh)
            if data.get("incident_id", data.get("id", "")).startswith("INC-"):
                return data
        except (json.JSONDecodeError, OSError):
            continue
    return None


def evaluate(
    action: str,
    resource: str,
    profile: str = "hardened",
    autonomy_level: int = 3,
    dry_run: bool = False,
) -> Dict:
    rules = PROFILES.get(profile, HARDENED_RULES)

    openclaw_check = None
    if openclaw_available():
        openclaw_check = exec_policy_check(action, resource)

    if openclaw_check and not openclaw_check["allowed"]:
        result = _decision(False, openclaw_check["policy_id"],
                           openclaw_check["reason"], True, dry_run)
        result["source"] = "openclaw"
        if not dry_run:
            record_action_blocked(action, result["policy_id"], result["reason"])
        return result

    if action in rules["blocklisted_commands"]:
        result = _decision(False, "safeguard-001",
                           f"Command '{action}' is blocklisted. Never allowed.",
                           True, dry_run)
        if not dry_run:
            record_action_blocked(action, result["policy_id"], result["reason"])
        result["source"] = "local"
        return result

    if action in rules["require_human_approval_for"]:
        if autonomy_level >= 4:
            return _decision(True, f"policy-{uuid.uuid4().hex[:4]}",
                             f"Action '{action}' on '{resource}' allowed at autonomy level {autonomy_level}.",
                             False, dry_run)
        
        incident = _load_incident_for_scoring(resource)
        score = compute_score(incident or {}, action, profile)
        auto_result = auto_remediate_summary(score, _AUTO_REMEDIATE_CONFIG["score_threshold"])

        if _AUTO_REMEDIATE_CONFIG["enabled"] and auto_result["auto_remediate"]:
            return _decision(True, f"auto-{uuid.uuid4().hex[:4]}",
                             f"Auto-remediated: {auto_result['reason']}",
                             False, dry_run)

        result = _decision(False, f"policy-{uuid.uuid4().hex[:4]}",
                           f"Action '{action}' on '{resource}' requires human approval at autonomy level {autonomy_level}. Score={score}.",
                           True, dry_run)
        if not dry_run:
            record_action_blocked(action, result["policy_id"], result["reason"])
        return result

    if rules["default_deny_network"] and action in ("curl", "wget", "ssh", "nc"):
        result = _decision(False, "net-policy-001",
                           "Default-deny network policy. Egress not permitted.",
                           True, dry_run)
        if not dry_run:
            record_action_blocked(action, result["policy_id"], result["reason"])
        return result

    return _decision(True, "policy-default",
                     f"Action '{action}' on '{resource}' allowed by default policy.",
                     False, dry_run)


def _decision(allowed: bool, policy_id: str, reason: str, requires_approval: bool, dry_run: bool) -> Dict:
    return {
        "allowed": allowed,
        "decision": "allowed" if allowed else "denied",
        "policy_id": policy_id,
        "reason": reason,
        "requires_human_approval": requires_approval,
        "dry_run": dry_run,
        "safeguards_checked": True,
    }
