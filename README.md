# Local Incident Commander (LIC) — The AI SRE That Cannot Violate Policy

Sovereign AI SRE agent on Dell Pro Max + NVIDIA GB10. Zero data leaves the device.
Kernel-enforced action governance with named policy IDs — not a Slack button.

## Quick Start

```bash
# Run the full demo pipeline (10 alerts → correlate → triage → policy → cost)
bash scripts/demo_pipeline.sh
```

Then open http://localhost:8081 for the glance dashboard.

## Services

| Port | Service |
|------|---------|
| 8081 | LIC API + Glance dashboard |
| 8501 | Streamlit interactive dashboard |
| 8000 | vLLM (Qwen3.6-35B) |

## Architecture

1. **Deterministic core** — correlation, severity, policy evaluation (rule-based, testable in CI)
2. **Kernel-enforced governance** — OpenClaw sandbox at the system-call boundary
3. **NHI Zero Trust** — least-privilege agent, default-deny egress, per-action authorization

## Commands

```bash
python -m src.cli correlate --input-dir inbox/   # Group events into incidents
python -m src.cli triage --incident-id INC-XXXX   # LLM triage with fix recommendation
python -m src.cli evaluate --action rollback --resource checkout-service --profile hardened  # THE MOMENT
python -m src.cli evaluate --action rollback --resource checkout-service --profile insecure   # Contrast
python -m src.cli cost                            # Cost savings report
python -m src.cli learn                           # Pattern-based rule suggestions
python -m src.cli learn --adopt <pattern-key>     # Adopt a learned rule
```

## Stack

- **Model:** Qwen3.6-35B-A3B-NVFP4 via vLLM on GB10
- **Policy:** OpenClaw sandbox + local rule engine
- **Dashboard:** Streamlit (8501) + static HTML (8081)
- **Ingestion:** Syslog UDP 5514, webhook POST :8081, file drop to `inbox/`
