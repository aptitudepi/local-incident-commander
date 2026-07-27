from src.cost_tracker import get_costs, record_incident_resolved, reset_costs

def test_cost_tracker_initial():
    reset_costs()
    costs = get_costs()
    assert costs.get("total_saved") is not None

def test_cost_tracker_record():
    reset_costs()
    record_incident_resolved()
    costs = get_costs()
    assert costs["total_incidents_resolved"] > 0
