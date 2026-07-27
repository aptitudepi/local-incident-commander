from src.watcher import scan_directory, parse_event_file

def test_scan_directory_empty():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        signals = scan_directory(tmp)
        assert signals == []

def test_scan_directory_with_files():
    import tempfile, json, os
    with tempfile.TemporaryDirectory() as tmp:
        f1 = os.path.join(tmp, "test1.json")
        f2 = os.path.join(tmp, "test2.txt")
        with open(f1, "w") as f: json.dump({"a": 1}, f)
        with open(f2, "w") as f: f.write("hello")
        signals = scan_directory(tmp)
        assert len(signals) == 2

def test_parse_event_file_json():
    import tempfile, json, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"service": "test"}, f)
        name = f.name
    try:
        ev = parse_event_file(name)
        assert ev is not None
        assert ev.get("service") == "test"
    finally:
        os.unlink(name)
