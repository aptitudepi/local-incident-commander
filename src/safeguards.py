import re
import time
from typing import Dict, List


BLOCKLIST = {
    "rm", "dd", "mkfs", "fdisk", "format", "shutdown", "reboot", "init",
    "poweroff", "halt", "mke2fs", "mkswap", "parted", "gdisk", "sfdisk",
    "pvcreate", "vgcreate", "lvcreate", "pvremove", "vgremove", "lvremove",
}

ALLOWLIST = {
    "docker", "kubectl", "systemctl", "service", "curl", "wget",
    "python", "node", "npm", "git", "echo", "cp", "mv", "mkdir",
    "chmod", "chown", "ln", "cat", "grep", "awk", "sed", "sort",
    "head", "tail", "wc", "date", "uptime", "free", "df", "ps", "top",
    "kill", "pkill", "ip", "iptables", "ufw",
}

MAX_FIXES_PER_HOUR = 3
RATE_LIMIT_SECONDS = 300
_fix_history: List[float] = []


def validate_command(command: str, service: str = "") -> Dict:
    result = {
        "command": command,
        "allowed": False,
        "checks": [],
        "blocked_by": None,
        "safe": False,
        "suggested_rollback": None,
    }

    parts = _split_command(command)
    if not parts:
        result["checks"].append({"check": "parse", "passed": False, "reason": "Empty command"})
        result["blocked_by"] = "parse"
        return result

    base = parts[0]

    check = _check_blocklist(base, parts)
    result["checks"].append(check)
    if not check["passed"]:
        result["blocked_by"] = "blocklist"
        return result

    check = _check_allowlist(base)
    result["checks"].append(check)
    if not check["passed"]:
        result["blocked_by"] = "allowlist"
        return result

    check = _check_arguments(parts)
    result["checks"].append(check)
    if not check["passed"]:
        result["blocked_by"] = "arguments"
        return result

    check = _check_rate_limit(service)
    result["checks"].append(check)
    if not check["passed"]:
        result["blocked_by"] = "rate_limit"
        return result

    result["allowed"] = True
    result["safe"] = True
    return result


def _split_command(command: str) -> List[str]:
    parts = []
    current = ""
    in_quote = False
    for ch in command.strip():
        if ch in ("'", '"'):
            in_quote = not in_quote
            current += ch
        elif ch.isspace() and not in_quote:
            if current:
                parts.append(current)
                current = ""
        else:
            current += ch
    if current:
        parts.append(current)
    return parts


def _check_blocklist(base: str, parts: List[str]) -> Dict:
    if base in BLOCKLIST:
        return {"check": "blocklist", "passed": False, "reason": f"'{base}' is blocklisted"}
    for part in parts:
        if part in BLOCKLIST:
            return {"check": "blocklist", "passed": False, "reason": f"'{part}' contains blocklisted command"}
        if "rm" in part and "--no-preserve-root" in part:
            return {"check": "blocklist", "passed": False, "reason": "Dangerous rm flags detected"}
        if ">" in part and "/dev/" in part:
            return {"check": "blocklist", "passed": False, "reason": "Block device write denied"}
    return {"check": "blocklist", "passed": True}


def _check_allowlist(base: str) -> Dict:
    if base in ALLOWLIST:
        return {"check": "allowlist", "passed": True}
    return {"check": "allowlist", "passed": False, "reason": f"'{base}' is not in allowed commands list"}


_dangerous_patterns = [
    (r"\.\./", "Path traversal detected"),
    (r"\$\(.*\)", "Shell injection via $()"),
    (r"`.*`", "Shell injection via backticks"),
    (r";\s*", "Command chaining with semicolon"),
    (r"\|\s*", "Command piping"),
    (r"&&\s*", "Command chaining with &&"),
    (r"\/etc\/", "Access to /etc denied"),
    (r"\/var\/", "Access to /var restricted"),
    (r">\s*\/", "Write to root filesystem denied"),
]


def _check_arguments(parts: List[str]) -> Dict:
    joined = " ".join(parts)
    for pattern, reason in _dangerous_patterns:
        if re.search(pattern, joined):
            return {"check": "arguments", "passed": False, "reason": reason}
    return {"check": "arguments", "passed": True}


def _check_rate_limit(service: str) -> Dict:
    global _fix_history
    now = time.time()
    _fix_history = [t for t in _fix_history if now - t < 3600]
    if len(_fix_history) >= MAX_FIXES_PER_HOUR:
        return {"check": "rate_limit", "passed": False,
                "reason": f"Rate limit exceeded: {MAX_FIXES_PER_HOUR}/hour"}
    if _fix_history and (now - _fix_history[-1] < RATE_LIMIT_SECONDS):
        wait = int(RATE_LIMIT_SECONDS - (now - _fix_history[-1]))
        return {"check": "rate_limit", "passed": False,
                "reason": f"Rate limit: wait {wait}s before next fix"}
    _fix_history.append(now)
    return {"check": "rate_limit", "passed": True}
