from src.llm_brief import generate_brief, configure

def test_generate_brief_returns_string():
    result = generate_brief({"id": "INC-001", "service": "checkout"})
    assert isinstance(result, str)
    assert len(result) > 0

def test_configure():
    configure(endpoint="http://localhost:8000/v1", model="qwen")
    assert True
