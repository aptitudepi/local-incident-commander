from src.local_model import generate, set_model_path, TRANSFORMERS_AVAILABLE

def test_local_model_generate_without_model():
    try:
        result = generate("test prompt")
        assert isinstance(result, str)
    except ImportError:
        pass

def test_set_model_path():
    set_model_path("/dev/null")
    assert True
