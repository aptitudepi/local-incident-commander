#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# LIC — System Monitor
# Collects real host metrics and forwards them to LIC's webhook
# every 30 seconds. Runs in background during demo.
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WEBHOOK_URL="http://localhost:8081/webhook"
LOG_FILE="$REPO_DIR/logs/system_monitor.log"

mkdir -p "$REPO_DIR/logs"

info()  { echo "[$(date +%H:%M:%S)] $*" >> "$LOG_FILE"; }
error() { echo "[$(date +%H:%M:%S)] ERROR: $*" >> "$LOG_FILE"; }

info "System monitor started"

while true; do
  # CPU
  CPU_IDLE=$(top -bn1 2>/dev/null | grep "Cpu(s)" | awk '{print $8}' | sed 's/..,//' || echo "0")
  CPU_USAGE=$(echo "100 - $CPU_IDLE" | bc 2>/dev/null || echo "0")
  CPU_USAGE=${CPU_USAGE%.*}

  # Memory
  MEM_TOTAL=$(free -b | grep Mem | awk '{print $2}')
  MEM_USED=$(free -b | grep Mem | awk '{print $3}')
  MEM_PCT=$(echo "scale=1; $MEM_USED * 100 / $MEM_TOTAL" | bc 2>/dev/null || echo "0")

  # Disk
  DISK_PCT=$(df / | tail -1 | awk '{print $5}' | sed 's/%//' 2>/dev/null || echo "0")

  # Docker containers
  DOCKER_RUNNING=$(docker ps -q 2>/dev/null | wc -l || echo "0")
  DOCKER_TOTAL=$(docker ps -aq 2>/dev/null | wc -l || echo "0")

  # vLLM check
  VLLM_OK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/v1/models 2>/dev/null || echo "000")

  # Load average
  LOAD=$(cat /proc/loadavg 2>/dev/null | awk '{print $1}' || echo "0.0")

  EVENT=$(cat <<JSON
{
  "service": "system-monitor",
  "event_type": "metric",
  "severity": "info",
  "payload": {
    "cpu_percent": $CPU_USAGE,
    "memory_percent": $MEM_PCT,
    "disk_percent": $DISK_PCT,
    "docker_running": $DOCKER_RUNNING,
    "docker_total": $DOCKER_TOTAL,
    "load_1m": $LOAD,
    "vllm_status": $VLLM_OK,
    "host": "$(hostname)"
  }
}
JSON
  )

  if curl -s -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "$EVENT" \
    -o /dev/null -w "%{http_code}" 2>/dev/null | grep -q "202"; then
    info "Sent: CPU=${CPU_USAGE}% Mem=${MEM_PCT}% Disk=${DISK_PCT}% Docker=${DOCKER_RUNNING}/${DOCKER_TOTAL}"
  else
    error "Webhook POST failed"
  fi

  sleep 30
done
