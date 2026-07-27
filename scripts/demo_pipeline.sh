#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# LIC — Full Demo Pipeline
# Run this script, then open http://localhost:8081 side-by-side
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_DIR"

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${CYAN}[LIC]${NC} $*"; }
ok()    { echo -e "${GREEN}[LIC]${NC} $*"; }
err()   { echo -e "${RED}[LIC]${NC} $*"; }
warn()  { echo -e "${YELLOW}[LIC]${NC} $*"; }
step()  { echo ""; echo -e "${BOLD}══ $* ══${NC}"; }

trap 'err "Pipeline failed at step $STEP"; exit 1' ERR

STEP=0

step "1/8 — Reset to clean state"
bash scripts/reset_demo.sh
python3 -c "from src.cost_tracker import reset_costs; reset_costs()"
ok "Clean state ready"

step "2/8 — Start live system monitor (background)"
bash scripts/system_monitor.sh > /dev/null 2>&1 &
MONITOR_PID=$!
ok "System monitor started (PID $MONITOR_PID)"

step "3/8 — Inject 10 synthetic alerts"
bash scripts/inject_fake_alerts.sh
ok "Alerts injected"

step "4/8 — Correlate, triage, remediate (LLM ~60s)"
python -m src.cli correlate --input-dir inbox/
ok "Correlation complete"

# Find the checkout-service with deploy for THE MOMENT
INCIDENT_ID=$(python3 -c "
import json
from pathlib import Path
for f in sorted(Path('reports/incidents').glob('*.json'), reverse=True):
    d = json.load(open(f))
    if d.get('service') == 'checkout-service' and d.get('has_deploy'):
        print(d['incident_id'])
        break
" 2>/dev/null || echo "")

step "5/8 — Triage a single incident (LLM)"
if [ -n "$INCIDENT_ID" ]; then
  python -m src.cli triage --incident-id "$INCIDENT_ID"
  ok "Triage complete for $INCIDENT_ID"
else
  warn "No checkout+deploy incident found, using first available"
  INCIDENT_ID=$(ls -t reports/incidents/*.json 2>/dev/null | head -1 | xargs -I{} python3 -c "import json; print(json.load(open('{}'))['incident_id'])")
  python -m src.cli triage --incident-id "$INCIDENT_ID"
fi

step "6/8 — THE MOMENT: Policy Evaluation"
echo ""
echo -e "${BOLD}HARDENED PROFILE:${NC}"
python -m src.cli evaluate --action rollback --resource checkout-service --profile hardened
echo ""
echo -e "${BOLD}INSECURE PROFILE (contrast):${NC}"
python -m src.cli evaluate --action rollback --resource checkout-service --profile insecure

step "7/8 — Cost savings report"
python -m src.cli cost

step "8/8 — OpenClaw Pattern Scan"
python -m src.cli learn 2>/dev/null || echo "No patterns yet"

step "✅ DEMO READY"
echo ""
echo -e "  ${BOLD}Glance dashboard:${NC}  http://localhost:8081"
echo -e "  ${BOLD}Full dashboard:${NC}   http://localhost:8501"
echo ""
echo -e "  Quick commands:"
echo -e "    THE MOMENT:    python -m src.cli evaluate --action rollback --resource checkout-service --profile hardened"
echo -e "    Contrast:      python -m src.cli evaluate --action rollback --resource checkout-service --profile insecure"
echo -e "    Cost:          python -m src.cli cost"
echo -e "    Rules:         python -m src.cli learn"
echo ""
ok "Pipeline complete. Ready for demo."
