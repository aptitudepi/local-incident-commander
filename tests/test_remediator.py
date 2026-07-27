from src.remediator import execute

def test_remediator_empty():
    result = execute({}, {"root_cause": "test", "fix_command": "echo test"})
    assert result is not None
    assert "status" in result

def test_remediator_not_dangerous():
    result = execute({"service": "checkout"}, {"root_cause": "cpu", "fix_command": "curl http://localhost"})
    assert result is not None
    assert "status" in result
