import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import os
import glob
import time
from datetime import datetime

st.set_page_config(page_title="Local Incident Commander", layout="wide", initial_sidebar_state="expanded")

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")
INCIDENTS_DIR = os.path.join(REPORTS_DIR, "incidents")
RUNBOOKS_DIR = os.path.join(os.path.dirname(__file__), "..", "runbooks")
SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "src")

st.markdown("""
<style>
    .stApp { background-color: #0d1117; }
    h1, h2, h3 { color: #e94560 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background: #161b22; border-radius: 6px; padding: 8px 16px; }
    .stTabs [aria-selected="true"] { background: #e94560 !important; }
    .blocked-card { background:#2d1b1b; border-left:4px solid #e94560; padding:12px; margin:6px 0; border-radius:5px; }
    .incident-critical { border-left: 4px solid #e94560; background: #2d1b1b; padding:12px; margin:6px 0; border-radius:5px; }
    .incident-high { border-left: 4px solid #ff6b35; background: #2d2515; padding:12px; margin:6px 0; border-radius:5px; }
    .incident-medium { border-left: 4px solid #ffc107; background: #2d2d15; padding:12px; margin:6px 0; border-radius:5px; }
    .incident-low { border-left: 4px solid #4caf50; background: #152d15; padding:12px; margin:6px 0; border-radius:5px; }
    .suggestion-card { background:#16213e; border-left:4px solid #0ea5e9; padding:12px; margin:6px 0; border-radius:5px; }
    div[data-testid="stMetricValue"] { font-size: 28px !important; }
</style>
""", unsafe_allow_html=True)

st.title("Local Incident Commander")
st.markdown("Sovereign AI SRE · Kernel-enforced governance · Local LLM")

sidebar_col = st.sidebar
sidebar_col.markdown(f"**Last update:** {datetime.now().strftime('%H:%M:%S')}")
sidebar_col.button("Refresh Now", on_click=lambda: None)

status_ok = os.path.exists("/home/dell/repos/Qwen3.6-35B-A3B-NVFP4")
sidebar_col.markdown(f"**Model:** {'✓ Qwen3.6-35B' if status_ok else '✗ Not found'}")
sidebar_col.markdown(f"**API:** localhost:8081")
sidebar_col.markdown(f"**vLLM:** localhost:8000")

inbox_count = len(glob.glob(os.path.join(os.path.dirname(__file__), "..", "inbox", "*")))
sidebar_col.markdown(f"**Inbox:** {inbox_count} pending")

def load_json(dirpath, pattern):
    files = sorted(glob.glob(os.path.join(dirpath, pattern)), key=os.path.getmtime, reverse=True)
    items = []
    for f in files:
        try:
            with open(f) as fh:
                items.append(json.load(fh))
        except (json.JSONDecodeError, OSError):
            continue
    return items

def load_file(path):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}

incidents = load_json(INCIDENTS_DIR, "*.json")
reports = load_json(REPORTS_DIR, "report_*.json")
triages = load_json(REPORTS_DIR, "triage_*.json")
costs = load_file(os.path.join(REPORTS_DIR, "metrics", "costs.json"))

tab_overview, tab_incidents, tab_triages, tab_reports, tab_rules, tab_cost = st.tabs([
    "Overview", "Incidents", "Triage", "Reports", "Rules", "Cost"
])

