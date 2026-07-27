from src.correlator import correlate, correlate_from_directory

def test_correlate_empty():
    result = correlate([])
    assert result == []

def test_correlate_related_alerts():
    signals = [
        {"service": "checkout-service", "event_type": "alert", "severity": "critical", "timestamp": "2026-07-26T15:30:00Z"},
        {"service": "checkout-service", "event_type": "alert", "severity": "high", "timestamp": "2026-07-26T15:31:00Z"},
    ]
    result = correlate(signals)
    assert len(result) > 0
