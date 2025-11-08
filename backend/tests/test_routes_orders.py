"""Tests for procurement order management API."""

from datetime import timedelta

import pytest

from models import get_current_time


@pytest.fixture
def create_order(client, auth_headers):
    def _create(**overrides):
        payload = {
            "title": overrides.get("title", "Hydraulic Pump"),
            "order_type": overrides.get("order_type", "tool"),
            "priority": overrides.get("priority", "normal"),
            "expected_due_date": (get_current_time() + timedelta(days=5)).isoformat(),
            "description": overrides.get("description", "Replacement hydraulic pump"),
        }
        payload.update(overrides)
        response = client.post("/api/orders", json=payload, headers=auth_headers)
        assert response.status_code == 201
        return response.get_json()

    return _create


class TestOrderRoutes:
    def test_create_and_list_orders(self, client, auth_headers, create_order):
        order = create_order(title="Torque Wrench", order_type="tool")

        response = client.get("/api/orders", headers=auth_headers)
        assert response.status_code == 200
        results = response.get_json()
        assert any(item["id"] == order["id"] for item in results)

    def test_update_order(self, client, auth_headers, create_order):
        order = create_order(order_type="chemical", priority="high")
        order_id = order["id"]

        new_due_date = (get_current_time() + timedelta(days=10)).isoformat()
        update_payload = {
            "status": "ordered",
            "expected_due_date": new_due_date,
            "tracking_number": "1Z999",
            "reference_number": "PO-12345",
            "notes": "Vendor confirmed shipment",
        }

        response = client.put(f"/api/orders/{order_id}", json=update_payload, headers=auth_headers)
        assert response.status_code == 200
        updated = response.get_json()
        assert updated["status"] == "ordered"
        assert updated["tracking_number"] == "1Z999"
        assert updated["reference_number"] == "PO-12345"
        assert updated["notes"] == "Vendor confirmed shipment"

    def test_order_analytics(self, client, auth_headers):
        now = get_current_time()
        future_due = (now + timedelta(days=2)).isoformat()
        past_due = (now - timedelta(days=2)).isoformat()

        for status, due_date in [("new", future_due), ("ordered", past_due), ("shipped", future_due)]:
            payload = {
                "title": f"Order {status}",
                "order_type": "tool",
                "status": status,
                "expected_due_date": due_date,
            }
            resp = client.post("/api/orders", json=payload, headers=auth_headers)
            assert resp.status_code == 201

        analytics_resp = client.get("/api/orders/analytics", headers=auth_headers)
        assert analytics_resp.status_code == 200
        analytics = analytics_resp.get_json()
        assert analytics["total_open"] >= 3
        assert analytics["late_count"] >= 1
        assert analytics["status_breakdown"]
        assert analytics["type_breakdown"]

    def test_late_order_alerts(self, client, auth_headers):
        late_due = (get_current_time() - timedelta(days=1)).isoformat()
        payload = {
            "title": "Overdue Order",
            "expected_due_date": late_due,
        }
        resp = client.post("/api/orders", json=payload, headers=auth_headers)
        assert resp.status_code == 201

        alerts_resp = client.get("/api/orders/late-alerts", headers=auth_headers)
        assert alerts_resp.status_code == 200
        alerts = alerts_resp.get_json()
        assert any(alert["title"] == "Overdue Order" for alert in alerts)

    def test_requests_user_can_create_order(self, client, auth_headers_requests_user):
        payload = {
            "title": "Line maintenance drill",
            "order_type": "tool",
            "priority": "high",
            "status": "ordered",  # should be forced to "new" for request-only users
            "quantity": 2,
            "unit": "each",
        }

        response = client.post("/api/orders", json=payload, headers=auth_headers_requests_user)
        assert response.status_code == 201
        order = response.get_json()
        assert order["status"] == "new"
        assert order["quantity"] == 2
        assert order["unit"] == "each"

    def test_requests_user_list_restricted_to_self(
        self,
        client,
        auth_headers,
        auth_headers_requests_user,
    ):
        create_resp = client.post(
            "/api/orders",
            json={"title": "Self submitted", "order_type": "expendable"},
            headers=auth_headers_requests_user,
        )
        assert create_resp.status_code == 201
        own_order = create_resp.get_json()

        other_resp = client.post(
            "/api/orders",
            json={"title": "Admin order", "order_type": "tool"},
            headers=auth_headers,
        )
        assert other_resp.status_code == 201

        list_resp = client.get("/api/orders", headers=auth_headers_requests_user)
        assert list_resp.status_code == 200
        results = list_resp.get_json()
        assert any(order["id"] == own_order["id"] for order in results)
        assert all(order["title"] != "Admin order" for order in results)

    def test_order_messages_workflow(
        self,
        client,
        auth_headers,
        user_auth_headers,
        regular_user,
    ):
        due_date = (get_current_time() + timedelta(days=7)).isoformat()
        create_resp = client.post(
            "/api/orders",
            json={
                "title": "Kit Restock",
                "order_type": "expendable",
                "expected_due_date": due_date,
                "requester_id": regular_user.id,
            },
            headers=auth_headers,
        )
        assert create_resp.status_code == 201
        order = create_resp.get_json()

        message_resp = client.post(
            f"/api/orders/{order['id']}/messages",
            json={"subject": "Need confirmation", "message": "Please confirm part number."},
            headers=auth_headers,
        )
        assert message_resp.status_code == 201
        message = message_resp.get_json()
        assert message["recipient_id"] == regular_user.id

        list_resp = client.get(
            f"/api/orders/{order['id']}/messages",
            headers=user_auth_headers,
        )
        assert list_resp.status_code == 200
        messages = list_resp.get_json()
        assert any(m["id"] == message["id"] for m in messages)

        reply_resp = client.post(
            f"/api/orders/messages/{message['id']}/reply",
            json={"message": "Confirmed, proceed."},
            headers=user_auth_headers,
        )
        assert reply_resp.status_code == 201
        reply = reply_resp.get_json()
        assert reply["parent_message_id"] == message["id"]

        mark_resp = client.put(
            f"/api/orders/messages/{reply['id']}/read",
            headers=auth_headers,
        )
        assert mark_resp.status_code == 200
        marked = mark_resp.get_json()
        assert marked["is_read"] is True


