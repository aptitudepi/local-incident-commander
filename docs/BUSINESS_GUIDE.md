# Local Incident Commander — Business Guide

## One-Liner
**Local Incident Commander (LIC)** is the only AI SRE agent whose actions are constrained by kernel policy rather than vendor promise — built for operators who cannot ship production telemetry to a cloud inference endpoint.

## The Real Problem (Two Parts)

**Problem A — Alert fatigue (market context):** SRE teams drown in alerts (90%+ noise), average MTTR for critical incidents exceeds 60 minutes, each incident costs $5K–$15K. The AIOps market is ~$19B and growing because this is expensive and universal. It proves the budget exists.

**Problem B — The sovereignty wall (defensible):** A specific class of buyer cannot adopt cloud AI SRE tools because doing so requires streaming production logs — containing PII, subscriber identifiers, network topology, CUI, or trade secrets — to a vendor-managed inference endpoint. Of the fifteen most-cited AI SRE tools in 2026, only three credibly reach on-prem or air-gapped deployment tiers. Contractual mitigations (Privacy Mode, Zero Data Retention) are legal controls, not technical network boundaries — precisely the objection a bank or defense CISO raises and no vendor can answer with a contract.

**Problem C — The governed agent gap (our white space):** Once an agent can propose a rollback, restart, or config change, you have created a non-human identity with production write access and no meaningful authorization model. Most vendors handle this with a Slack approval button — an application-layer control the agent's own runtime could bypass. This is our actual competitive advantage.

## Our Solution

LIC provides three layers that no competitor combines:

1. **Deterministic decision layer (compliance artifact, not fallback):** Correlation, severity classification, and policy evaluation are rule-based — testable, reproducible, and explainable without invoking a model. An auditor asking "why did this incident get classified Critical" gets a rule, not a token distribution. The LLM is confined to narration (brief generation).

2. **Kernel-enforced action governance, not app-layer approval:** Our policy engine produces a denial with a named policy ID at the system-call boundary. This is the difference between a policy the agent *obeys* and a policy the agent *cannot violate*. Blocked egress with a named policy ID is the moment no competitor can replicate on stage.

3. **Agent as governed non-human identity:** An autonomous ops agent is an NHI with production entitlements. It receives the same Zero Trust treatment as any workload identity — scoped least privilege, default-deny egress, per-action authorization, immutable audit trail.

## Competitive Landscape

| Category | Players | Our Edge |
|----------|---------|----------|
| **Platform incumbents** | Datadog Bits AI, Dynatrace Davis, Splunk/Cisco, IBM Cloud Pak | Their business model *is* the cloud data pipeline — cannot credibly offer air-gapped without cannibalizing ingest revenue |
| **Incident management** | PagerDuty, incident.io, Rootly, FireHydrant | Adjacent, not competitive — potential integration surface |
| **Pure-play AI SRE** | Resolve.ai ($1B valuation), Traversal ($48M raised), Cleric | Lose on RCA accuracy — compete on governance, not intelligence |
| **Self-hostable / open-source** | HolmesGPT, K8sGPT, NudgeBee, Arvo | NudgeBee has human-in-the-loop; Arvo has "Sovereignty Spectrum" — the sovereignty positioning is already being staked out |
| **Sovereign-native** | Hyground (€3M pre-seed, Deutsche Bahn) | Direct proof the thesis is fundable — and the window is not open indefinitely |
| **DIY** | Senior SRE + Ollama weekend | Our answer is the governance layer and audit artifact, not correlation logic |

## Market Opportunity

- **TAM:** $45B (AIOps + incident management)
- **Beachhead:** Telecom network operations / OSS — your domain, edge sites with intermittent backhaul, subscriber data that cannot leave the NOC boundary, existing appliance procurement muscle
- **Second wave:** OT / industrial control networks (genuinely air-gapped by design)
- **Third wave:** Defense / federal contractors (CUI, IL5 — highest willingness to pay)
- **Why now:** GB10 hardware ($4K) turns a compliance blocker into a purchase order. Dell and NVIDIA need proof workloads that justify GB10 deployments. A sovereign ops agent is a clean attach story for their field teams.

## Business Model

- **Appliance, not SaaS.** Ship LIC as a preloaded box: hardware + model + policy pack + audit store. Sidesteps the entire "can we send you our logs" procurement conversation. Converts a security review into a hardware acceptance test. Charges capex rather than fighting for a new software line item.
- **Pricing:** Appliance list price + annual subscription for policy packs, model updates, and support. Anchor value against a single avoided major incident ($50K–$150K) or one FTE-year of on-call toil ($200K+), not against a per-host observability SKU.

## The Honest Positioning Sentence

> *Not the smartest AI SRE — the only one that can be deployed where the smart ones are legally prohibited, and the only one whose actions are constrained by kernel policy rather than vendor promise.*

## Pitch for Hackathon Judges (3-Minute Spine)

**Problem (30s):** Ops teams are drowning in alerts, and the tools that fix that require shipping your most sensitive telemetry to someone else's inference endpoint — so an entire class of operator is locked out. Second problem: the moment an agent can act, you've created an unmanaged non-human identity with production write access.

**Solution (45s):** LIC correlates deterministically (auditable), explains locally (LLM confined to narration), and cannot act — enforced at the kernel boundary, not by a Slack button. Three layers: deterministic decision layer, kernel-enforced governance, NHI Zero Trust.

**Live moment (60s):** The blocked egress with a named policy ID. [Run `evaluate --action rollback --resource checkout-service --profile hardened`] "That is not a vendor promise. That is a kernel boundary. This agent cannot violate this policy even if it wanted to."

**Why this hardware (15s):** A $4K Dell Pro Max with GB10 turns a compliance blocker into a purchase order. Dell and NVIDIA are looking for exactly this proof workload.

**Ask (30s):** We are looking for design partners — run LIC in read-only mode against your historical incident set for 30 days. We'll show you blocked-call counts, time-to-first-brief vs your baseline, and agreement rate against human RCA. Then you choose when to climb the trust ladder.

## Competitive Vulnerabilities (What Could Kill This)

| Threat | Mitigation |
|--------|------------|
| Incumbents ship an on-prem tier | Our defense is governance layer + audit story, not topology — topology is copyable, category ownership is less so |
| Model quality ceiling (9B < frontier) | LLM confined to synthesis; deterministic layer makes decisions |
| TAM ceiling from hardware attach (one box per site) | Fine for wedge; multi-site fleet management by Series A |
| Category confusion (benchmarked against Traversal) | Pitch as governed autonomous ops for sovereign environments — category of roughly three |

## Proof Points to Build Next

- Agreement rate against human RCA on customer's own historical incident set (run read-only for 30 days)
- Blocked-call counts from policy engine as ongoing security metric
- Time-to-first-brief versus their current triage baseline

## Revenue Projection (3-Year)

- Year 1: 10 appliance placements × $25K + 10 subscriptions × $5K = $300K ARR
- Year 2: 50 appliances × $25K + 40 subscriptions × $5K = $1.45M ARR
- Year 3: 200 appliances × $25K + 180 subscriptions × $5K + 5 enterprise × $100K = $6.4M ARR
