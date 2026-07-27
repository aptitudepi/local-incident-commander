#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Local Incident Commander — Preflight Checklist
# Verifies the system is ready before demo or dev work
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_DIR"

PASS=0
FAIL=0
WARN=0

check() {
    local label="$1"
    local cmd="$2"
    if eval "$cmd" &>/dev/null; then
        echo -e "  [PASS]  $label"
        PASS=$((PASS + 1))
    else
        echo -e "  [FAIL]  $label"
        FAIL=$((FAIL + 1))
    fi
}

warn_check() {
    local label="$1"
    local cmd="$2"
    if eval "$cmd" &>/dev/null; then
        echo -e "  [PASS]  $label"
        PASS=$((PASS + 1))
    else
        echo -e "  [WARN]  $label"
        WARN=$((WARN + 1))
    fi
}

echo ""
echo "=============================================="
echo " Local Incident Commander — Preflight Check"
echo "=============================================="
echo ""

echo "── Core Files ──────────────────────────────"
check "cli.py exists"               "test -f src/cli.py"
check "config.yaml exists"          "test -f config.yaml"
check "requirements.txt exists"     "test -f requirements.txt"

echo ""
echo "── Python Environment ──────────────────────"
check "python3 found"               "command -v python3"
check "pip found"                   "python3 -m pip --version"
warn_check "virtual env exists"     "test -d .venv"

echo ""
echo "── Directories ─────────────────────────────"
check "inbox/ exists"               "test -d inbox"
check "reports/ exists"             "test -d reports"
check "logs/ exists"                "test -d logs"
check "runbooks/ exists"            "test -d runbooks"
check "sample_data/ exists"         "test -d sample_data"
check "tests/ exists"               "test -d tests"
check "scripts/ exists"             "test -d scripts"
check "dashboard/ exists"           "test -d dashboard"

echo ""
echo "── Sample Data ─────────────────────────────"
for f in sample_data/*; do
    [ -f "$f" ] && check "sample: $(basename "$f")" "test -f '$f'"
done

echo ""
echo "── Runbooks ────────────────────────────────"
for f in runbooks/*.yaml; do
    [ -f "$f" ] && check "runbook: $(basename "$f")" "test -f '$f'"
done

echo ""
echo "── Scripts ─────────────────────────────────"
for f in scripts/*.sh; do
    [ -f "$f" ] && check "script: $(basename "$f") (has shebang)" "head -1 '$f' | grep -qE '^#!/'"
done

echo ""
echo "── Optional Tools ──────────────────────────"
warn_check "Docker found"            "command -v docker"
warn_check "vLLM found"             "command -v vllm"
warn_check "Qwen model downloaded"  "test -d /home/dell/repos/Qwen3.6-35B-A3B-NVFP4"

echo ""
echo "=============================================="
echo " Results:  $PASS passed, $FAIL failed, $WARN warnings"
echo "=============================================="
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo "Fix the failures above before running the demo."
    echo ""
    exit 1
fi

if [ "$WARN" -gt 0 ]; then
    echo "Warnings indicate optional components. Demo may still work."
    echo ""
fi

echo "✓ Ready to go!"
echo ""
