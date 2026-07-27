#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Local Incident Commander — Reset Demo
# Wipes all data, restores to clean state
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_DIR"

echo ""
echo "=============================================="
echo " Resetting Demo Environment"
echo "=============================================="
echo ""

echo "Clearing inbox/..."
rm -f inbox/*
echo "  done"

echo "Clearing reports/..."
rm -rf reports/*
mkdir -p reports/briefs reports/events reports/incidents reports/metrics reports/tickets
echo "  done"

echo "Clearing logs/..."
rm -rf logs/*
mkdir -p logs
echo "  done"

echo "Removing SQLite database..."
rm -f reports/reports.db
echo "  done"

echo "Reloading sample data..."
cp -n sample_data/* inbox/ 2>/dev/null || true
echo "  done"

echo ""
echo "=============================================="
echo " Demo environment reset to clean state."
echo " Run  bash scripts/preflight.sh  to verify."
echo "=============================================="
echo ""
