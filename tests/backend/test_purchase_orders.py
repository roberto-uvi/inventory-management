"""
Tests for purchase order API endpoints (demo only, stored in memory).
"""
import pytest

from main import purchase_orders


@pytest.fixture(autouse=True)
def reset_purchase_orders():
    """POs live in a module-level list; clear it so tests don't leak state."""
    purchase_orders.clear()
    yield
    purchase_orders.clear()


@pytest.fixture
def po_payload():
    """Valid request body for backlog item '1'."""
    return {
        "backlog_item_id": "1",
        "supplier_name": "Acme Filters",
        "quantity": 350,
        "unit_cost": 12.5,
        "expected_delivery_date": "2025-12-01",
        "notes": "Rush order",
    }


class TestPurchaseOrderEndpoints:
    """Test suite for purchase order endpoints."""

    def test_create_purchase_order(self, client, po_payload):
        """Creating a PO returns 201 with server-filled fields."""
        response = client.post("/api/purchase-orders", json=po_payload)
        assert response.status_code == 201

        po = response.json()
        assert po["id"] == "PO-0001"
        assert po["status"] == "Pending"
        assert po["created_date"]
        for key, value in po_payload.items():
            assert po[key] == value

    def test_get_purchase_order_by_backlog_item(self, client, po_payload):
        """A created PO can be fetched by its backlog item ID."""
        created = client.post("/api/purchase-orders", json=po_payload).json()

        response = client.get("/api/purchase-orders/1")
        assert response.status_code == 200
        assert response.json() == created

    def test_backlog_flag_set_after_create(self, client, po_payload):
        """The backlog endpoint marks the item as having a PO."""
        client.post("/api/purchase-orders", json=po_payload)

        backlog = client.get("/api/backlog").json()
        flags = {item["id"]: item["has_purchase_order"] for item in backlog}
        assert flags["1"] is True
        assert not any(v for k, v in flags.items() if k != "1")

    def test_get_missing_purchase_order_returns_404(self, client):
        """Fetching a PO that doesn't exist returns 404."""
        response = client.get("/api/purchase-orders/1")
        assert response.status_code == 404

    def test_create_for_unknown_backlog_item_returns_404(self, client, po_payload):
        """A PO must reference an existing backlog item."""
        po_payload["backlog_item_id"] = "does-not-exist"
        response = client.post("/api/purchase-orders", json=po_payload)
        assert response.status_code == 404

    def test_duplicate_purchase_order_returns_409(self, client, po_payload):
        """Only one PO is allowed per backlog item."""
        client.post("/api/purchase-orders", json=po_payload)
        response = client.post("/api/purchase-orders", json=po_payload)
        assert response.status_code == 409

    @pytest.mark.parametrize("field,value", [("quantity", 0), ("quantity", -5), ("unit_cost", -1)])
    def test_invalid_amounts_return_400(self, client, po_payload, field, value):
        """Non-positive quantity or negative cost is rejected."""
        po_payload[field] = value
        response = client.post("/api/purchase-orders", json=po_payload)
        assert response.status_code == 400

    def test_missing_required_field_returns_422(self, client, po_payload):
        """Pydantic rejects a body missing a required field."""
        del po_payload["supplier_name"]
        response = client.post("/api/purchase-orders", json=po_payload)
        assert response.status_code == 422
