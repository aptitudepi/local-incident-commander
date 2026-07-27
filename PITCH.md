Title: Local Incident Commander (LIC) — The AI SRE That Cannot Violate Policy

Tags: AIOps, SRE, sovereign AI, air-gapped, non-human identity, kernel-enforced governance, GB10, edge

---

## 2-Minute Demo Script (for video recording)

**Setup:** Terminal left, `http://localhost:8081` right. Script has already been run once (incidents exist).

```
[0:00-0:15] "Everything here runs on this $4K Dell Pro Max with NVIDIA GB10. No cloud. No network."
  → Point at 8081 glance: 4 green checks, incident table populated

[0:15-0:30] "I just injected a bad deploy to checkout-service — latency spike, error rate climbing."
  → bash scripts/inject_fake_alerts.sh
  → python -m src.cli correlate --input-dir inbox/
  → Point at 8081: incidents table filling in

[0:30-0:45] "The local Qwen3.6 LLM triages it. It recommends rollback. But it does not decide."
  → python -m src.cli triage --incident-id <latest checkout-service incident from 8081>

[0:45-1:10] "THE MOMENT. I ask LIC to roll back checkout-service."
  → python -m src.cli evaluate --action rollback --resource checkout-service --profile hardened
  [Pause 3s. Point at "denied" + "policy-XXXX"]
  "That's a kernel boundary, not a Slack button. The agent cannot violate this."
  → python -m src.cli evaluate --action rollback --resource checkout-service --profile insecure
  "Same engine, different config — auto-approved. This is every other vendor's default."

[1:10-1:25] "Cost tracking: every denied action has a named policy ID for audit."
  → python -m src.cli cost
  → Point at "Blocked Actions": policy ID, timestamp, reason

[1:25-1:40] "OpenClaw learns from patterns. auth-service had 5 security alerts — it suggests an isolate rule."
  → python -m src.cli learn
  → python -m src.cli learn --adopt auth-service:alert
  → Point at "Adopted Rules" in 8081 glance or Rules tab in 8501

[1:40-2:00] "Five verticals where cloud AI SRE tools cannot compete — healthcare, finance, defense, telecom, OT.
   $33B ITOM spend. We're the only option where cloud AI is prohibited by law.
   Sovereign by default. Deterministic by design. Governed at the kernel boundary."
```

---

## Executive Summary (30-second version)

Every minute a production app is broken costs $5K-$15K. The people who fix this (SREs — site reliability engineers) spend 90% of their time buried in false alarms from 50+ services each screaming at once. AI tools promise to help, but they need your logs to leave your network — illegal for healthcare, finance, defense, telecom — and their "safety" is a Slack button the AI can ignore. LIC runs on a $4K Dell Pro Max with NVIDIA GB10: data never leaves, and when it says "denied" that's a kernel boundary, not a chat message.

---

## 5-Minute Pitch Script

**[0:00–0:45] What SREs Actually Do**

"Every company that runs software has someone whose job is keeping it running. They're called Site Reliability Engineers — SREs. Their reality is war by a thousand alerts.

A typical setup: 50 microservices. Each generates logs, metrics, alerts. Most are false alarms. A real incident — a deploy that broke checkout, a database that's about to fill up — gets buried in the noise. Finding it takes 60+ minutes on average. Each minute of downtime costs $5,000 to $15,000 depending on the business.

The AIOps market — AI for operations — is $19B because every company wants this solved. But the tools that fix it have two problems that aren't being addressed.

**[0:45–1:30] Two Gaps No One Is Solving**

"First: data sovereignty. Datadog Bits AI, Resolve.ai, PagerDuty — they all need your production logs to reach their cloud API. Logs with PII, network topology, subscriber identifiers. For a hospital under HIPAA, a bank under SOX/PCI-DSS, a defense contractor under ITAR, a telecom under GDPR — the answer from their CISO is no. A contract clause saying 'we promise not to look' doesn't change the network architecture.

Second: agent governance. The moment an AI can propose restarting a server or rolling back a deploy, you've created a non-human identity with production access and no real authorization model. Every vendor solves this with a Slack approval button — a popup the agent's own runtime could bypass because it's application-layer software, not a system boundary.

