#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Local Incident Commander — Demo Runner
# End-to-end walkthrough for hackathon demos
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_DIR"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

step()  { echo -e "\n${BOLD}${CYAN}═══ Step $1: $2 ═══${NC}\n"; }
ok()    { echo -e "${GREEN}  ✓ $*${NC}"; }
warn()  { echo -e "${YELLOW}  ⚠ $*${NC}"; }
cmd()   { echo -e "  \$ $*"; eval "$*"; }

echo ""
echo "=============================================="
echo " Local Incident Commander — Demo Run"
echo "=============================================="
echo ""

step 1 "Clean environment"
bash scripts/reset_demo.sh
echo ""

step 2 "Preflight check"
bash scripts/preflight.sh
echo ""

step 3 "Seed sample signals"
cp -n sample_data/* inbox/ 2>/dev/null
ok "Sample signals copied to inbox/"
ls -la inbox/
echo ""

step 4 "Correlate signals"
cmd python -m src.cli correlate --input-dir inbox/
echo ""

# Find the latest incident
LATEST_INCIDENT=$(ls -t reports/incidents/*.json 2>/dev/null | head -1)
if [ -z "$LATEST_INCIDENT" ]; then
    warn "No incident generated — may need to wait for more signals."
    warn "Try: bash scripts/chaos_monkey.sh --rate 2"
    exit 0
fi

INCIDENT_ID=$(python3 -c "import json; d=json.load(open('$LATEST_INCIDENT')); print(d.get('incident_id','unknown'))" 2>/dev/null || echo "unknown")
ok "Incident ID: $INCIDENT_ID"
echo ""

step 5 "Classify severity"
cmd python -m src.cli classify --incident-id "$INCIDENT_ID"
echo ""

step 6 "Generate brief"
cmd python -m src.cli brief --incident-id "$INCIDENT_ID"
echo ""

step 7 "Policy evaluation"
for action in restart rollback isolate; do
    cmd python -m src.cli evaluate --action "$action" --resource checkout-service --profile hardened
done
echo ""

step 8 "Triage (LLM-powered)"
cmd python -m src.cli triage --incident-id "$INCIDENT_ID"
echo ""

step 9 "Attempt remediation"
cmd python -m src.cli remediate --incident-id "$INCIDENT_ID"
echo ""

step 10 "Show cost tracker"
cmd python -m src.cli cost
echo ""

step 11 "Show system health"
cmd python -m src.cli cost
echo ""

step 12 "Show system health"
cmd python -m src.cli health
echo ""

echo ""
echo "=============================================="
echo " Demo Complete!"
echo "=============================================="
echo ""
echo "  Reports:  ls reports/"
echo "  Dashboard: streamlit run dashboard/app.py"
echo "  CLI help:  python -m src.cli --help"
echo "=============================================="
echo ""
