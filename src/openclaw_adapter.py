import subprocess
import json
import shutil
import os
from typing import Optional, Dict

OPENCLAW_PATH = shutil.which("openclaw")
OPENCLAW_AVAILABLE = OPENCLAW_PATH is not None and os.access(OPENCLAW_PATH, os.X_OK)


def _run_openclaw(args: list, timeout: int = 30) -> Optional[str]:
    if not OPENCLAW_AVAILABLE:
        return None
    try:
        result = subprocess.run(
            [OPENCLAW_PATH] + args,
            capture_output=True, text=True, timeout=timeout,
            env={**os.environ, "HOME": os.path.expanduser("~")}
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def call_llm(prompt: str, model: str = "lic/qwen") -> Optional[str]:
    if not OPENCLAW_AVAILABLE:
        return None
    output = _run_openclaw([
        "infer", "model", "run",
        "--model", model,
        "--prompt", prompt,
        "--json"
    ], timeout=60)
    if output:
        try:
            data = json.loads(output)
            if isinstance(data, dict):
                return data.get("text") or data.get("content") or data.get("output") or output
        except json.JSONDecodeError:
            return output
    return None


def exec_policy_check(action: str, resource: str) -> Optional[Dict]:
    if not OPENCLAW_AVAILABLE:
        return None
    status_output = _run_openclaw(["exec-policy", "show"], timeout=15)
    if status_output and "deny-all" in status_output.lower():
        return {
            "allowed": False,
            "policy_id": "openclaw-exec-policy",
            "reason": "OpenClaw exec-policy denies all tool execution",
            "source": "openclaw"
        }
    return {
        "allowed": True,
        "policy_id": "openclaw-default",
        "reason": "OpenClaw exec-policy allows execution",
        "source": "openclaw"
    }


def set_exec_policy(mode: str = "cautious") -> bool:
    if not OPENCLAW_AVAILABLE:
        return False
    result = _run_openclaw(["exec-policy", "preset", mode], timeout=15)
    return result is not None


def is_available() -> bool:
    return OPENCLAW_AVAILABLE