# ── TAB 1: Overview ──
with tab_overview:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Incidents", len(incidents))
    with col2:
        st.metric("Critical", len([i for i in incidents if str(i.get("severity","")).lower()=="critical"]))
    with col3:
        st.metric("High", len([i for i in incidents if str(i.get("severity","")).lower()=="high"]))
    with col4:
        st.metric("Medium", len([i for i in incidents if str(i.get("severity","")).lower()=="medium"]))
    with col5:
        st.metric("Total Savings", f"${costs.get('total_saved', 0):,.2f}")

    if incidents:
        st.subheader("Incident Timeline")
        df = pd.DataFrame(incidents)
        ts_col = next((c for c in ["timestamp", "created_at", "date"] if c in df.columns), None)
        sev_col = "severity" if "severity" in df.columns else None
        if ts_col and sev_col:
            df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
            df = df.dropna(subset=[ts_col]).sort_values(ts_col)
            fig = px.scatter(df, x=ts_col, y=sev_col, color=sev_col,
                             title="Incidents Over Time",
                             color_discrete_map={"critical":"#e94560","high":"#ff6b35","medium":"#ffc107","low":"#4caf50"},
                             hover_data=["incident_id", "service", "severity"])
            st.plotly_chart(fig, use_container_width=True)

        if sev_col:
            st.subheader("Severity Distribution")
            sev_counts = df[sev_col].value_counts()
            fig2 = px.pie(values=sev_counts.values, names=sev_counts.index,
                          title="Incidents by Severity",
                          color_discrete_map={"critical":"#e94560","high":"#ff6b35","medium":"#ffc107","low":"#4caf50"})
            st.plotly_chart(fig2, use_container_width=True)

        if "service" in df.columns:
            st.subheader("Service Breakdown")
            svc_counts = df["service"].value_counts().head(10)
            fig3 = px.bar(x=svc_counts.values, y=svc_counts.index, orientation="h",
                          title="Incidents by Service",
                          color_discrete_sequence=["#e94560"])
            st.plotly_chart(fig3, use_container_width=True)

