import tempfile, os
from src.runbook_engine import load_runbooks, match_runbook

def test_load_runbooks():
    rbs = load_runbooks()
    assert len(rbs) >= 0

def test_match_runbook_empty():
    result = match_runbook({}, [])
    assert result is None

def test_generate_runbook_from_fix():
    from src.runbook_engine import generate_runbook_from_fix
    rb = generate_runbook_from_fix({"id": "INC-001", "service": "test"}, "docker restart test")
    assert rb is not None
    assert "id" in rb
