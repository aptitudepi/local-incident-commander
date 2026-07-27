import logging

logger = logging.getLogger(__name__)

MODEL_PATH = None

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    AutoModelForCausalLM = None
    AutoTokenizer = None


def set_model_path(path: str):
    global MODEL_PATH
    MODEL_PATH = path


def generate(
    prompt: str,
    max_tokens: int = 300,
    temperature: float = 0.3,
    think: bool = True,
) -> str:
    if not TRANSFORMERS_AVAILABLE or MODEL_PATH is None:
        raise ImportError("Transformers not available or model path not set")

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)

    if think:
        prompt = f"Reason step by step, then provide your answer.\n\n{prompt}"
    else:
        prompt = f"Answer directly without reasoning.\n\n{prompt}"

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        temperature=temperature,
        do_sample=temperature > 0,
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if prompt in response:
        response = response[len(prompt):].strip()
    return response
