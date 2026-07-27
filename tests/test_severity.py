from src.severity import classify_severity

def test_classify_critical():
    assert classify_severity({"events": [{"payload": {"latency_ms": 500}}], "has_security": True}) == "Critical"

def test_classify_high():
    assert classify_severity({"events": [{"payload": {"latency_ms": 1200}}]}) == "High"

def test_classify_medium():
    assert classify_severity({"events": [{"payload": {"latency_ms": 500}}]}) == "Medium"

def test_classify_low():
    assert classify_severity({"events": [{"payload": {}}]}) == "Low"

def test_classify_empty():
    assert classify_severity({"events": [{"payload": {}}]}) == "Low"
