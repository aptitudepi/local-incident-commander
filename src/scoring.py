from typing import Dict, Optional


def compute_score(
    incident: Dict,
    action: str,
    profile: str = "hardened",
) -> int:
    severity = incident.get("severity", "Medium")
    events = incident.get("correlated_events", incident.get("events", []))
    has_security = incident.get("has_security", False)
    autonomy_level = incident.get("autonomy_level", 3)

    if profile == "insecure":
        return 100

    score = 0

    severity_weights = {
        "Critical": -5,
        "High": -2,
        "Medium": 1,
        "Low": 3,
    }
    score += severity_weights.get(severity, 0)

    action_weights = {
        "restart": 2,
        "clear-cache": 2,
        "drain": 1,
        "rollback": -3,
        "isolate": -3,
        "scale": -2,
        "deploy": -5,
        "stop": -4,
    }
    score += action_weights.get(action, 0)

    if autonomy_level >= 3:
        score += 1
    else:
        score -= 2

    if has_security:
        score -= 5

    return score


def should_auto_remediate(score: int, threshold: int = 0) -> bool:
    return score >= threshold


def auto_remediate_summary(score: int, threshold: int) -> Dict:
    if should_auto_remediate(score, threshold):
        return {
            "auto_remediate": True,
            "score": score,
            "threshold": threshold,
            "reason": f"Score {score} ≥ {threshold} — auto-remediated",
        }
    return {
        "auto_remediate": False,
        "score": score,
        "threshold": threshold,
        "reason": f"Score {score} < {threshold} — requires human approval",
    }
