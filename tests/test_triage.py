from src.triage import triage

def test_triage_returns_dict():
    result = triage({"id": "INC-001", "service": "checkout-service", "events": [{"event_type": "alert", "payload": {"latency_ms": 500}}]})
    assert isinstance(result, dict)

def test_triage_empty():
    result = triage({})
    assert isinstance(result, dict)
