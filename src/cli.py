import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def cmd_watch(args):
    from src.api_server import run_api_server
    print(json.dumps({"status": "starting", "service": "api_server", "port": 8080, "syslog_port": 5514}))
    run_api_server(http_port=args.port or 8080)


def cmd_correlate(args):
    from src.watcher import scan_directory, write_event_log
    from src.correlator import correlate, save_incident
    from src.cost_tracker import record_events_processed
    from src.severity import classify_severity
    from src.incident_report import build_incident_report, save_report
    from src.triage import triage
    from src.remediator import execute

    input_dir = args.input_dir or "inbox"
    events = scan_directory(input_dir)

    if not events:
        print(json.dumps({"status": "no_events", "input_dir": input_dir}))
        return

    for ev in events:
        write_event_log(ev)
    record_events_processed(len(events))

    incidents = correlate(events)
    enriched = []
    for inc in incidents:
        save_incident(inc)
        severity = classify_severity(inc)
        report = build_incident_report(inc, severity)
        triage_result = triage(report)
        report["auto_fix_command"] = triage_result.get("fix_command", "")
        report["manual_fix_command"] = report.get("recommended_action", "")
        remediation_result = execute(report, triage_result)
        report["remediation_status"] = remediation_result["status"]
        report["policy_decision"] = remediation_result.get("policy_decision", {})
        save_report(report)

        # Save triage result separately
        from pathlib import Path
        Path("reports").mkdir(exist_ok=True)
        with open(f"reports/triage_{report['incident_id']}.json", "w") as f:
            json.dump(triage_result, f, indent=2, default=str)

        # Save post-incident report separately
        pir = {
            "incident_id": report["incident_id"],
            "service": report["service"],
            "severity": report["severity"],
            "status": "resolved" if report["remediation_status"] == "verified" else report["remediation_status"],
            "score": report["score"],
            "auto_remediate": report["auto_remediate"],
            "auto_fix": report["auto_fix_command"],
            "manual_fix": report["manual_fix_command"],
            "root_cause": report["probable_root_cause"],
            "timestamp": report["timestamp"],
            "remediation_status": report["remediation_status"],
            "policy_decision": report.get("policy_decision", {}),
        }
        with open(f"reports/report_{report['incident_id']}.json", "w") as f:
            json.dump(pir, f, indent=2, default=str)

        enriched.append((inc, report))

    print(json.dumps({
        "status": "ok",
        "events_found": len(events),
        "incidents_created": len(incidents),
        "incidents": [
            {
                "incident_id": inc["incident_id"],
                "service": inc["service"],
                "event_count": inc["event_count"],
                "severity": report.get("severity", ""),
                "score": report.get("score", 0),
                "auto_fix": report.get("auto_fix_command", ""),
                "remediation_status": report.get("remediation_status", ""),
                "has_deploy": inc["has_deploy"],
                "has_alert": inc["has_alert"],
                "has_security": inc.get("has_security", False),
            }
            for inc, report in enriched
        ],
    }, indent=2))


def cmd_classify(args):
    from src.correlator import load_incident
    from src.severity import classify_severity

    incident = load_incident(args.incident_id)
    if incident is None:
        print(json.dumps({"error": f"Incident {args.incident_id} not found"}))
        return

    from src.incident_report import build_incident_report

    severity = classify_severity(incident)
    report = build_incident_report(incident, severity)
    from src.incident_report import save_report
    save_report(report)

    print(json.dumps({
        "status": "ok",
        "incident_id": args.incident_id,
        "severity": severity,
        "report": report,
    }, indent=2))


def cmd_brief(args):
    from src.correlator import load_incident
    from src.llm_brief import generate_brief

    incident = load_incident(args.incident_id)
    if incident is None:
        print(json.dumps({"error": f"Incident {args.incident_id} not found"}))
        return

    brief = generate_brief(incident)
    print(json.dumps({
        "status": "ok",
        "incident_id": args.incident_id,
        "brief": brief,
    }, indent=2))


def cmd_evaluate(args):
    from src.policy import evaluate
    decision = evaluate(args.action, args.resource, args.profile)
    print(json.dumps(decision, indent=2))


def cmd_triage(args):
    from src.correlator import load_incident
    from src.triage import triage

    incident = load_incident(args.incident_id)
    if incident is None:
        print(json.dumps({"error": f"Incident {args.incident_id} not found"}))
        return

    result = triage(incident)
    print(json.dumps(result, indent=2))


def cmd_remediate(args):
    from src.correlator import load_incident
    from src.triage import triage
    from src.remediator import execute

    incident = load_incident(args.incident_id)
    if incident is None:
        print(json.dumps({"error": f"Incident {args.incident_id} not found"}))
        return

    triage_result = triage(incident)
    remediation_result = execute(incident, triage_result, args.profile)
    print(json.dumps({
        "incident_id": args.incident_id,
        "triage": triage_result,
        "remediation": remediation_result,
    }, indent=2))