Two unsolved problems: operators who can't use cloud AI tools, and tools that can't actually enforce their own safety rules."

**[1:30–2:15] The LIC Pipeline — Live Demo**

"I'll show you the full pipeline on this Dell Pro Max with GB10. No cloud. No network. Watch.

[Run: `bash scripts/system_monitor.sh &`]
"LIC is monitoring this laptop right now — CPU, memory, disk. Real metrics hitting the dashboard.

[Run: `bash scripts/inject_fake_alerts.sh`]
"I just simulated a deploy to checkout-service, a latency spike, and a DB pool warning.

[Run: `python -m src.cli correlate --input-dir inbox/`]
"LIC grouped them into one incident — deterministic, rule-based. No ML involved.

[Run: `python -m src.cli triage --incident-id INC-XXXX`]
"The local Qwen3.6 LLM writes an executive brief. Notice: it recommends. It does not decide.

Now THE MOMENT. I ask LIC to roll back checkout-service.

[Run: `python -m src.cli evaluate --action rollback --resource checkout-service --profile hardened`]

```
Decision: denied. Policy ID: policy-c76a.
```

[Pause 3 seconds. Point at the screen.]

That is not a Slack button. That is not a vendor promise. That is a kernel boundary. The agent cannot make this system call even if its code tried. The denial has a named, traceable policy ID.

Now the contrast:

[Run: `python -m src.cli evaluate --action rollback --resource checkout-service --profile insecure`]

```
Decision: allowed.
```

Same engine, same code, different config — auto-approved. This is what every other vendor ships by default."

**[2:15–2:45] Architecture**

"Three layers, and the order matters:

1. **Deterministic core** — correlation, severity classification, policy evaluation. All rule-based. Testable in CI, reviewable in git, presentable to an auditor. The LLM is nowhere near the decision path.

2. **Kernel-enforced governance** — OpenClaw sandbox enforces the policy at the system-call boundary. Not application code. Not a Slack button. A boundary the agent cannot cross.

3. **NHI Zero Trust** — the agent is scoped least privilege, default-deny egress, per-action authorization. Every decision logged with policy ID, timestamp, reason."

**[2:45–3:15] Auto-Remediation With Scoring**

"Not everything needs a human. Low-severity restart? Clear a cache? The system scores each incident:

- LOW severity + non-destructive action = auto-execute
- HIGH severity + destructive action = blocked by default

The scoring is configurable, transparent, and logged. No black boxes. Operators tune the threshold, not the model."

**[3:15–3:45] The Market**

"Five verticals where cloud AI SRE tools structurally cannot compete:

Telecom NOCs with subscriber PII. Hospitals under HIPAA. Financial services under SOX and PCI-DSS. OT/industrial sites with intermittent backhaul. Defense environments behind air-gaps — GovCloud can't serve SAP/SCI networks or tactical deployments.

$33B in IT operations spend across these five. 56% of AIOps remains on-premises precisely because regulated industries cannot use the cloud. The honest TAM for a sovereign-only agent: $7.5B today, $15B+ by 2030.

We don't compete on feature count. We're the only option where cloud AI is prohibited by law."

**[3:45–4:15] Go-to-Market + Ask**

"Ship LIC as a preloaded Dell Pro Max with GB10 — hardware, model, policy pack, audit store. Procurement is a hardware PO, not a security review. Converts six months of compliance negotiation into a purchase order.

Dell and NVIDIA need proof workloads for GB10. LIC is a clean attach story for their field teams.

We want one design partner: 30 days read-only against your historical incidents. We deliver agreement rate vs human RCA, blocked-action counts, time-to-brief comparison. You choose when to climb the trust ladder."

**[4:15–4:30] The Close**

> Not the smartest AI SRE — the only one that can be deployed where the smart ones are legally prohibited. And the only one whose actions are constrained by kernel policy rather than vendor promise.

Local Incident Commander. Sovereign by default. Deterministic by design. Governed at the kernel boundary."

**[4:30–5:00] Q&A — see Judge Feedback section below**

---

## Slide Outlines (10 slides)

