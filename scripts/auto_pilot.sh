#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Local Incident Commander — Auto-Pilot Mode
# Continuously watches inbox/ and runs the full pipeline
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_DIR"

# Activate virtualenv if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[AUTO-PILOT]${NC} $*"; }
ok()    { echo -e "${GREEN}[AUTO-PILOT]${NC} $*"; }
warn()  { echo -e "${YELLOW}[AUTO-PILOT]${NC} $*"; }
err()   { echo -e "${RED}[AUTO-PILOT]${NC} $*"; }

mkdir -p inbox reports logs

info "Auto-Pilot mode engaged"
info "Watching inbox/ for new signals..."
echo ""

WATCHED=()
while true; do
    for f in inbox/*; do
        [ -f "$f" ] || continue
        if [[ ! " ${WATCHED[@]} " =~ " $f " ]]; then
            WATCHED+=("$f")
            info "New signal detected: $f"

            # Phase 1: Correlate
            ok "Running correlation..."
            python -m src.cli correlate --input-dir inbox/ 2>&1 | sed 's/^/  /'
            echo ""

            # Find latest incident
            LATEST_INCIDENT=$(ls -t reports/incidents/*.json 2>/dev/null | head -1)
            if [ -n "$LATEST_INCIDENT" ]; then
                INCIDENT_ID=$(python3 -c "import json; d=json.load(open('$LATEST_INCIDENT')); print(d.get('incident_id',d.get('id','unknown')))" 2>/dev/null || echo "unknown")

                # Phase 2: Classify
                ok "Classifying incident $INCIDENT_ID..."
                python -m src.cli classify --incident-id "$INCIDENT_ID" 2>&1 | sed 's/^/  /'
                echo ""

                # Phase 3: Brief
                ok "Generating brief for incident $INCIDENT_ID..."
                python -m src.cli brief --incident-id "$INCIDENT_ID" 2>&1 | sed 's/^/  /'
                echo ""

                # Phase 4: Triage
                ok "Triaging incident $INCIDENT_ID..."
                python -m src.cli triage --incident-id "$INCIDENT_ID" 2>&1 | sed 's/^/  /'
                echo ""

                ok "Incident $INCIDENT_ID processed."
            else
                warn "No incident report generated — signals may be noise."
            fi
        fi
    done
    sleep 5
done
