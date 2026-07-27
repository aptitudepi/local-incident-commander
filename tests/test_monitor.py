from src.monitor import collect_health

def test_monitor_check():
    result = collect_health()
    assert isinstance(result, dict)
    assert "pipeline" in result
    assert "watcher" in result["pipeline"]
