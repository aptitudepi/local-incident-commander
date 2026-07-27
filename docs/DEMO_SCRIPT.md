# Local Incident Commander — Demo Script

**Total: ~10 minutes**

---

## Setup (2 min) — Backend

```bash
cd ~/repos/local-incident-commander
bash scripts/install.sh && source .venv/bin/activate
bash scripts/openclaw_setup.sh   # register model with OpenClaw
bash scripts/reset_demo.sh && bash scripts/preflight.sh
streamlit run dashboard/app.py   # open http://localhost:8501
```

---

## Act 1: The Problem (1 min) — Business

Show empty dashboard and empty inbox.

> "Every minute a critical incident goes unfixed costs $5K. SREs spend 90% of their time fighting false alarms. The tools that fix this require streaming your production telemetry — PII, topology, trade secrets — to someone else's inference endpoint. An entire class of operator is locked out by the sovereignty wall."

> "Second problem: the moment an agent can act, you've created an unmanaged non-human identity with production write access. Most vendors handle this with a Slack approval button — an application-layer control the agent's own runtime could bypass."

---

## Act 2: Signal Injection (1 min) — Frontend

```bash
cp sample_data/* inbox/
ls inbox/
```

Dashboard populates with signal data.

> "LIC ingests alerts, logs, and deploy events via file drops, syslog, or HTTP webhook — all locally."

---

## Act 3: Correlation + Classification (1 min) — Backend

```bash
python -m src.cli correlate --input-dir inbox/
python -m src.cli classify --incident-id INC-001
```

> "Deterministic correlation — no model involved. Three signals from the same service in a 15-minute window grouped into one incident. The severity classifier uses thresholds, not tokens. This is reproducible and auditable. An auditor asking 'why Critical' gets a rule, not a probability distribution."

---

## Act 4: Brief + Triage (1 min) — Backend

```bash
python -m src.cli brief --incident-id INC-001
python -m src.cli triage --incident-id INC-001
```

> "The LLM is confined to narration — it generates the brief and suggests a root cause. If the model endpoint is down, templates produce the same structure. The LLM advises; the deterministic layer decides."

---

## Act 5: *** THE MOMENT *** — Policy Eval (2 min) — Business

This is the centerpiece. Pause. Let it land.

```bash
python -m src.cli evaluate --action rollback --resource checkout-service --profile hardened
```

Read the output aloud:

> **"Decision: denied. Policy ID: policy-a1b2. Reason: Action 'rollback' on 'checkout-service' requires human approval at autonomy level 3."**

> "That is not a Slack button. That is not a vendor promise. **That is a kernel boundary enforced by OpenClaw exec-policy.** This agent cannot violate this policy even if it wanted to. Every competitor shows you an approval popup. We show you a denial this agent cannot bypass."

Now contrast with insecure:

```bash
python -m src.cli evaluate --action rollback --resource checkout-service --profile insecure
```

> "Insecure profile — auto-approved. Terrifying. Our customers choose their posture."

**Pause 3 seconds. Let the blocked-egress moment land.**

---

## Act 6: Security Incident (1 min) — Backend

```bash
cp sample_data/ssh_brute_force.json inbox/
python -m src.cli correlate --input-dir inbox/
python -m src.cli triage --incident-id INC-002
python -m src.cli evaluate --action isolate --resource auth-service --profile hardened
```

> "Security incident detected — 150 SSH attempts from 3 IPs in 10 seconds. Recommended action: isolate. Policy says human approval required at this autonomy level. The system will not let a compromised auth service be isolated without a human in the loop."

---

## Act 7: Dashboard + Cost Tracker (1 min) — Frontend

Refresh the browser. All panels populated.

```bash
python -m src.cli cost
```

> "Every auto-resolved incident saves 2+ engineering hours at $150/hr. Every policy block is a prevented disaster. The dashboard shows policy denials in real time."

---

## Act 8: Why This Hardware (30s) — Business

> "This entire system runs on a single Dell Pro Max with GB10 — a $4,000 desk-side appliance. That turns a compliance blocker into a purchase order. A bank's CISO says 'no cloud inference for our production logs' — we hand them a box. Dell and NVIDIA are looking for exactly this proof workload."

## Closing (30s) — Business

> **One-liner:** "Local Incident Commander — the only AI SRE whose actions are constrained by kernel policy rather than vendor promise."

> **Call to action:** "Run us in read-only mode against your historical incidents for 30 days. We'll show you blocked-call counts, time-to-first-brief, and agreement rate against your current triage baseline. Then you choose when to climb the trust ladder."

---

## Full Demo Timeline

| Time | Act | Speaker | Key Line |
|------|-----|---------|----------|
| 0:00–2:00 | Setup | Backend | — |
| 2:00–3:00 | Act 1: Problem | Business | "Sovereignty wall locks operators out of AI SRE tools" |
| 3:00–4:00 | Act 2: Injection | Frontend | Dashboard populates live |
| 4:00–5:00 | Act 3: Correlation | Backend | "Deterministic — reproducible — auditable" |
| 5:00–6:00 | Act 4: Brief | Backend | "LLM narrates; deterministic layer decides" |
| **6:00–8:00** | **Act 5: Policy** | **Business** | **"Kernel boundary, not Slack button"** |
| 8:00–9:00 | Act 6: Security | Backend | Security incident + mediated isolation |
| 9:00–10:00 | Act 7: Dashboard | Frontend | Cost tracker + policy denial feed |
| 10:00–10:30 | Act 8: Hardware | Business | "$4K box turns blocker into PO" |
| 10:30–11:00 | Closing | Business | One-liner + CTA |
