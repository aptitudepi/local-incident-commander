from src.incident_report import build_incident_report, save_report

def test_build_incident_report():
    incident = {"incident_id": "INC-001", "service": "checkout-service", "events": [{"event_type": "alert", "payload": {"latency_ms": 500}}]}
    report = build_incident_report(incident, "critical")
    assert report["incident_id"] == "INC-001"
    assert report["service"] == "checkout-service"
    assert report["severity"] == "critical"
