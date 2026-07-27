from src.ticketing import create_ticket, list_tickets, configure_webhook

def test_ticket_create():
    ticket = create_ticket({"id": "INC-001"}, {"root_cause": "test"}, {"success": False})
    assert ticket is not None
    assert "ticket_id" in ticket

def test_ticket_list():
    tickets = list_tickets()
    assert isinstance(tickets, list)
