from src.similarity import find_similar

def test_similarity_empty():
    result = find_similar({"id": "INC-001", "service": "checkout-service"})
    assert isinstance(result, list)

def test_similarity_returns_list():
    result = find_similar({"service": "checkout-service", "severity": "critical"})
    assert isinstance(result, list)
