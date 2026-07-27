#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Local Incident Commander — OpenClaw Setup
# Configures OpenClaw model provider + exec-policy for LIC
# ─────────────────────────────────────────────────────────────
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*"; }

echo ""
echo "=============================================="
echo " OpenClaw Integration Setup"
echo "=============================================="
echo ""

if ! command -v openclaw &>/dev/null; then
    err "OpenClaw is not installed. Install it first."
    exit 1
fi

info "Registering local Qwen model as OpenClaw provider 'lic'..."
openclaw config set models.providers.lic '{"baseUrl":"http://localhost:8000/v1","apiKey":"sk-no-key-needed","models":[{"id":"qwen","name":"Qwen 3.6 35B","api":"openai-completions","baseUrl":"http://localhost:8000/v1"}]}'

info "Verifying model registration..."
if openclaw infer model list 2>&1 | grep -q "lic/qwen"; then
    info "Model lic/qwen registered successfully."
else
    warn "Model not found. Continuing anyway."
fi

info "Setting exec-policy to cautious (hardened default)..."
openclaw exec-policy preset cautious 2>/dev/null || warn "Could not set exec-policy (may need gateway running)"

echo ""
echo "=============================================="
echo " Setup complete."
echo ""
echo " Test LLM: openclaw infer model run --model lic/qwen --prompt 'Say OK'"
echo "=============================================="
echo ""
