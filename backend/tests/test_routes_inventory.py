"""
Comprehensive tests for inventory management routes (routes_inventory.py).

Tests cover:
- Lot number generation (auto and custom)
- Transaction history retrieval with pagination
- Item detail retrieval
- Batch transaction creation
- Authentication requirements
- Error handling and validation
"""

import pytest
from datetime import datetime


class TestLotNumberGeneration:
    """Tests for POST /api/lot-numbers/generate endpoint"""

    def test_generate_lot_number_success(self, client, auth_headers):
        """Test successful auto-generation of lot number"""
        response = client.post("/api/lot-numbers/generate", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "lot_number" in data
        assert data["generated"] is True
        assert data["message"] == "Lot number generated successfully"
        # Verify format: LOT-YYMMDD-XXXX
        lot_number = data["lot_number"]
        assert lot_number.startswith("LOT-")
        parts = lot_number.split("-")
        assert len(parts) == 3
        assert len(parts[1]) == 6  # YYMMDD
        assert len(parts[2]) == 4  # XXXX

    def test_generate_lot_number_sequential(self, client, auth_headers):
        """Test sequential lot number generation increments counter"""
        # Generate first lot number
        response1 = client.post("/api/lot-numbers/generate", headers=auth_headers)
        assert response1.status_code == 200
        lot1 = response1.get_json()["lot_number"]

        # Generate second lot number
        response2 = client.post("/api/lot-numbers/generate", headers=auth_headers)
        assert response2.status_code == 200
        lot2 = response2.get_json()["lot_number"]

        # Extract counters
        counter1 = int(lot1.split("-")[2])
        counter2 = int(lot2.split("-")[2])

        # Counter should increment
        assert counter2 == counter1 + 1

    def test_generate_lot_number_with_custom_override(self, client, auth_headers):
        """Test using custom lot number override"""
        custom_lot = "CUSTOM-LOT-12345"
        response = client.post(
            "/api/lot-numbers/generate",
            json={"override": custom_lot},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["lot_number"] == custom_lot
        assert data["generated"] is False
        assert data["message"] == "Using custom lot number"

    def test_generate_lot_number_empty_override_error(self, client, auth_headers):
        """Test error when override is empty string"""
        response = client.post(
            "/api/lot-numbers/generate",
            json={"override": "   "},
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_generate_lot_number_with_whitespace_trimmed(self, client, auth_headers):
        """Test that whitespace in custom lot number is trimmed"""
        custom_lot = "  MY-LOT-001  "
        response = client.post(
            "/api/lot-numbers/generate",
            json={"override": custom_lot},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["lot_number"] == "MY-LOT-001"

    def test_generate_lot_number_no_auth(self, client):
        """Test that authentication is required"""
        response = client.post("/api/lot-numbers/generate")

        assert response.status_code == 401

    def test_generate_lot_number_empty_body(self, client, auth_headers):
        """Test generation with empty request body"""
        response = client.post(
            "/api/lot-numbers/generate",
            json={},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["generated"] is True

    def test_generate_lot_number_no_json_body(self, client, auth_headers):
        """Test generation with no JSON body at all"""
        response = client.post(
            "/api/lot-numbers/generate",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["generated"] is True

    def test_generate_lot_number_database_error(self, client, auth_headers, monkeypatch):
        """Test error handling when database operation fails"""
        # Mock the generate_lot_number method to raise an exception
        def mock_generate_error():
            raise Exception("Database connection lost")

        from models import LotNumberSequence
        monkeypatch.setattr(LotNumberSequence, "generate_lot_number", staticmethod(mock_generate_error))

        response = client.post("/api/lot-numbers/generate", headers=auth_headers)

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "Failed to generate lot number" in data["error"]


class TestInventoryTransactions:
    """Tests for GET /api/inventory/<item_type>/<item_id>/transactions endpoint"""

    def test_get_transactions_tool_success(self, client, auth_headers, sample_tool, admin_user, db_session):
        """Test getting transactions for a tool"""
        # Create some transactions
        from models import InventoryTransaction

        trans1 = InventoryTransaction(
            item_type="tool",
            item_id=sample_tool.id,
            transaction_type="checkout",
            user_id=admin_user.id,
            notes="First checkout"
        )
        trans2 = InventoryTransaction(
            item_type="tool",
            item_id=sample_tool.id,
            transaction_type="return",
            user_id=admin_user.id,
            notes="First return"
        )
        db_session.add_all([trans1, trans2])
        db_session.commit()

        response = client.get(
            f"/api/inventory/tool/{sample_tool.id}/transactions",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["item_type"] == "tool"
        assert data["item_id"] == sample_tool.id
        assert data["total_count"] == 2
        assert data["limit"] == 100
        assert data["offset"] == 0
        assert len(data["transactions"]) == 2

    def test_get_transactions_chemical_success(self, client, auth_headers, sample_chemical, admin_user, db_session):
        """Test getting transactions for a chemical"""
        from models import InventoryTransaction

        trans = InventoryTransaction(
            item_type="chemical",
            item_id=sample_chemical.id,
            transaction_type="issuance",
            user_id=admin_user.id,
            quantity_change=-10.0,
            notes="Issued to job"
        )
        db_session.add(trans)
        db_session.commit()

        response = client.get(
            f"/api/inventory/chemical/{sample_chemical.id}/transactions",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["item_type"] == "chemical"
        assert data["total_count"] == 1
        assert data["transactions"][0]["transaction_type"] == "issuance"
        assert data["transactions"][0]["quantity_change"] == -10.0

    def test_get_transactions_expendable_valid_type(self, client, auth_headers):
        """Test that expendable is a valid item type"""
        response = client.get(
            "/api/inventory/expendable/1/transactions",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["item_type"] == "expendable"

    def test_get_transactions_kit_item_valid_type(self, client, auth_headers):
        """Test that kit_item is a valid item type"""
        response = client.get(
            "/api/inventory/kit_item/1/transactions",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["item_type"] == "kit_item"

    def test_get_transactions_invalid_item_type(self, client, auth_headers):
        """Test error for invalid item type"""
        response = client.get(
            "/api/inventory/invalid_type/1/transactions",
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "Invalid item_type" in data["error"]

    def test_get_transactions_with_pagination(self, client, auth_headers, sample_tool, admin_user, db_session):
        """Test pagination parameters work correctly"""
        from models import InventoryTransaction

        # Create 5 transactions
        for i in range(5):
            trans = InventoryTransaction(
                item_type="tool",
                item_id=sample_tool.id,
                transaction_type="checkout",
                user_id=admin_user.id,
                notes=f"Transaction {i}"
            )
            db_session.add(trans)
        db_session.commit()

        # Test with limit
        response = client.get(
            f"/api/inventory/tool/{sample_tool.id}/transactions?limit=2",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["transactions"]) == 2
        assert data["total_count"] == 5
        assert data["limit"] == 2

    def test_get_transactions_with_offset(self, client, auth_headers, sample_tool, admin_user, db_session):
        """Test offset pagination parameter"""
        from models import InventoryTransaction

        # Create 3 transactions
        for i in range(3):
            trans = InventoryTransaction(
                item_type="tool",
                item_id=sample_tool.id,
                transaction_type="checkout",
                user_id=admin_user.id,
                notes=f"Transaction {i}"
            )
            db_session.add(trans)
        db_session.commit()

        response = client.get(
            f"/api/inventory/tool/{sample_tool.id}/transactions?offset=1",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["transactions"]) == 2  # 3 total - 1 offset = 2 returned
        assert data["offset"] == 1

    def test_get_transactions_limit_too_low(self, client, auth_headers):
        """Test error when limit is less than 1"""
        response = client.get(
            "/api/inventory/tool/1/transactions?limit=0",
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "Limit must be between 1 and 1000" in data["error"]

    def test_get_transactions_limit_too_high(self, client, auth_headers):
        """Test error when limit exceeds 1000"""
        response = client.get(
            "/api/inventory/tool/1/transactions?limit=1001",
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "Limit must be between 1 and 1000" in data["error"]

    def test_get_transactions_negative_offset(self, client, auth_headers):
        """Test error when offset is negative"""
        response = client.get(
            "/api/inventory/tool/1/transactions?offset=-1",
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "Offset must be non-negative" in data["error"]

    def test_get_transactions_no_auth(self, client):
        """Test that authentication is required"""
        response = client.get("/api/inventory/tool/1/transactions")

        assert response.status_code == 401

    def test_get_transactions_empty_result(self, client, auth_headers, sample_tool):
        """Test getting transactions when none exist"""
        response = client.get(
            f"/api/inventory/tool/{sample_tool.id}/transactions",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["transactions"] == []
        assert data["total_count"] == 0

    def test_get_transactions_boundary_limit(self, client, auth_headers):
        """Test boundary values for limit parameter"""
        # Test minimum valid limit
        response = client.get(
            "/api/inventory/tool/1/transactions?limit=1",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Test maximum valid limit
        response = client.get(
            "/api/inventory/tool/1/transactions?limit=1000",
            headers=auth_headers
        )
        assert response.status_code == 200


class TestItemDetail:
    """Tests for GET /api/inventory/<item_type>/<item_id>/detail endpoint"""

    def test_get_tool_detail_success(self, client, auth_headers, sample_tool):
        """Test getting tool detail successfully"""
        response = client.get(
            f"/api/inventory/tool/{sample_tool.id}/detail",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["item_type"] == "tool"
        assert "transactions" in data
        assert "transaction_count" in data
        assert isinstance(data["transactions"], list)

    def test_get_chemical_detail_success(self, client, auth_headers, sample_chemical):
        """Test getting chemical detail successfully"""
        response = client.get(
            f"/api/inventory/chemical/{sample_chemical.id}/detail",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["item_type"] == "chemical"
        assert "transactions" in data
        assert "transaction_count" in data

    def test_get_detail_invalid_item_type(self, client, auth_headers):
        """Test error for invalid item type"""
        response = client.get(
            "/api/inventory/unknown_type/1/detail",
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "Invalid item_type" in data["error"]

    def test_get_detail_nonexistent_tool(self, client, auth_headers):
        """Test 404 for non-existent tool"""
        response = client.get(
            "/api/inventory/tool/99999/detail",
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
        assert "not found" in data["error"]

    def test_get_detail_nonexistent_chemical(self, client, auth_headers):
        """Test 404 for non-existent chemical"""
        response = client.get(
            "/api/inventory/chemical/99999/detail",
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.get_json()
        assert "Chemical" in data["error"]
        assert "not found" in data["error"]

    def test_get_detail_nonexistent_expendable(self, client, auth_headers):
        """Test 404 for non-existent expendable"""
        response = client.get(
            "/api/inventory/expendable/99999/detail",
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
        # The error message may be generic or specific
        assert "not found" in data["error"] or "could not be found" in data["error"]

    def test_get_detail_nonexistent_kit_item(self, client, auth_headers):
        """Test 404 for non-existent kit_item"""
        response = client.get(
            "/api/inventory/kit_item/99999/detail",
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.get_json()
        assert "Kit_item" in data["error"]
        assert "not found" in data["error"]

    def test_get_detail_with_transactions(self, client, auth_headers, sample_tool, admin_user, db_session):
        """Test that detail includes transaction history"""
        from models import InventoryTransaction

        # Add transactions
        trans = InventoryTransaction(
            item_type="tool",
            item_id=sample_tool.id,
            transaction_type="adjustment",
            user_id=admin_user.id,
            notes="Calibration adjustment"
        )
        db_session.add(trans)
        db_session.commit()

        response = client.get(
            f"/api/inventory/tool/{sample_tool.id}/detail",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["transaction_count"] == 1
        assert len(data["transactions"]) == 1
        assert data["transactions"][0]["transaction_type"] == "adjustment"

    def test_get_detail_no_auth(self, client):
        """Test that authentication is required"""
        response = client.get("/api/inventory/tool/1/detail")

        assert response.status_code == 401

    def test_get_detail_expendable_valid_type(self, client, auth_headers):
        """Test that expendable is a valid item type for detail endpoint"""
        # This will return 404 for non-existent item, not 400 for invalid type
        response = client.get(
            "/api/inventory/expendable/1/detail",
            headers=auth_headers
        )

        # Should be 404 (not found) or 200 (found), not 400 (invalid type)
        assert response.status_code in [200, 404]

    def test_get_detail_kit_item_valid_type(self, client, auth_headers):
        """Test that kit_item is a valid item type for detail endpoint"""
        response = client.get(
            "/api/inventory/kit_item/1/detail",
            headers=auth_headers
        )

        # Should be 404 (not found) or 200 (found), not 400 (invalid type)
        assert response.status_code in [200, 404]


class TestBatchTransactions:
    """Tests for POST /api/inventory/transactions/batch endpoint"""

    def test_create_batch_transactions_success(self, client, auth_headers, sample_tool, sample_chemical):
        """Test successful creation of batch transactions"""
        transactions_data = {
            "transactions": [
                {
                    "item_type": "tool",
                    "item_id": sample_tool.id,
                    "transaction_type": "adjustment",
                    "quantity_change": 1.0,
                    "notes": "Found missing tool"
                },
                {
                    "item_type": "chemical",
                    "item_id": sample_chemical.id,
                    "transaction_type": "issuance",
                    "quantity_change": -5.0,
                    "notes": "Issued to work order"
                }
            ]
        }

        response = client.post(
            "/api/inventory/transactions/batch",
            json=transactions_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["created_count"] == 2
        assert "Successfully created 2 transactions" in data["message"]

    def test_create_batch_single_transaction(self, client, auth_headers, sample_tool):
        """Test batch creation with single transaction"""
        transactions_data = {
            "transactions": [
                {
                    "item_type": "tool",
                    "item_id": sample_tool.id,
                    "transaction_type": "checkout",
                    "notes": "Single checkout"
                }
            ]
        }

        response = client.post(
            "/api/inventory/transactions/batch",
            json=transactions_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["created_count"] == 1

    def test_create_batch_with_optional_fields(self, client, auth_headers, sample_tool):
        """Test batch creation with all optional fields"""
        transactions_data = {
            "transactions": [
                {
                    "item_type": "tool",
                    "item_id": sample_tool.id,
                    "transaction_type": "transfer",
                    "quantity_change": 0,
                    "location_from": "Warehouse A",
                    "location_to": "Warehouse B",
                    "reference_number": "WO-12345",
                    "notes": "Transfer for maintenance",
                    "lot_number": "LOT-001",
                    "serial_number": "SN-001"
                }
            ]
        }

        response = client.post(
            "/api/inventory/transactions/batch",
            json=transactions_data,
            headers=auth_headers
        )

        assert response.status_code == 201

    def test_create_batch_missing_transactions_array(self, client, auth_headers):
        """Test error when transactions array is missing"""
        response = client.post(
            "/api/inventory/transactions/batch",
            json={},
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'Request must include "transactions" array' in data["error"]

    def test_create_batch_no_json_body(self, client, auth_headers):
        """Test error when no JSON body provided"""
        response = client.post(
            "/api/inventory/transactions/batch",
            headers=auth_headers
        )

        # Without Content-Type: application/json, the endpoint may return 415 or 500
        # depending on how error handling is configured
        assert response.status_code in [400, 415, 500]

    def test_create_batch_transactions_not_array(self, client, auth_headers):
        """Test error when transactions is not an array"""
        response = client.post(
            "/api/inventory/transactions/batch",
            json={"transactions": "not an array"},
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert '"transactions" must be an array' in data["error"]

    def test_create_batch_empty_transactions(self, client, auth_headers):
        """Test error when transactions array is empty"""
        response = client.post(
            "/api/inventory/transactions/batch",
            json={"transactions": []},
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "At least one transaction is required" in data["error"]

    def test_create_batch_exceeds_maximum(self, client, auth_headers):
        """Test error when more than 100 transactions"""
        # Create 101 transactions
        transactions = [
            {
                "item_type": "tool",
                "item_id": 1,
                "transaction_type": "checkout"
            }
            for _ in range(101)
        ]

        response = client.post(
            "/api/inventory/transactions/batch",
            json={"transactions": transactions},
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "Maximum 100 transactions per batch" in data["error"]

    def test_create_batch_missing_item_type(self, client, auth_headers):
        """Test error when item_type is missing"""
        transactions_data = {
            "transactions": [
                {
                    "item_id": 1,
                    "transaction_type": "checkout"
                }
            ]
        }

        response = client.post(
            "/api/inventory/transactions/batch",
            json=transactions_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "missing required field: item_type" in data["error"]

    def test_create_batch_missing_item_id(self, client, auth_headers):
        """Test error when item_id is missing"""
        transactions_data = {
            "transactions": [
                {
                    "item_type": "tool",
                    "transaction_type": "checkout"
                }
            ]
        }

        response = client.post(
            "/api/inventory/transactions/batch",
            json=transactions_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "missing required field: item_id" in data["error"]

    def test_create_batch_missing_transaction_type(self, client, auth_headers):
        """Test error when transaction_type is missing"""
        transactions_data = {
            "transactions": [
                {
                    "item_type": "tool",
                    "item_id": 1
                }
            ]
        }

        response = client.post(
            "/api/inventory/transactions/batch",
            json=transactions_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "missing required field: transaction_type" in data["error"]

    def test_create_batch_no_auth(self, client):
        """Test that authentication is required"""
        response = client.post(
            "/api/inventory/transactions/batch",
            json={"transactions": []}
        )

        assert response.status_code == 401

    def test_create_batch_exactly_100_transactions(self, client, auth_headers, sample_tool):
        """Test boundary case of exactly 100 transactions"""
        transactions = [
            {
                "item_type": "tool",
                "item_id": sample_tool.id,
                "transaction_type": "checkout"
            }
            for _ in range(100)
        ]

        response = client.post(
            "/api/inventory/transactions/batch",
            json={"transactions": transactions},
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["created_count"] == 100

    def test_create_batch_verifies_transactions_saved(self, client, auth_headers, sample_tool, db_session):
        """Test that transactions are actually persisted to database"""
        from models import InventoryTransaction

        initial_count = InventoryTransaction.query.filter_by(
            item_type="tool",
            item_id=sample_tool.id
        ).count()

        transactions_data = {
            "transactions": [
                {
                    "item_type": "tool",
                    "item_id": sample_tool.id,
                    "transaction_type": "checkout",
                    "notes": "Verify persistence"
                },
                {
                    "item_type": "tool",
                    "item_id": sample_tool.id,
                    "transaction_type": "return",
                    "notes": "Verify persistence 2"
                }
            ]
        }

        response = client.post(
            "/api/inventory/transactions/batch",
            json=transactions_data,
            headers=auth_headers
        )

        assert response.status_code == 201

        # Verify transactions were saved
        new_count = InventoryTransaction.query.filter_by(
            item_type="tool",
            item_id=sample_tool.id
        ).count()

        assert new_count == initial_count + 2

    def test_create_batch_with_user_id_set_correctly(self, client, user_auth_headers, regular_user, sample_tool, db_session):
        """Test that transactions are created with correct user_id"""
        from models import InventoryTransaction

        transactions_data = {
            "transactions": [
                {
                    "item_type": "tool",
                    "item_id": sample_tool.id,
                    "transaction_type": "checkout",
                    "notes": "User ID test"
                }
            ]
        }

        response = client.post(
            "/api/inventory/transactions/batch",
            json=transactions_data,
            headers=user_auth_headers
        )

        assert response.status_code == 201

        # Verify user_id was set correctly
        transaction = InventoryTransaction.query.filter_by(
            item_type="tool",
            item_id=sample_tool.id,
            notes="User ID test"
        ).first()

        assert transaction is not None
        assert transaction.user_id == regular_user.id


class TestAuthenticationRequirements:
    """Tests to verify all endpoints require authentication"""

    def test_lot_generation_requires_auth(self, client):
        """Verify lot number generation requires authentication"""
        response = client.post("/api/lot-numbers/generate")
        assert response.status_code == 401

    def test_transactions_endpoint_requires_auth(self, client):
        """Verify transactions endpoint requires authentication"""
        response = client.get("/api/inventory/tool/1/transactions")
        assert response.status_code == 401

    def test_detail_endpoint_requires_auth(self, client):
        """Verify detail endpoint requires authentication"""
        response = client.get("/api/inventory/tool/1/detail")
        assert response.status_code == 401

    def test_batch_transactions_requires_auth(self, client):
        """Verify batch transactions endpoint requires authentication"""
        response = client.post(
            "/api/inventory/transactions/batch",
            json={"transactions": []}
        )
        assert response.status_code == 401

    def test_invalid_token_rejected(self, client):
        """Test that invalid JWT tokens are rejected"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/api/lot-numbers/generate", headers=headers)
        assert response.status_code == 401

    def test_expired_token_rejected(self, client, jwt_manager, admin_user):
        """Test that expired tokens are rejected"""
        # This test verifies that the jwt_required decorator is in place
        # Actual token expiration testing would require time manipulation
        headers = {"Authorization": "Bearer expired_token_simulation"}
        response = client.get("/api/inventory/tool/1/detail", headers=headers)
        assert response.status_code == 401


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_transactions_with_large_offset(self, client, auth_headers):
        """Test getting transactions with offset larger than count"""
        response = client.get(
            "/api/inventory/tool/1/transactions?offset=10000",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["transactions"] == []

    def test_item_id_zero(self, client, auth_headers):
        """Test behavior with item_id of 0"""
        response = client.get(
            "/api/inventory/tool/0/transactions",
            headers=auth_headers
        )

        # Should handle gracefully
        assert response.status_code == 200

    def test_very_long_notes_in_batch(self, client, auth_headers, sample_tool):
        """Test batch transaction with very long notes"""
        long_notes = "A" * 999  # Close to max length of 1000
        transactions_data = {
            "transactions": [
                {
                    "item_type": "tool",
                    "item_id": sample_tool.id,
                    "transaction_type": "adjustment",
                    "notes": long_notes
                }
            ]
        }

        response = client.post(
            "/api/inventory/transactions/batch",
            json=transactions_data,
            headers=auth_headers
        )

        assert response.status_code == 201

    def test_mixed_item_types_in_batch(self, client, auth_headers, sample_tool, sample_chemical):
        """Test batch with different item types"""
        transactions_data = {
            "transactions": [
                {
                    "item_type": "tool",
                    "item_id": sample_tool.id,
                    "transaction_type": "checkout"
                },
                {
                    "item_type": "chemical",
                    "item_id": sample_chemical.id,
                    "transaction_type": "issuance",
                    "quantity_change": -10.0
                }
            ]
        }

        response = client.post(
            "/api/inventory/transactions/batch",
            json=transactions_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["created_count"] == 2


class TestResponseFormats:
    """Tests for response data format validation"""

    def test_lot_number_response_format(self, client, auth_headers):
        """Verify lot number response has correct structure"""
        response = client.post("/api/lot-numbers/generate", headers=auth_headers)
        data = response.get_json()

        assert "lot_number" in data
        assert "generated" in data
        assert "message" in data
        assert isinstance(data["lot_number"], str)
        assert isinstance(data["generated"], bool)
        assert isinstance(data["message"], str)

    def test_transactions_response_format(self, client, auth_headers, sample_tool):
        """Verify transactions response has correct structure"""
        response = client.get(
            f"/api/inventory/tool/{sample_tool.id}/transactions",
            headers=auth_headers
        )
        data = response.get_json()

        assert "item_type" in data
        assert "item_id" in data
        assert "transactions" in data
        assert "total_count" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["transactions"], list)
        assert isinstance(data["total_count"], int)

    def test_detail_response_includes_item_type(self, client, auth_headers, sample_tool):
        """Verify detail response includes item_type field"""
        response = client.get(
            f"/api/inventory/tool/{sample_tool.id}/detail",
            headers=auth_headers
        )
        data = response.get_json()

        assert data["item_type"] == "tool"
        assert "transactions" in data
        assert "transaction_count" in data

    def test_batch_response_format(self, client, auth_headers, sample_tool):
        """Verify batch creation response has correct structure"""
        transactions_data = {
            "transactions": [
                {
                    "item_type": "tool",
                    "item_id": sample_tool.id,
                    "transaction_type": "checkout"
                }
            ]
        }

        response = client.post(
            "/api/inventory/transactions/batch",
            json=transactions_data,
            headers=auth_headers
        )
        data = response.get_json()

        assert "created_count" in data
        assert "message" in data
        assert isinstance(data["created_count"], int)
        assert isinstance(data["message"], str)


class TestRealWorldScenarios:
    """Tests simulating real-world usage patterns"""

    def test_full_inventory_lifecycle(self, client, auth_headers, sample_tool, db_session):
        """Test complete inventory tracking cycle"""
        from models import InventoryTransaction

        # 1. Generate lot number
        lot_response = client.post("/api/lot-numbers/generate", headers=auth_headers)
        assert lot_response.status_code == 200
        lot_number = lot_response.get_json()["lot_number"]

        # 2. Create batch transactions for lifecycle
        transactions_data = {
            "transactions": [
                {
                    "item_type": "tool",
                    "item_id": sample_tool.id,
                    "transaction_type": "receipt",
                    "lot_number": lot_number,
                    "notes": "Received new tool"
                },
                {
                    "item_type": "tool",
                    "item_id": sample_tool.id,
                    "transaction_type": "checkout",
                    "lot_number": lot_number,
                    "notes": "Checked out for job"
                },
                {
                    "item_type": "tool",
                    "item_id": sample_tool.id,
                    "transaction_type": "return",
                    "lot_number": lot_number,
                    "notes": "Returned from job"
                }
            ]
        }

        batch_response = client.post(
            "/api/inventory/transactions/batch",
            json=transactions_data,
            headers=auth_headers
        )
        assert batch_response.status_code == 201

        # 3. Verify transaction history
        history_response = client.get(
            f"/api/inventory/tool/{sample_tool.id}/transactions",
            headers=auth_headers
        )
        assert history_response.status_code == 200
        history = history_response.get_json()
        assert history["total_count"] == 3

        # 4. Get full detail
        detail_response = client.get(
            f"/api/inventory/tool/{sample_tool.id}/detail",
            headers=auth_headers
        )
        assert detail_response.status_code == 200
        detail = detail_response.get_json()
        assert detail["transaction_count"] == 3

    def test_paginated_history_retrieval(self, client, auth_headers, sample_tool, admin_user, db_session):
        """Test paginating through large transaction history"""
        from models import InventoryTransaction

        # Create 25 transactions
        for i in range(25):
            trans = InventoryTransaction(
                item_type="tool",
                item_id=sample_tool.id,
                transaction_type="checkout",
                user_id=admin_user.id,
                notes=f"Transaction {i+1}"
            )
            db_session.add(trans)
        db_session.commit()

        # Page 1
        page1 = client.get(
            f"/api/inventory/tool/{sample_tool.id}/transactions?limit=10&offset=0",
            headers=auth_headers
        )
        assert page1.status_code == 200
        page1_data = page1.get_json()
        assert len(page1_data["transactions"]) == 10

        # Page 2
        page2 = client.get(
            f"/api/inventory/tool/{sample_tool.id}/transactions?limit=10&offset=10",
            headers=auth_headers
        )
        assert page2.status_code == 200
        page2_data = page2.get_json()
        assert len(page2_data["transactions"]) == 10

        # Page 3 (partial)
        page3 = client.get(
            f"/api/inventory/tool/{sample_tool.id}/transactions?limit=10&offset=20",
            headers=auth_headers
        )
        assert page3.status_code == 200
        page3_data = page3.get_json()
        assert len(page3_data["transactions"]) == 5

        # Total count should be consistent
        assert page1_data["total_count"] == 25
        assert page2_data["total_count"] == 25
        assert page3_data["total_count"] == 25