### Slide 1: Title
- LIC — The AI SRE That Cannot Violate Policy
- Tagline: Sovereign by default. Deterministic by design. Governed at the kernel boundary.

### Slide 2: The SRE Problem (First Principles)
- What SREs do: keep 50+ services running, drowning in alert noise
- 60+ min avg time to find real incident × $5K-$15K/min downtime
- AI tools promise help but have two unsolved problems

### Slide 3: Two Gaps
- Two columns:
  - **Sovereignty Wall**: Cloud AI requires logs to leave network → prohibited for HIPAA, SOX, PCI-DSS, ITAR, CPNI
  - **Governance Gap**: AI agent = NHI with production access → safety is a Slack button the agent can bypass

### Slide 4: Live Pipeline (Visual)
- Flow diagram: System → Syslog/Webhook → Correlator → LLM Brief → Policy Engine → DENY/ALLOW
- Highlight: **LLM narrates, rules decide**

### Slide 5: THE MOMENT
- Screenshot of terminal with `Decision: denied. Policy ID: policy-c76a.`
- Big text: **"That is a kernel boundary, not a Slack button"**
- Inset: insecure profile contrast

### Slide 6: Architecture (3-panel)
- Panel 1: Deterministic Core — correlation, severity, policy = rule-based
- Panel 2: Kernel Governance — OpenClaw sandbox, system-call enforcement
- Panel 3: NHI Zero Trust — least privilege, default-deny, per-action auth

### Slide 7: Auto-Remediation Scoring
- Score formula: severity + action risk + service criticality
- LOW/MEDIUM + safe action → auto-execute
- HIGH/CRITICAL + risky action → blocked by policy
- Configurable threshold, transparent logging

### Slide 8: The Market — 5 Verticals
- Telecom NOC, Healthcare, Financial Services, OT/Industrial, Defense
- $33B ITOM spend, $7.5B sovereign-addressable today
- 56% of AIOps remains on-premises

### Slide 9: Go-to-Market + Ask
- Appliance play: $4K Dell Pro Max + GB10
- Procurement: Hardware PO, not SaaS review
- 30-day read-only design partner trial
- Deliverables: agreement rate, blocked counts, time-to-brief

### Slide 10: Closing
- Positioning sentence (large text)
- Logo + tagline
- QR code / contact
- "Come see the live demo"

---

## Demo Steps — Smooth Execution

### Pre-Demo Checklist

```bash
# 1. Verify vLLM is running
curl -s http://localhost:8000/v1/models | head -3

# 2. Verify dashboard is running
curl -s -o /dev/null -w "%{http_code}" http://localhost:8501

# 3. Start LIC watch mode (API server + syslog listener)
python -m src.cli watch --port 8080 &

# 4. Start system monitor in background
bash scripts/system_monitor.sh &

# 5. Reset to clean state
cd /home/dell/repos/local-incident-commander
source .venv/bin/activate
bash scripts/reset_demo.sh

# 6. Open browser to http://localhost:8501
```

### Live Demo Script (3 minutes)

**[0:00] Step 1 — Show the live system**
```bash
# System monitor is already running in background
# Point to dashboard showing real CPU/memory metrics
```
"This laptop is being monitored right now. Real metrics, real time, all local."

**[0:15] Step 2 — Inject a realistic incident**
```bash
bash scripts/inject_fake_alerts.sh
```
"I just simulated: a deploy, a latency spike, and a DB pool warning — the three signals that precede a checkout outage."

**[0:30] Step 3 — Correlate**
```bash
python -m src.cli correlate --input-dir inbox/
```
"One incident formed. Three signals grouped by service and time window. Deterministic — no model guesses."

**[0:45] Step 4 — LLM Brief**
```bash
python -m src.cli triage --incident-id INC-XXXX
```
(Pick the checkout-service incident ID from step 3)
"The local LLM writes a brief. It recommends rollback. But it does not decide."

**[1:10] Step 5 — THE MOMENT**
```bash
python -m src.cli evaluate --action rollback --resource checkout-service --profile hardened
```
[Pause 2 seconds. Point at "denied" + "policy-c76a".]
"That is a kernel boundary. The agent cannot violate this policy even if it tried."