def cmd_escalate(args):
    from src.correlator import load_incident
    from src.triage import triage
    from src.remediator import execute
    from src.escalation import escalate

    incident = load_incident(args.incident_id)
    if incident is None:
        print(json.dumps({"error": f"Incident {args.incident_id} not found"}))
        return

    triage_result = triage(incident)
    remediation_result = execute(incident, triage_result)
    escalation_result = escalate(incident, triage_result, remediation_result)
    print(json.dumps(escalation_result, indent=2))


def cmd_demo(args):
    from src.watcher import scan_directory, write_event_log
    from src.correlator import correlate, save_incident, list_incidents
    from src.severity import classify_severity
    from src.incident_report import build_incident_report, save_report
    from src.triage import triage
    from src.remediator import execute
    from src.escalation import escalate
    from src.llm_brief import generate_brief
    from src.cost_tracker import record_events_processed, get_costs
    from src.monitor import collect_health
    from src.similarity import find_similar

    input_dir = args.input_dir or "sample_data"

    print(json.dumps({"phase": "ingest", "input_dir": input_dir}))
    events = scan_directory(input_dir)
    print(json.dumps({"phase": "ingest", "events_found": len(events)}))

    for ev in events:
        write_event_log(ev)
    record_events_processed(len(events))

    print(json.dumps({"phase": "correlate", "events": len(events)}))
    incidents = correlate(events)
    print(json.dumps({"phase": "correlate", "incidents_created": len(incidents)}))

    results = []
    for inc in incidents:
        save_incident(inc)
        severity = classify_severity(inc)
        report = build_incident_report(inc, severity)
        save_report(report)

        similar = find_similar(report)
        if similar:
            report["similar_incidents"] = similar

        print(json.dumps({"phase": "classify", "incident_id": inc["incident_id"], "severity": severity}))

        brief = generate_brief(report)
        print(json.dumps({"phase": "brief", "incident_id": inc["incident_id"], "brief": brief[:100] + "..."}))

        triage_result = triage(report)
        print(json.dumps({"phase": "triage", "incident_id": inc["incident_id"], "fix": triage_result["fix_command"]}))

        report["auto_fix_command"] = triage_result.get("fix_command", "")
        report["manual_fix_command"] = report.get("recommended_action", "")

        remediation_result = execute(report, triage_result)
        report["remediation_status"] = remediation_result["status"]
        report["policy_decision"] = remediation_result.get("policy_decision", {})
        save_report(report)
        print(json.dumps({"phase": "remediate", "incident_id": inc["incident_id"], "status": remediation_result["status"]}))

        if triage_result.get("escalated"):
            escalation_result = escalate(report, triage_result, remediation_result)
            print(json.dumps({"phase": "escalate", "incident_id": inc["incident_id"], "ticket": escalation_result.get("ticket_id")}))

        results.append({
            "incident_id": inc["incident_id"],
            "service": inc["service"],
            "severity": severity,
            "event_count": inc["event_count"],
            "root_cause": report["probable_root_cause"],
            "action": report["recommended_action"],
            "brief": brief,
            "triage": triage_result["fix_command"],
            "remediation_status": remediation_result["status"],
        })

    costs = get_costs()
    health = collect_health()

    print(json.dumps({
        "status": "complete",
        "events_processed": len(events),
        "incidents": len(incidents),
        "results": results,
        "costs": costs,
        "health": health,
    }, indent=2))


def cmd_cost(args):
    from src.cost_tracker import get_costs
    c = get_costs()
    print("=" * 54)
    print(f"  Local Incident Commander — Cost Savings Report")
    print("=" * 54)
    print(f"  Events processed:           {c['total_events_processed']:>8,}")
    print(f"  Incidents resolved:         {c['total_incidents_resolved']:>8,}")
    print(f"  Cloud API calls avoided:    {c['cloud_api_calls_avoided']:>8,}")
    print(f"  Actions blocked by policy:  {c.get('total_actions_blocked', 0):>8,}")
    print("-" * 54)
    print(f"  Splunk cost avoided:       ${c['splunk_cost_saved']:>8.2f}")
    print(f"  PagerDuty cost avoided:    ${c['pagerduty_cost_saved']:>8.2f}")
    print(f"  Cloud API cost avoided:    ${c['cloud_api_cost_saved']:>8.2f}")
    print(f"  Engineer hours saved:       {c['engineer_hours_saved']:>8.1f}")
    print(f"  MTTR saved (minutes):       {c['mttr_saved_minutes']:>8,.0f}")
    print(f"  Downtime cost avoided:     ${c['downtime_cost_saved']:>8,.2f}")
    print("=" * 54)
    print(f"  TOTAL SAVED:               ${c['total_saved']:>8,.2f}")
    print(f"  Annual projected:          ${c['annual_projected_savings']:>8,.2f}")
    print("=" * 54)
    if c.get("blocked_actions"):
        print()
        print(f"  Blocked Actions ({c['total_actions_blocked']} total):")
        for ba in c["blocked_actions"][-3:]:
            print(f"    · {ba['action']} → {ba['policy_id']}  ({ba['reason'][:60]})")


