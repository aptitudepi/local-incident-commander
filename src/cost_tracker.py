import json
import math
from typing import Dict
from pathlib import Path

COST_FILE = "reports/metrics/costs.json"

SPLUNK_COST_PER_EVENT = 0.05
PAGERDUTY_COST_PER_INCIDENT = 30.0
CLOUD_API_COST_PER_CALL = 0.10
ENGINEER_HOURLY_RATE = 150.0
MTTR_SAVED_MINUTES = 45.0
DOWNTIME_COST_PER_MINUTE = 250.0


def _load_costs() -> Dict:
    path = Path(COST_FILE)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {
        "total_events_processed": 0,
        "total_incidents_resolved": 0,
        "cloud_api_calls_avoided": 0,
        "splunk_cost_saved": 0.0,
        "pagerduty_cost_saved": 0.0,
        "cloud_api_cost_saved": 0.0,
        "engineer_hours_saved": 0.0,
        "mttr_saved_minutes": 0.0,
        "downtime_cost_saved": 0.0,
        "annual_projected_savings": 0.0,
        "total_saved": 0.0,
    }


def _save_costs(costs: Dict):
    path = Path(COST_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)

    events = costs["total_events_processed"]
    incidents = costs["total_incidents_resolved"]

    engineer_hours = events / 4000
    mttr_saved = incidents * MTTR_SAVED_MINUTES
    downtime_saved = mttr_saved * DOWNTIME_COST_PER_MINUTE

    costs["splunk_cost_saved"] = round(events * SPLUNK_COST_PER_EVENT, 2)
    costs["pagerduty_cost_saved"] = round(incidents * PAGERDUTY_COST_PER_INCIDENT, 2)
    costs["cloud_api_cost_saved"] = round(events * CLOUD_API_COST_PER_CALL, 2)
    costs["engineer_hours_saved"] = round(engineer_hours, 1)
    costs["mttr_saved_minutes"] = round(mttr_saved, 0)
    costs["downtime_cost_saved"] = round(downtime_saved, 2)
    costs["annual_projected_savings"] = round(costs["total_saved"] * 12, 2)
    costs["total_saved"] = round(
        costs["splunk_cost_saved"]
        + costs["pagerduty_cost_saved"]
        + costs["cloud_api_cost_saved"]
        + downtime_saved,
        2,
    )

    with open(path, "w") as f:
        json.dump(costs, f, indent=2)


def record_events_processed(count: int):
    costs = _load_costs()
    costs["total_events_processed"] += count
    costs["cloud_api_calls_avoided"] += count
    _save_costs(costs)


def record_incident_resolved():
    costs = _load_costs()
    costs["total_incidents_resolved"] += 1
    _save_costs(costs)


def get_costs() -> Dict:
    return _load_costs()


def record_action_blocked(action: str, policy_id: str, reason: str):
    costs = _load_costs()
    costs.setdefault("total_actions_blocked", 0)
    costs["total_actions_blocked"] += 1
    costs.setdefault("blocked_actions", [])
    costs["blocked_actions"].append({
        "action": action,
        "policy_id": policy_id,
        "reason": reason,
        "timestamp": (
            __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat()
        ),
    })
    costs["blocked_actions"] = costs["blocked_actions"][-100:]
    _save_costs(costs)


def reset_costs():
    costs = {
        "total_events_processed": 0,
        "total_incidents_resolved": 0,
        "total_actions_blocked": 0,
        "cloud_api_calls_avoided": 0,
        "splunk_cost_saved": 0.0,
        "pagerduty_cost_saved": 0.0,
        "cloud_api_cost_saved": 0.0,
        "engineer_hours_saved": 0.0,
        "mttr_saved_minutes": 0.0,
        "downtime_cost_saved": 0.0,
        "annual_projected_savings": 0.0,
        "total_saved": 0.0,
        "blocked_actions": [],
    }
    _save_costs(costs)