**[1:30] Step 6 — The Contrast**
```bash
python -m src.cli evaluate --action rollback --resource checkout-service --profile insecure
```
"Same action, no guardrails. Auto-approved. This is every other vendor's default."

**[1:45] Step 7 — Auto-Remediate (low-severity)**
```bash
python -m src.cli remediate --incident-id INC-XXXX --profile hardened
```
"For low-severity incidents with safe actions, LIC auto-executes. The scoring decided this was safe."

**[2:05] Step 8 — Dashboard**
Point to the dashboard (already open): Policy Denials feed, Incident Timeline, Cost Tracker.
"Every denial logged with named policy ID. Every decision auditable. Every dollar saved tracked."

**[2:25] Step 9 — Cost**
```bash
python -m src.cli cost
```

**[2:35] Step 10 — The Ask**
"30 days read-only against your historical incidents. We catch what humans miss and never execute what policy forbids."

**[3:00] Done.**

### Pro Tips

1. **24pt+ terminal font** — "denied" must be readable from 10 feet
2. **Split screen** — terminal on left, dashboard on right
3. **The 2-second pause after "denied"** — let them read "policy-c76a"
4. **LLM latency** — say "the model is thinking" and make eye contact
5. **Backup plan** — if LLM fails, template fallback produces same output
6. **The insecurity contrast is the closer** — "Every vendor shows you an approval popup. We show you a denial the agent cannot bypass."

---

## Judge Feedback — Responses

### 1. What kind of incidents will LIC focus on?

Latent failures — conditions that degrade over minutes to hours before becoming critical. Resource exhaustion (DB pool, memory, disk), latency degradation from bad deploys, security signals (SSH brute force, anomalous auth). We exclude novel code bugs (needs a code change) and hardware failures (needs a truck roll). LIC operates in the remediable middle — ~40% of incidents that end with restart, rollback, scale, drain, or isolate.

### 2. What repetitive incidents are resolved via rule-based decision making?

| Pattern | Signal | Action |
|---|---|---|
| DB pool exhausted | Connection timeout + pool metric low | `docker restart <db-sidecar>` |
| Bad deploy rollback | Deploy log + latency spike aligned | `kubectl rollout undo` |
| Cache stale | P99 spike, no deploy | `curl cache:port/clear` |
| Cert expiring | Expiration < 72h | `systemctl restart tls-proxy` |
| SSH brute force | Failure burst from single IP | `iptables block` via runbook |

### 3. Why rule-based for critical decisions?

Compliance artifact. An auditor accepts a written rule — "rollback requires human approval at autonomy level 3" — because it's deterministic, testable, and produces the same result every time. No auditor accepts "the neural network decided." The policy engine lives in git, is reviewed in PRs, tested with pytest. The LLM narrates. It does not decide.

### 4. Why local-only? Wouldn't cloud be better?

Five markets where cloud is structurally unavailable: telecom NOC (CPNI/GDPR), healthcare (HIPAA), financial services (SOX/PCI-DSS), OT/industrial (intermittent connectivity), defense (SAP/SCI air-gap, ITAR, tactical no-backhaul). Beyond data residency: kernel-enforced governance is structurally impossible in cloud architecture — when the agent and policy engine are on different hardware connected by a network, the policy is always application-layer.

$33B ITOM spend across these five verticals. 56% of AIOps remains on-premises. Honest TAM: $7.5B today, $15B+ by 2030.

### 5. Local vs cloud comparison

| Dimension | Cloud AI SRE | LIC Local Appliance |
|---|---|---|
| Data residency | Logs leave network | Zero data leaves |
| Connectivity | Always-on required | Fully offline capable |
| Policy enforcement | Application-layer (Slack button) | Kernel-boundary (OpenClaw sandbox) |
| Audit trail | Vendor-managed, opaque | Immutable, local, named policy IDs |
| Procurement | SaaS contract + security review | Hardware PO |
| Compliance artifact | "The model decided" | Written policy rules in git |
| Cost model | Monthly per-host SaaS | One-time capex (~$4K) |
| Auto-remediation | All-or-nothing | Scored: low-risk auto, high-risk blocked |