def cmd_health(args):
    from src.monitor import collect_health
    health = collect_health()
    print(json.dumps(health, indent=2))


def cmd_learn(args):
    from src.pattern_learner import detect_patterns, adopt_rule, reject_suggestion, get_learned_rules

    if args.adopt:
        if adopt_rule(args.adopt):
            print(f"✅ Rule adopted: {args.adopt}")
            print("   OpenClaw will enforce this rule on next scan.")
        else:
            print(f"❌ Could not adopt: {args.adopt} (not found)")
        return

    if args.reject:
        if reject_suggestion(args.reject):
            print(f"🗑️ Suggestion rejected: {args.reject}")
        else:
            print(f"❌ Could not reject: {args.reject} (not found)")
        return

    rules_data = get_learned_rules()

    if rules_data.get("rules"):
        print("\n✅ Adopted Rules:")
        print("-" * 50)
        for r in rules_data["rules"]:
            print(f"  · {r.get('policy_id','?')}: {r.get('service','?')} / {r.get('action','?')}")
            print(f"    Profile: {r.get('profile','hardened')} | Autonomy: {r.get('autonomy_level',3)}")

    if rules_data.get("suggestions"):
        print(f"\n💡 Pattern-Based Suggestions ({len(rules_data['suggestions'])}):")
        print("-" * 50)
        for s in rules_data["suggestions"]:
            print(f"  · {s['service']} ({s['occurrences']}x)")
            print(f"    Events: {s['event_types']}")
            print(f"    Rule: {s['suggested_rule']['if']} → {s['suggested_rule']['then']}")
            print(f"    Pattern key: {s['pattern_key']}")
            print()
        print("   Use: python -m src.cli learn --adopt <pattern_key>")
    else:
        print("\n💡 No new pattern suggestions. Run more incidents to generate them.")


def main():
    parser = argparse.ArgumentParser(description="Local Incident Commander")
    sub = parser.add_subparsers(dest="command")

    p_watch = sub.add_parser("watch", help="Run the API server and folder watcher")
    p_watch.add_argument("--port", type=int, default=8080)

    p_correlate = sub.add_parser("correlate", help="Correlate events from input directory")
    p_correlate.add_argument("--input-dir", default="inbox")

    p_classify = sub.add_parser("classify", help="Classify incident severity")
    p_classify.add_argument("--incident-id", required=True)

    p_brief = sub.add_parser("brief", help="Generate executive brief")
    p_brief.add_argument("--incident-id", required=True)

    p_evaluate = sub.add_parser("evaluate", help="Evaluate policy decision")
    p_evaluate.add_argument("--action", required=True)
    p_evaluate.add_argument("--resource", required=True)
    p_evaluate.add_argument("--profile", default="hardened", choices=["hardened", "insecure"])

    p_triage = sub.add_parser("triage", help="Auto-triage an incident")
    p_triage.add_argument("--incident-id", required=True)

    p_remediate = sub.add_parser("remediate", help="Auto-remediate an incident")
    p_remediate.add_argument("--incident-id", required=True)
    p_remediate.add_argument("--profile", default="hardened", choices=["hardened", "insecure"])

    p_escalate = sub.add_parser("escalate", help="Escalate an incident")
    p_escalate.add_argument("--incident-id", required=True)

    p_demo = sub.add_parser("demo", help="Run full demo pipeline")
    p_demo.add_argument("--input-dir", default="sample_data")

    p_cost = sub.add_parser("cost", help="Show cost tracker")

    p_health = sub.add_parser("health", help="Show LIC system health")

    p_learn = sub.add_parser("learn", help="Scan incidents and suggest policy rules")
    p_learn.add_argument("--adopt", help="Adopt a specific rule by pattern_key")
    p_learn.add_argument("--reject", help="Reject a suggestion by pattern_key")
    p_learn.add_argument("--list", action="store_true", help="List all suggestions")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return

    commands = {
        "watch": cmd_watch,
        "correlate": cmd_correlate,
        "classify": cmd_classify,
        "brief": cmd_brief,
        "evaluate": cmd_evaluate,
        "triage": cmd_triage,
        "remediate": cmd_remediate,
        "escalate": cmd_escalate,
        "demo": cmd_demo,
        "cost": cmd_cost,
        "health": cmd_health,
        "learn": cmd_learn,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
