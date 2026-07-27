#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Local Incident Commander — Trigger Network Block
# THE MOMENT: Demonstrates kernel-enforced policy denial.
# Shows a blocked egress with a named policy ID.
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -f "$REPO_DIR/.venv/bin/activate" ]; then
    source "$REPO_DIR/.venv/bin/activate"
fi

cd "$REPO_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo "══════════════════════════════════════════════════════════"
echo -e "  ${BOLD}${CYAN}THE MOMENT: Kernel-Enforced Policy Denial${NC}"
echo "══════════════════════════════════════════════════════════"
echo ""

ACTION="${1:-rollback}"
RESOURCE="${2:-checkout-service}"
PROFILE="${3:-hardened}"

echo -e "  ${BOLD}Evaluating:${NC} action=${ACTION}  resource=${RESOURCE}  profile=${PROFILE}"
echo ""

RESULT=$(python -m src.cli evaluate --action "$ACTION" --resource "$RESOURCE" --profile "$PROFILE" 2>&1 || true)

echo "$RESULT"
echo ""

echo "══════════════════════════════════════════════════════════"
echo -e "  ${BOLD}What just happened:${NC}"
echo ""
echo -e "  ${YELLOW}This is NOT a Slack approval button.${NC}"
echo -e "  ${YELLOW}This is NOT a vendor promise.${NC}"
echo -e "  ${YELLOW}${BOLD}This is a kernel boundary.${NC}${NC}"
echo ""
echo -e "  The agent ${RED}cannot violate${NC} this policy, even if it wanted to."
echo -e "  The policy ID is traceable. The denial is deterministic."
echo -e "  No competitor can replicate this on stage."
echo ""
echo -e "  ${GREEN}Policy ID:${NC} $(echo "$RESULT" | grep -oP '"policy_id":\s*"[^"]*"' | head -1 | cut -d'"' -f4 || echo 'see above')"
echo ""
echo "══════════════════════════════════════════════════════════"
echo ""
echo -e "  Contrast with insecure profile:"
echo -e "  ${BOLD}$ python -m src.cli evaluate --action $ACTION --resource $RESOURCE --profile insecure${NC}"
echo ""
python -m src.cli evaluate --action "$ACTION" --resource "$RESOURCE" --profile insecure
echo ""
echo "══════════════════════════════════════════════════════════"
