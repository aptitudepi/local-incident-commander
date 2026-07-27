# Local Incident Commander — Frontend Guide

## Overview
The frontend is a Streamlit dashboard that displays real-time incident data from the Local Incident Commander engine.

## Running the Dashboard

```bash
source .venv/bin/activate
streamlit run dashboard/app.py
```

Open http://localhost:8501 in a browser.

## Dashboard Panels

1. **System Status Bar** — Total incidents, critical count, high count, cost savings
2. **Incident Timeline** — Scatter plot of incidents over time by severity
3. **Severity Distribution** — Pie chart of critical/high/medium/low
4. **Service Breakdown** — Bar chart of incidents by service
5. **Triage Results** — Latest auto-triage cards with root cause + suggested fix
6. **Post-Incident Reports** — Expandable PIR detail views
7. **Cost Tracker** — Hours saved, auto-resolved count, $ savings
8. **Savings Over Time** — Line chart of cumulative cost savings
9. **System Health** — LLM model status, inbox queue depth, report count
10. **Manual Refresh** — Sidebar button + auto-refresh at 2s interval

## Customization
- Change `refresh_interval_seconds` in `config.yaml`
- Toggle `dark_mode` in `config.yaml`
- Dashboard auto-reads all files from `reports/` directory

## During the Demo
The dashboard auto-updates as chaos_monkey injects events.

### Pro Tip for Presenters
Open the dashboard before running the demo. As you run `run_demo.sh`, the panels will populate in real time, creating a compelling visual narrative.

## Color Legend
- 🔴 Critical — `#e94560`
- 🟠 High — `#ff6b35`
- 🟡 Medium — `#ffc107`
- 🟢 Low — `#4caf50`
