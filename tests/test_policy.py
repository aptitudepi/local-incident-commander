import json, os
from pathlib import Path
from src.policy import evaluate, HARDENED_RULES, INSECURE_RULES


def test_hardened_requires_approval():
    result = evaluate("rollback", "checkout-service", profile="hardened")
    assert result["allowed"] == False
    assert result["requires_human_approval"] == True


def test_insecure_auto_approve():
    result = evaluate("rollback", "checkout-service", profile="insecure")
    assert result["allowed"] == True


def test_unknown_action_allowed():
    result = evaluate("unknown-action", "checkout-service", profile="hardened")
    assert result["allowed"] == True


def test_auto_remediate_safe_action():
    Path("reports/incidents").mkdir(parents=True, exist_ok=True)
    with open("reports/incidents/INC-TEST-AUTO.json", "w") as f:
        json.dump({"incident_id": "INC-TEST-AUTO", "service": "test", "severity": "Low", "autonomy_level": 3, "has_security": False}, f)
    result = evaluate("restart", "checkout-service", profile="hardened")
    assert result["allowed"] == True
    os.remove("reports/incidents/INC-TEST-AUTO.json")


def test_rules_exist():
    assert len(HARDENED_RULES) > 0
    assert len(INSECURE_RULES) > 0