# ── TAB 2: Incidents ──
with tab_incidents:
    st.subheader(f"All Incidents ({len(incidents)})")
    sev_filter = st.selectbox("Filter by severity", ["All", "Critical", "High", "Medium", "Low"])
    filtered = [i for i in incidents if sev_filter == "All" or str(i.get("severity","")).lower() == sev_filter.lower()]
    for inc in filtered:
        sev = str(inc.get("severity", "low")).lower()
        css = f"incident-{sev}" if sev in ("critical","high","medium","low") else "incident-low"
        inc_id = inc.get("incident_id", inc.get("id", "?"))
        svc = inc.get("service", "?")
        score = inc.get("score", "N/A")
        auto_fix = inc.get("auto_fix_command", "")
        manual_fix = inc.get("manual_fix_command", inc.get("recommended_action", ""))
        rem_status = inc.get("remediation_status", "")
        rc = inc.get("probable_root_cause", "")

        with st.container():
            st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
            cols = st.columns([4,1,1,1,1])
            with cols[0]:
                st.markdown(f"**{inc_id}** — {svc}")
                if rc:
                    st.caption(rc[:120] + "..." if len(rc) > 120 else rc)
            with cols[1]:
                st.markdown(f"Score: **{score}**")
            with cols[2]:
                st.markdown(f"Sev: **{inc.get('severity','?')}**")
            with cols[3]:
                st.markdown(f"Ev: {inc.get('event_count', '?')}")
            with cols[4]:
                flags = []
                if inc.get("has_deploy"): flags.append("🚀")
                if inc.get("has_security"): flags.append("🔒")
                if inc.get("has_alert"): flags.append("⚠️")
                st.markdown(" ".join(flags) if flags else "&nbsp;")

            with st.expander(f"View Report & Fixes — {inc_id}"):
                tabs_detail = st.tabs(["Report", "Fixes", "Policy", "Evidence"])
                with tabs_detail[0]:
                    st.markdown(f"**Root Cause:** {rc or 'Not identified'}")
                    st.markdown(f"**Status:** {inc.get('status', 'open')}")
                    st.markdown(f"**Score:** {score} — {'✅ Auto-remediate' if inc.get('auto_remediate') else '❌ Requires approval'}")
                    st.markdown(f"**Autonomy Level:** {inc.get('autonomy_level', 'N/A')}")
                    if inc.get("llm_reasoning"):
                        with st.expander("LLM Analysis"):
                            st.caption(inc["llm_reasoning"])
                with tabs_detail[1]:
                    if auto_fix:
                        st.markdown("**🤖 Auto-Fix (executed by LIC):**")
                        st.code(auto_fix, language="bash")
                        if rem_status:
                            status_color = {"verified":"green","executed":"#ffc107","blocked_by_policy":"#e94560","blocked_by_safeguards":"#e94560","execution_failed":"#e94560"}
                            c = status_color.get(rem_status, "#888")
                            st.markdown(f"Status: <span style='color:{c}'>{rem_status}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("**🤖 Auto-Fix:** Not available")
                    if manual_fix:
                        st.markdown("**✋ Manual Fix (recommended):**")
                        st.info(manual_fix)
                    policy_dec = inc.get("policy_decision", {})
                    if policy_dec:
                        st.markdown(f"**Policy Decision:** `{policy_dec.get('decision','N/A')}` (Policy ID: `{policy_dec.get('policy_id','N/A')}`)")
                with tabs_detail[2]:
                    pol_decision = inc.get("policy_decision", {})
                    if pol_decision:
                        st.json(pol_decision)
                    elif inc.get("requires_human_approval"):
                        st.warning("Requires human approval")
                    else:
                        st.success("No policy restrictions")
                with tabs_detail[3]:
                    evidence = inc.get("evidence", [])
                    if evidence:
                        for ev in evidence[:10]:
                            st.markdown(f"- **{ev.get('metric','?')}**: {ev.get('value','?')}")
                    else:
                        st.caption("No evidence recorded")

            st.markdown('</div>', unsafe_allow_html=True)

# ── TAB 3: Triage ──
with tab_triages:
    st.subheader(f"Triage Results ({len(triages)})")
    for t in triages[:20]:
        sev = str(t.get("severity", "low")).lower()
        css = f"incident-{sev}" if sev in ("critical","high","medium","low") else "incident-low"
        svc = t.get("service", "?")
        with st.container():
            st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
            st.markdown(f"**{svc}** — *{t.get('root_cause', t.get('llm_reasoning','')[:120] + '...' if t.get('llm_reasoning') else 'No root cause identified')}*")
            fix = t.get("suggested_fix", t.get("fix_command", "None"))
            if fix and fix != "None":
                st.code(fix, language="bash")
            if t.get("escalated"):
                st.error(f"Escalated: {t.get('escalation_reason','')}")
            st.markdown('</div>', unsafe_allow_html=True)

# ── TAB 4: Reports ──
with tab_reports:
    st.subheader(f"Post-Incident Reports ({len(reports)})")
    for r in reports[:10]:
        rid = r.get("incident_id", r.get("id", "unknown"))
        title = r.get("title", r.get("summary", ""))
        with st.expander(f"PIR: {rid} — {title}"):
            st.json(r)

# ── TAB 5: Rules (Pattern Learner + OpenClaw) ──
with tab_rules:
    st.subheader("🤖 OpenClaw Pattern Learner")
    st.markdown("The agent analyzes incident patterns and suggests policy rules. Adopt suggestions to create OpenClaw-enforced runbooks.")

    try:
        import sys
        sys.path.insert(0, SRC_DIR)
        from pattern_learner import detect_patterns, adopt_rule, reject_suggestion, get_learned_rules
        import yaml
    except ImportError as e:
        st.warning(f"Pattern learner not available: {e}")
        st.stop()

    col_refresh, col_reset = st.columns([1,1])
    with col_refresh:
        if st.button("🔄 Scan for New Patterns"):
            rules_data = get_learned_rules()
            st.success(f"Scan complete. {len(rules_data.get('suggestions',[]))} new pattern(s) found.")
    with col_reset:
        if st.button("🗑️ Reset Learned Rules"):
            from pattern_learner import reset_learned_rules
            reset_learned_rules()
            st.success("Learned rules reset.")

    rules_data = get_learned_rules()

    if rules_data.get("rules"):
        st.subheader("✅ Adopted Rules")
        for rule in rules_data["rules"]:
            with st.container():
                st.markdown(f"""
                <div style="background:#0d2818; border-left:4px solid #4caf50; padding:10px; margin:5px 0; border-radius:5px;">
                    <strong style="color:#4caf50;">ACTIVE</strong> — <code>{rule.get('policy_id','')}</code><br>
                    <b>If:</b> {rule.get('service','?')} / {rule.get('action','?')}<br>
                    <b>Profile:</b> {rule.get('profile','hardened')} · Autonomy: {rule.get('autonomy_level',3)} · Score: ≥{rule.get('score_threshold',0)}
                </div>
                """, unsafe_allow_html=True)

    if rules_data.get("suggestions"):
        st.subheader("💡 Pattern-Based Rule Suggestions")
        st.markdown("These patterns were detected repeatedly. Adopt to create a permanent rule.")
        for s in rules_data["suggestions"]:
            with st.container():
                st.markdown(f'<div class="suggestion-card">', unsafe_allow_html=True)
                cols = st.columns([3,1,1])
                with cols[0]:
                    st.markdown(f"**{s['service']}** — {s['event_types']}")
                    st.markdown(f"Occurred **{s['occurrences']}x** · Suggest action: **`{s['action']}`**")
                    st.markdown(f"Rule: `{s['suggested_rule']['if']}` → `{s['suggested_rule']['then']}`")
                with cols[1]:
                    if st.button(f"✅ Adopt", key=f"adopt-{s['pattern_key']}"):
                        if adopt_rule(s["pattern_key"]):
                            st.success("Rule adopted! OpenClaw will enforce it.")
                            st.rerun()
                with cols[2]:
                    if st.button(f"❌ Reject", key=f"reject-{s['pattern_key']}"):
                        if reject_suggestion(s["pattern_key"]):
                            st.info("Suggestion dismissed.")
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # Show raw rules file
    if os.path.exists("learned_rules.yaml"):
        st.subheader("📄 learned_rules.yaml")
        with open("learned_rules.yaml") as f:
            st.code(f.read(), language="yaml")

# ── TAB 6: Cost ──
with tab_cost:
    st.subheader("Cost Savings Report")
    if costs:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Savings", f"${costs.get('total_saved', 0):,.2f}")
        with c2:
            st.metric("Annual Projected", f"${costs.get('annual_projected_savings', 0):,.2f}")
        with c3:
            st.metric("Events Processed", f"{costs.get('total_events_processed', 0):,}")
        with c4:
            st.metric("Actions Blocked", costs.get('total_actions_blocked', 0))

        c5, c6, c7, c8 = st.columns(4)
        with c5:
            st.metric("Engineer Hours Saved", f"{costs.get('engineer_hours_saved', 0):.1f}")
        with c6:
            st.metric("MTTR Saved (min)", f"{costs.get('mttr_saved_minutes', 0):,.0f}")
        with c7:
            st.metric("Downtime Cost Avoided", f"${costs.get('downtime_cost_saved', 0):,.2f}")
        with c8:
            st.metric("Cloud API Cost Avoided", f"${costs.get('cloud_api_cost_saved', 0):,.2f}")

        st.subheader("Savings Breakdown")
        breakdown = pd.DataFrame({
            "Category": ["Splunk", "PagerDuty", "Cloud API", "Downtime Avoided"],
            "Amount": [
                costs.get("splunk_cost_saved", 0),
                costs.get("pagerduty_cost_saved", 0),
                costs.get("cloud_api_cost_saved", 0),
                costs.get("downtime_cost_saved", 0),
            ]
        })
        fig = px.bar(breakdown, x="Category", y="Amount", title="Cost Savings by Category",
                     color="Category", color_discrete_sequence=["#e94560", "#ff6b35", "#ffc107", "#4caf50"])
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    blocked_list = costs.get("blocked_actions", [])
    if blocked_list:
        st.subheader("Policy Denials")
        st.markdown(f"**{costs.get('total_actions_blocked', 0)} actions blocked by policy** — kernel-enforced, not Slack-approved")
        df_blocked = pd.DataFrame(blocked_list)
        if "timestamp" in df_blocked.columns and "action" in df_blocked.columns:
            df_blocked["time"] = df_blocked["timestamp"].str[11:19]
            fig2 = px.line(df_blocked, x="time", y=[1]*len(df_blocked), title="Policy Denials Over Time",
                          markers=True)
            fig2.update_yaxes(visible=False)
            st.plotly_chart(fig2, use_container_width=True)

        for b in blocked_list[-15:]:
            pid = b.get("policy_id", "?")
            action = b.get("action", "?")
            reason = b.get("reason", "?")
            ts = b.get("timestamp", "?")[11:19] if len(b.get("timestamp", "")) > 19 else b.get("timestamp", "?")
            st.markdown(f"""
            <div class="blocked-card">
                <strong style="color:#e94560;">DENIED</strong> <span style="color:#888;">{ts}</span><br>
                <code>{action}</code> → Policy ID: <code>{pid}</code><br>
                <span style="color:#aaa;">{reason}</span>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("Local Incident Commander · Dell x NVIDIA GB10 · Sovereign by default · Deterministic by design · Governed at the kernel boundary")

time.sleep(2)
st.rerun()
