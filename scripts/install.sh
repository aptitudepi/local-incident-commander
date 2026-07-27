#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────
# Local Incident Commander — One-Line Install Script
# ─────────────────────────────────────────────────────────────
# Usage: bash <(curl -s https://raw.githubusercontent.com/.../install.sh)
# Or:    bash install.sh
# ─────────────────────────────────────────────────────────────

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="python3"
VENV_DIR="$REPO_DIR/.venv"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

trap 'log_error "Installation failed at line $LINENO"' ERR

echo ""
echo "=============================================="
echo " Local Incident Commander — Setup Wizard"
echo "=============================================="
echo ""

# ── Check Python ──────────────────────────────────────────
log_info "Checking Python..."
if ! command -v "$PYTHON" &>/dev/null; then
    log_error "Python 3 is required. Install it and re-run."
    exit 1
fi

# ── Create virtual env ───────────────────────────────────
log_info "Creating Python virtual environment..."
"$PYTHON" -m venv "$VENV_DIR"

# ── Activate ─────────────────────────────────────────────
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# ── Install dependencies ─────────────────────────────────
log_info "Installing Python dependencies..."
if [ -f "$REPO_DIR/requirements.txt" ]; then
    pip install --quiet --upgrade pip
    pip install --quiet -r "$REPO_DIR/requirements.txt"
else
    log_warn "No requirements.txt found. Creating default..."
    cat > "$REPO_DIR/requirements.txt" <<'EOF'
fastapi==0.115.0
uvicorn==0.30.0
pyyaml==6.0.2
httpx==0.27.0
pydantic==2.9.0
rich==13.8.0
streamlit==1.39.0
plotly==5.24.0
pandas==2.2.0
numpy==1.26.0
transformers==4.44.0
torch==2.4.0
scikit-learn==1.5.0
EOF
    pip install --quiet --upgrade pip
    pip install --quiet -r "$REPO_DIR/requirements.txt"
fi

# ── Create directories ───────────────────────────────────
log_info "Creating required directories..."
mkdir -p "$REPO_DIR/inbox" "$REPO_DIR/reports" "$REPO_DIR/logs"

# ── Set permissions ──────────────────────────────────────
chmod +x "$REPO_DIR/scripts/"*.sh 2>/dev/null || true

# ── Config check ─────────────────────────────────────────
if [ ! -f "$REPO_DIR/config.yaml" ]; then
    log_warn "config.yaml not found — will be auto-created on first run."
fi

# ── OS detection ─────────────────────────────────────────
log_info "Detecting system..."
if command -v docker &>/dev/null; then
    log_info "Docker detected — microservice demo available."
else
    log_warn "Docker not detected — microservice demo will use stubs."
fi

if command -v vllm &>/dev/null; then
    log_info "vLLM detected — full inference available."
else
    log_warn "vLLM not detected — LLM endpoint will use transformers fallback."
fi

# ── Success ──────────────────────────────────────────────
echo ""
echo "=============================================="
echo " Installation Complete!"
echo "=============================================="
echo ""
echo "  Activate:   source .venv/bin/activate"
echo "  Dashboard:  streamlit run dashboard/app.py"
echo "  CLI help:   python -m src.cli --help"
echo "  Demo:       bash scripts/run_demo.sh"
echo "=============================================="
echo ""
