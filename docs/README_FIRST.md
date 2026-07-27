# Local Incident Commander — README FIRST

> **The only AI SRE whose actions are constrained by kernel policy rather than vendor promise.**
> Sovereign by default. Deterministic by design. Governed at the kernel boundary.

---

## Quick Start

```bash
# 1. Install dependencies
bash scripts/install.sh
source .venv/bin/activate

# 2. (Optional) Install vLLM for full AI — skip if model is unavailable
pip install vllm

# 3. Serve the local Qwen model
vllm serve /home/dell/repos/Qwen3.6-35B-A3B-NVFP4 \
  --trust-remote-code --kv-cache-dtype fp8 \
  --gpu-memory-utilization 0.4 --max-model-len 262144 \
  --served-model-name qwen

# 4. (Optional) Register model with OpenClaw for sandbox-policy enforcement
bash scripts/openclaw_setup.sh
```

## Run the Demo

```bash
bash scripts/run_demo.sh
```

Or step by step:

```bash
# 1. Seed sample signals
cp sample_data/* inbox/

# 2. Correlate signals into incidents
python -m src.cli correlate --input-dir inbox/

# 3. Classify severity
python -m src.cli classify --incident-id $(ls -t reports/incident_*.json | head -1 | xargs -I{} python3 -c "import json; print(json.load(open('{}'))['id'])")

# 4. Generate brief
python -m src.cli brief --incident-id INC-001

# 5. Evaluate policy
python -m src.cli evaluate --action restart --resource checkout-service

# 6. Auto-triage
python -m src.cli triage --incident-id INC-001

# 7. Attempt remediation
python -m src.cli remediate --incident-id INC-001

# 8. Generate report
python -m src.cli report --incident-id INC-001

# 9. Show cost savings
python -m src.cli cost

# 10. System health
python -m src.cli status
```

## Dashboard

```bash
streamlit run dashboard/app.py
# Open http://localhost:8501
```

## Chaos Monkey (Continuous Event Injection)

```bash
# Terminal 1: Watch + Process
bash scripts/auto_pilot.sh

# Terminal 2: Inject events
bash scripts/chaos_monkey.sh --rate 10
```

## Project Structure

```
local-incident-commander/
├── config.yaml              # Configuration (auto-detected)
├── docker-compose.yml       # 8 microservices + dashboard + vLLM
├── requirements.txt         # Python dependencies
├── src/                     # Core engine (19 modules)
├── services/                # Microservice stubs for demo
├── dashboard/               # Streamlit dashboard
├── scripts/                 # Install, demo, chaos, preflight
├── runbooks/                # YAML remediation runbooks
├── sample_data/             # Synthetic operational signals
├── tests/                   # Pytest suite (28+ tests)
├── inbox/                   # Signal landing zone
├── reports/                 # Incident reports + PIRs
├── logs/                    # Runtime logs
└── docs/                    # Architecture, business, demo guides
```

## Running the AI Model

LIC works **without** the model (template fallback). For full AI:

### Install vLLM (recommended — ~200MB, uses NVIDIA-optimized flags):
```bash
source .venv/bin/activate
pip install vllm
```

Then serve the model:
```bash
vllm serve /home/dell/repos/Qwen3.6-35B-A3B-NVFP4 \
  --trust-remote-code \
  --kv-cache-dtype fp8 \
  --attention-backend flashinfer \
  --moe-backend marlin \
  --gpu-memory-utilization 0.4 \
  --max-model-len 262144 \
  --max-num-seqs 4 \
  --max-num-batched-tokens 8192 \
  --enable-chunked-prefill \
  --async-scheduling \
  --enable-prefix-caching \
  --load-format fastsafetensors \
  --reasoning-parser qwen3 \
  --tool-call-parser qwen3_xml \
  --enable-auto-tool-choice \
  --served-model-name qwen
```

### With Docker (alternative):
```bash
docker compose up vllm-server -d
```

## Testing

```bash
pytest -q --tb=short
```

## Important Notes

- **All data is synthetic.** Everything in sample_data/ is fictional.
- **Fully offline.** No cloud API calls. Ever.
- **Safety is layered.** OpenClaw exec-policy → Policy eval → Safeguard validation → Rate limiter.
- **OpenClaw integrated.** LLM inference via `openclaw infer`, policy via `openclaw exec-policy`, sandbox via `openclaw sandbox`.
- **License: All Rights Reserved.** This is a startup project.
- **Hackathon-ready.** 30-minute setup, 5-minute demo.
