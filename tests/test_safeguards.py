from src.safeguards import validate_command, BLOCKLIST

def test_blocklisted_command():
    result = validate_command("rm -rf /")
    assert result["allowed"] == False

def test_safe_command():
    from src.safeguards import _fix_history
    _fix_history.clear()
    result = validate_command("echo hello")
    assert result["allowed"] == True

def test_allowlist_blocked():
    result = validate_command("unknown-tool do-stuff")
    assert result["allowed"] == False
    assert result["blocked_by"] == "allowlist"

def test_blocklist_not_empty():
    assert len(BLOCKLIST) > 0
