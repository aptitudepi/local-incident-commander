#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# LIC — Live Demo Alert Injector
# Sends realistic synthetic alerts to LIC's webhook endpoint.
# Demonstrates the full correlation → triage → policy pipeline.
# ─────────────────────────────────────────────────────────────
set -euo pipefail

WEBHOOK_URL="http://localhost:8081/webhook"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

red()   { echo -e "\033[0;31m$*\033[0m"; }
green() { echo -e "\033[0;32m$*\033[0m"; }
blue()  { echo -e "\033[0;36m$*\033[0m"; }
bold()  { echo -e "\033[1m$*\033[0m"; }

echo ""
bold "══════════════════════════════════════════"
bold "  Injecting Synthetic Alerts into LIC"
bold "══════════════════════════════════════════"
echo ""

inject() {
  local service="$1"
  local type="$2"
  local severity="$3"
  local payload="$4"
  local desc="$5"

  EVENT=$(cat <<JSON
{
  "service": "$service",
  "event_type": "$type",
  "severity": "$severity",
  "timestamp": "$TIMESTAMP",
  "payload": $payload,
  "summary": "$desc"
}
JSON
  )

  echo -n "  [${service}] ${desc}... "
  STATUS=$(curl -s -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "$EVENT" \
    -o /dev/null -w "%{http_code}" 2>/dev/null)
  if [ "$STATUS" = "202" ]; then
    green "✓ injected"
  else
    red "✗ failed (HTTP $STATUS)"
  fi
  sleep 0.5
}

# ── Scenario 1: Bad deploy → latency spike on checkout-service ──
blue ""
blue "── Scenario 1: Bad deploy causes latency spike ──"
blue ""

inject "checkout-service" "deploy" "info" \
  '{"version":"v2.1.3-rc2","deployer":"ci-bot","duration_seconds":47,"changed_files":["payment_gateway.py","checkout_handler.py","inventory_client.py"],"canary_percent":100}' \
  "Deploy v2.1.3-rc2 to checkout-service (100% canary)"

inject "checkout-service" "alert" "high" \
  '{"latency_ms":5200,"p50_ms":3400,"p99_ms":5200,"error_rate":7.2,"throughput_rps":142,"threshold_ms":2000}' \
  "P99 latency 5200ms (threshold 2000ms) — 5-second degradation"

inject "checkout-service" "alert" "medium" \
  '{"latency_ms":4800,"p50_ms":3100,"p99_ms":4800,"error_rate":5.1,"throughput_rps":138,"threshold_ms":2000}' \
  "P99 latency 4800ms — still degrading, error rate climbing"

inject "checkout-service" "alert" "high" \
  '{"error_rate":12.3,"http_500_count":47,"endpoint":"/checkout/submit","deploy_version":"v2.1.3-rc2"}' \
  "12.3% error rate on /checkout/submit after deploy v2.1.3-rc2"

# ── Scenario 2: DB pool exhaustion on auth-service ──
blue ""
blue "── Scenario 2: Auth database pool exhaustion ──"
blue ""

inject "auth-service" "alert" "critical" \
  '{"db_connections":92,"max_connections":100,"connection_wait_ms":3400,"pool_hit_ratio":0.72,"active_queries":28}' \
  "DB pool at 92/100 connections — 3.4s wait time"

inject "auth-service" "alert" "high" \
  '{"db_connections":97,"max_connections":100,"connection_wait_ms":5800,"pool_hit_ratio":0.65,"active_queries":31}' \
  "DB pool at 97/100 — near exhaustion, 5.8s wait time"

# ── Scenario 3: SSH brute force on auth-service ──
blue ""
blue "── Scenario 3: SSH brute force attack ──"
blue ""

inject "auth-service" "alert" "critical" \
  '{"ssh_failures":143,"source_ips":["185.220.101.42","91.121.89.188","45.33.32.156"],"time_window_minutes":5,"target_user":"root","auth_method":"password"}' \
  "143 SSH failures from 3 IPs in 5 minutes — brute force in progress"

# ── Scenario 4: CPU spike on inventory-service ──
blue ""
blue "── Scenario 4: CPU spike on inventory-service ──"
blue ""

inject "inventory-service" "alert" "medium" \
  '{"cpu_percent":94,"memory_mb":2800,"disk_iops":4200,"thread_count":89,"gc_pause_ms":1200}' \
  "CPU at 94% — background job consuming resources"

# ── Scenario 5: Noise event (should NOT correlate) ──
blue ""
blue "── Scenario 5: Transient noise (should be filtered) ──"
blue ""

inject "checkout-service" "alert" "low" \
  '{"latency_ms":350,"duration_seconds":3,"auto_resolved":true}' \
  "Transient latency 350ms — self-resolved in 3s (noise)"

echo ""
bold "══════════════════════════════════════════"
bold "  Injection complete!"
bold "══════════════════════════════════════════"
echo ""
echo "  Next step: python -m src.cli correlate --input-dir inbox/"
echo "  Then:      python -m src.cli triage --incident-id INC-XXXX"
echo "  THE MOMENT: python -m src.cli evaluate --action rollback --resource checkout-service --profile hardened"
echo ""
