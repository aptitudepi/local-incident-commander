# Local Incident Commander — Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Signal Ingestion                       │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ Syslog   │  │ File Watcher │  │ HTTP / Webhook API │  │
│  │ UDP:5514 │  │ inbox/       │  │ REST :8080         │  │
│  └────┬─────┘  └──────┬───────┘  └─────────┬──────────┘  │
│       └───────────────┼────────────────────┘              │
│                       ▼                                   │
│                 [Signal Store]                            │
├──────────────────────────────────────────────────────────┤
│                    Correlation                            │
│  Multi-signal + Topology-aware → Incident groups          │
├──────────────────────────────────────────────────────────┤
│                    Classification                         │
│  Severity: Critical / High / Medium / Low                 │
│  Threshold-based with override                            │
├──────────────────────────────────────────────────────────┤
│                    LLM Pipeline                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐│
│  │ vLLM     │  │ Qwen3.6  │  │ Transformers Fallback    ││
│  │ Server   │  │ Local    │  │ (no GPU / no vLLM)       ││
│  │ :8000    │  │ Model    │  │                          ││
│  └──────────┘  └──────────┘  └──────────────────────────┘│
│       │              │              │                     │
│       └──────────────┼──────────────┘                     │
│                      ▼                                    │
│              Brief Generator                              │
├──────────────────────────────────────────────────────────┤
│                    Safety Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐│
│  │ Policy   │  │ Safeguard│  │ Rate Limiter             ││
│  │ Evaluator│  │ Validator│  │ (3 fixes/hour)           ││
│  └──────────┘  └──────────┘  └──────────────────────────┘│
├──────────────────────────────────────────────────────────┤
│                    Action Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐│
│  │ Triage   │  │ Remediate│  │ Escalate → Jira/Slack/PD ││
│  │ Engine   │  │ Engine   │  │                          ││
│  └──────────┘  └──────────┘  └──────────────────────────┘│
├──────────────────────────────────────────────────────────┤
│                    Observability                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐│
│  │ Cost     │  │ System   │  │ Reports & PIRs           ││
│  │ Tracker  │  │ Monitor  │  │                           ││
│  └──────────┘  └──────────┘  └──────────────────────────┘│
├──────────────────────────────────────────────────────────┤
│                    User Interfaces                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐│
│  │ CLI      │  │Streamlit │  │ FastAPI / Web UI         ││
│  │ 10 cmds  │  │Dashboard │  │                          ││
│  └──────────┘  └──────────┘  └──────────────────────────┘│
└──────────────────────────────────────────────────────────┘

                     Docker Topology

    ┌─────────────┐     ┌─────────────┐
    │  Checkout   │     │   Payment   │
    │  :5001      │◄────┤  :5002      │
    └──────┬──────┘     └──────┬──────┘
           │                   │
    ┌──────▼───────────────────▼──────┐
    │         API Gateway :5000        │
    │          ┌─────────────┐         │
    │          │   Auth      │         │
    │          │  :5003      │         │
    │          └─────────────┘         │
    │          ┌─────────────┐         │
    │          │  Inventory  │         │
    │          │  :5004      │         │
    │          └─────────────┘         │
    │          ┌─────────────┐         │
    │          │  Notify     │         │
    │          │  :5005      │         │
    │          └─────────────┘         │
    └─────────────────────────────────┘
                     │
    ┌────────────────▼────────────────┐
    │       Dashboard :8501           │
    │  (Streamlit + Plotly)           │
    └─────────────────────────────────┘
    ┌─────────────────────────────────┐
    │  vLLM Server :8000              │
    │  Qwen3.6-35B-A3B-NVFP4         │
    │  (GPU, 1 container)             │
    └─────────────────────────────────┘
```

## Data Flow

1. **Ingestion** → Signals arrive via syslog :5514, file drops inbox/, HTTP POST /webhook, or HEC :8080
2. **Correlation** → Multi-signal + topology-aware → incident groups
3. **Classification** → Severity thresholds → C/H/M/L
4. **Brief** → LLM generates executive summary
5. **Triage** → LLM identifies root cause + suggested fix
6. **Policy** → Action evaluated against hardened (default) or insecure profile
7. **Safeguards** → 7-layer safety validation (command blocklist, rate limit, human approval)
8. **Remediate** → Execute fix with verification
9. **Escalate** → If no fix or not approved: ticket + notification
10. **Track** → Cost savings, MTTR, incident count logged

## Key Design Decisions

- **Fully local** — Zero cloud API calls; model runs on-prem via vLLM
- **SQLite for hackathon** — Migrate to PostgreSQL/Supabase post-demo
- **Mock-friendly tests** — All tests use in-memory DB and mock LLM
- **Autonomy levels** — Per-service: 1 (manual) to 3 (autonomous)
- **Defense in depth** — Policy + Safeguards + Rate limiter in series
