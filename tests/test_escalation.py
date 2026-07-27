from src.escalation import escalate

def test_escalation_empty():
    result = escalate({}, {"root_cause": "test"})
    assert result is not None
    assert "ticket_id" in result

def test_escalation_with_reason():
    result = escalate({"id": "INC-001"}, {"root_cause": "need human", "fix_command": ""})
    assert "ticket_id" in result