class TestOrderAccessControl:
    def test_requester_can_view_without_permission(
        self,
        client,
        create_order,
        regular_user,
        jwt_manager,
        app,
    ):
        order = create_order(requester_id=regular_user.id)

        with app.app_context():
            tokens = jwt_manager.generate_tokens(regular_user)
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        response = client.get(f"/api/orders/{order['id']}", headers=headers)
        assert response.status_code == 200
        detail = response.get_json()
        assert detail["id"] == order["id"]

    def test_non_participant_without_permission_denied(
        self,
        client,
        create_order,
        user_auth_headers,
        regular_user,
        jwt_manager,
        app,
    ):
        order = create_order()

        with app.app_context():
            other_user_tokens = jwt_manager.generate_tokens(regular_user)
        headers = {"Authorization": f"Bearer {other_user_tokens['access_token']}"}

        response = client.get(f"/api/orders/{order['id']}", headers=headers)
        assert response.status_code == 403


class TestOrderFilters:
    def test_filter_by_status_and_priority(self, client, auth_headers):
        future_due = (get_current_time() + timedelta(days=4)).isoformat()

        client.post(
            "/api/orders",
            json={
                "title": "Filter Test",
                "status": "awaiting_info",
                "priority": "critical",
                "expected_due_date": future_due,
            },
            headers=auth_headers,
        )

        response = client.get(
            "/api/orders?status=awaiting_info&priority=critical",
            headers=auth_headers,
        )
        assert response.status_code == 200
        results = response.get_json()
        assert results
        assert all(item["status"] == "awaiting_info" for item in results)
        assert all(item["priority"] == "critical" for item in results)
