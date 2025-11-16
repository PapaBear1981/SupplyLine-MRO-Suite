"""
Tests for Chemical Management Routes

This module tests the chemical management endpoints including:
- CRUD operations for chemicals
- Chemical issuance and returns
- Reorder management
- Archive/unarchive functionality
- Barcode generation
"""

import json
from datetime import datetime, timedelta

import pytest

from models import Chemical, ChemicalIssuance, AuditLog, UserActivity, Warehouse


class TestChemicalListEndpoint:
    """Test the GET /api/chemicals endpoint"""

    def test_get_chemicals_empty(self, client):
        """Test getting chemicals when none exist"""
        response = client.get("/api/chemicals")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "chemicals" in data
        assert "pagination" in data
        assert isinstance(data["chemicals"], list)

    def test_get_chemicals_with_data(self, client, test_chemical):
        """Test getting chemicals with data"""
        response = client.get("/api/chemicals")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert len(data["chemicals"]) >= 1
        # Find our test chemical
        chemical_ids = [c["id"] for c in data["chemicals"]]
        assert test_chemical.id in chemical_ids

    def test_get_chemicals_pagination(self, client, db_session, test_warehouse):
        """Test chemicals pagination"""
        # Create multiple chemicals
        for i in range(25):
            chemical = Chemical(
                part_number=f"PNPAG{i:03d}",
                lot_number=f"LOTPAG{i:03d}",
                description=f"Pagination Test Chemical {i}",
                manufacturer="Test Manufacturer",
                quantity=100,
                unit="ml",
                location="Storage A",
                warehouse_id=test_warehouse.id
            )
            db_session.add(chemical)
        db_session.commit()

        # Test first page
        response = client.get("/api/chemicals?page=1&per_page=10")
        assert response.status_code == 200
        data = json.loads(response.data)

        assert len(data["chemicals"]) == 10
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["per_page"] == 10
        assert data["pagination"]["has_next"] is True

    def test_get_chemicals_filter_by_category(self, client, db_session, test_warehouse):
        """Test filtering chemicals by category"""
        # Create chemicals with different categories
        chemical1 = Chemical(
            part_number="PNCAT001",
            lot_number="LOTCAT001",
            description="Adhesive",
            manufacturer="Test",
            quantity=50,
            unit="ml",
            location="A",
            category="Adhesives",
            warehouse_id=test_warehouse.id
        )
        chemical2 = Chemical(
            part_number="PNCAT002",
            lot_number="LOTCAT002",
            description="Lubricant",
            manufacturer="Test",
            quantity=50,
            unit="ml",
            location="B",
            category="Lubricants",
            warehouse_id=test_warehouse.id
        )
        db_session.add_all([chemical1, chemical2])
        db_session.commit()

        response = client.get("/api/chemicals?category=Adhesives")
        assert response.status_code == 200
        data = json.loads(response.data)

        categories = [c["category"] for c in data["chemicals"]]
        assert "Adhesives" in categories or len([c for c in data["chemicals"] if c["category"] == "Adhesives"]) > 0

    def test_get_chemicals_search(self, client, db_session, test_warehouse):
        """Test searching chemicals"""
        chemical = Chemical(
            part_number="UNIQUE123",
            lot_number="LOT123",
            description="UniqueSearchable Chemical",
            manufacturer="UniqueManufacturer",
            quantity=100,
            unit="g",
            location="Storage",
            warehouse_id=test_warehouse.id
        )
        db_session.add(chemical)
        db_session.commit()

        response = client.get("/api/chemicals?q=UniqueSearchable")
        assert response.status_code == 200
        data = json.loads(response.data)

        descriptions = [c["description"] for c in data["chemicals"]]
        assert "UniqueSearchable Chemical" in descriptions

    def test_get_chemicals_invalid_page(self, client):
        """Test invalid page number"""
        response = client.get("/api/chemicals?page=0")
        assert response.status_code == 400

    def test_get_chemicals_invalid_per_page(self, client):
        """Test invalid per_page value"""
        response = client.get("/api/chemicals?per_page=1000")
        assert response.status_code == 400


class TestChemicalCreateEndpoint:
    """Test the POST /api/chemicals endpoint"""

    def test_create_chemical_success(self, client, auth_headers_materials, test_warehouse):
        """Test creating a chemical successfully"""
        chemical_data = {
            "part_number": "PNEW001",
            "lot_number": "LNEW001",
            "description": "New Test Chemical",
            "manufacturer": "ACME Corp",
            "quantity": 100,
            "unit": "ml",
            "location": "Lab A",
            "warehouse_id": test_warehouse.id,
            "category": "Solvents"
        }

        response = client.post("/api/chemicals",
                               json=chemical_data,
                               headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data["part_number"] == "PNEW001"
        assert data["lot_number"] == "LNEW001"
        assert data["quantity"] == 100

    def test_create_chemical_without_auth(self, client, test_warehouse):
        """Test creating chemical without authentication"""
        chemical_data = {
            "part_number": "PN002",
            "lot_number": "LN002",
            "description": "Test",
            "quantity": 50,
            "unit": "g",
            "warehouse_id": test_warehouse.id
        }

        response = client.post("/api/chemicals", json=chemical_data)
        assert response.status_code == 401

    def test_create_chemical_missing_warehouse_id(self, client, auth_headers_materials):
        """Test creating chemical without warehouse_id"""
        chemical_data = {
            "part_number": "PN003",
            "lot_number": "LN003",
            "description": "Test",
            "quantity": 50,
            "unit": "ml"
        }

        response = client.post("/api/chemicals",
                               json=chemical_data,
                               headers=auth_headers_materials)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "warehouse_id" in data["error"]

    def test_create_chemical_invalid_warehouse(self, client, auth_headers_materials):
        """Test creating chemical with invalid warehouse"""
        chemical_data = {
            "part_number": "PN004",
            "lot_number": "LN004",
            "description": "Test",
            "quantity": 50,
            "unit": "ml",
            "warehouse_id": 99999
        }

        response = client.post("/api/chemicals",
                               json=chemical_data,
                               headers=auth_headers_materials)
        assert response.status_code == 400

    def test_create_chemical_duplicate(self, client, auth_headers_materials, test_chemical, test_warehouse):
        """Test creating duplicate chemical"""
        chemical_data = {
            "part_number": test_chemical.part_number,
            "lot_number": test_chemical.lot_number,
            "description": "Duplicate",
            "quantity": 50,
            "unit": "ml",
            "warehouse_id": test_warehouse.id
        }

        response = client.post("/api/chemicals",
                               json=chemical_data,
                               headers=auth_headers_materials)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "already exists" in data["error"]

    def test_create_chemical_missing_required_fields(self, client, auth_headers_materials, test_warehouse):
        """Test creating chemical with missing required fields"""
        chemical_data = {
            "part_number": "PN005",
            "warehouse_id": test_warehouse.id
            # Missing lot_number, quantity, unit
        }

        response = client.post("/api/chemicals",
                               json=chemical_data,
                               headers=auth_headers_materials)
        assert response.status_code == 400

    def test_create_chemical_logs_activity(self, client, auth_headers_materials, db_session, test_warehouse):
        """Test that chemical creation logs activity"""
        chemical_data = {
            "part_number": "PNLOG001",
            "lot_number": "LNLOG001",
            "description": "Log Test Chemical",
            "manufacturer": "Test",
            "quantity": 25,
            "unit": "oz",
            "location": "Test",
            "warehouse_id": test_warehouse.id
        }

        response = client.post("/api/chemicals",
                               json=chemical_data,
                               headers=auth_headers_materials)
        assert response.status_code == 201

        # Check audit log
        audit = AuditLog.query.filter_by(
            action_type="chemical_added"
        ).order_by(AuditLog.id.desc()).first()
        assert audit is not None
        assert "PNLOG001" in audit.action_details


class TestChemicalDetailEndpoint:
    """Test the GET/PUT/DELETE /api/chemicals/<id> endpoint"""

    def test_get_chemical_by_id(self, client, test_chemical):
        """Test getting a specific chemical"""
        response = client.get(f"/api/chemicals/{test_chemical.id}")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == test_chemical.id

    def test_get_chemical_not_found(self, client):
        """Test getting non-existent chemical"""
        response = client.get("/api/chemicals/99999")
        assert response.status_code == 404

    def test_update_chemical_success(self, client, auth_headers_materials, test_chemical):
        """Test updating a chemical"""
        update_data = {
            "description": "Updated Description",
            "quantity": 75
        }

        response = client.put(f"/api/chemicals/{test_chemical.id}",
                              json=update_data,
                              headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["description"] == "Updated Description"
        assert data["quantity"] == 75

    def test_update_chemical_without_auth(self, client, test_chemical):
        """Test updating chemical without authentication"""
        update_data = {"description": "New Desc"}

        response = client.put(f"/api/chemicals/{test_chemical.id}", json=update_data)
        assert response.status_code == 401

    def test_delete_chemical_success(self, client, auth_headers_admin, db_session, test_warehouse):
        """Test deleting a chemical"""
        # Create a chemical to delete
        chemical = Chemical(
            part_number="PNDEL001",
            lot_number="LNDEL001",
            description="To Delete",
            manufacturer="Test",
            quantity=10,
            unit="g",
            location="A",
            warehouse_id=test_warehouse.id
        )
        db_session.add(chemical)
        db_session.commit()
        chem_id = chemical.id

        response = client.delete(f"/api/chemicals/{chem_id}",
                                 headers=auth_headers_admin)
        assert response.status_code == 200

        # Verify deletion
        deleted = Chemical.query.get(chem_id)
        assert deleted is None

    def test_delete_chemical_not_found(self, client, auth_headers_admin):
        """Test deleting non-existent chemical"""
        response = client.delete("/api/chemicals/99999",
                                 headers=auth_headers_admin)
        assert response.status_code == 404


class TestChemicalIssuanceEndpoint:
    """Test the POST /api/chemicals/<id>/issue endpoint"""

    def test_issue_chemical_success(self, client, auth_headers_materials, test_chemical, db_session):
        """Test successful chemical issuance"""
        issuance_data = {
            "quantity": 5,
            "hangar": "Hangar A",
            "purpose": "Maintenance"
        }

        response = client.post(f"/api/chemicals/{test_chemical.id}/issue",
                               json=issuance_data,
                               headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "issuance" in data
        assert data["issuance"]["quantity_issued"] == 5

        # Verify quantity was reduced
        db_session.refresh(test_chemical)
        assert test_chemical.quantity == 45  # 50 - 5

    def test_issue_chemical_exceeds_stock(self, client, auth_headers_materials, test_chemical):
        """Test issuing more than available stock"""
        issuance_data = {
            "quantity": 1000,  # More than available
            "hangar": "Hangar B"
        }

        response = client.post(f"/api/chemicals/{test_chemical.id}/issue",
                               json=issuance_data,
                               headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Insufficient" in data.get("error", "") or "quantity" in data.get("error", "").lower()

    def test_issue_chemical_missing_fields(self, client, auth_headers_materials, test_chemical):
        """Test issuance with missing required fields"""
        issuance_data = {
            "quantity": 5
            # Missing hangar
        }

        response = client.post(f"/api/chemicals/{test_chemical.id}/issue",
                               json=issuance_data,
                               headers=auth_headers_materials)

        assert response.status_code == 400

    def test_issue_chemical_not_found(self, client, auth_headers_materials):
        """Test issuing non-existent chemical"""
        issuance_data = {
            "quantity": 5,
            "hangar": "Hangar C"
        }

        response = client.post("/api/chemicals/99999/issue",
                               json=issuance_data,
                               headers=auth_headers_materials)
        assert response.status_code == 404

    def test_issue_chemical_without_auth(self, client, test_chemical):
        """Test issuance without authentication"""
        issuance_data = {
            "quantity": 5,
            "hangar": "Hangar D"
        }

        response = client.post(f"/api/chemicals/{test_chemical.id}/issue",
                               json=issuance_data)
        assert response.status_code == 401


class TestChemicalReturnEndpoint:
    """Test the POST /api/chemicals/<id>/return endpoint"""

    def test_return_chemical_success(self, client, auth_headers_materials, test_chemical, db_session):
        """Test successful chemical return"""
        # First issue some chemical
        issuance_data = {
            "quantity": 10,
            "hangar": "Hangar A"
        }
        client.post(f"/api/chemicals/{test_chemical.id}/issue",
                    json=issuance_data,
                    headers=auth_headers_materials)

        # Now return some
        return_data = {
            "quantity": 5,
            "reason": "Unused portion",
            "condition": "good"
        }

        response = client.post(f"/api/chemicals/{test_chemical.id}/return",
                               json=return_data,
                               headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data

        # Verify quantity was increased
        db_session.refresh(test_chemical)
        assert test_chemical.quantity == 45  # 50 - 10 + 5

    def test_return_chemical_without_auth(self, client, test_chemical):
        """Test return without authentication"""
        return_data = {
            "quantity": 5,
            "reason": "Test"
        }

        response = client.post(f"/api/chemicals/{test_chemical.id}/return",
                               json=return_data)
        assert response.status_code == 401


class TestChemicalArchiveEndpoint:
    """Test archive/unarchive functionality"""

    def test_archive_chemical_success(self, client, auth_headers_materials, test_chemical):
        """Test archiving a chemical"""
        archive_data = {
            "reason": "Expired"
        }

        response = client.post(f"/api/chemicals/{test_chemical.id}/archive",
                               json=archive_data,
                               headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "archived" in data["message"].lower()

    def test_archive_chemical_not_found(self, client, auth_headers_materials):
        """Test archiving non-existent chemical"""
        archive_data = {"reason": "Test"}

        response = client.post("/api/chemicals/99999/archive",
                               json=archive_data,
                               headers=auth_headers_materials)
        assert response.status_code == 404

    def test_unarchive_chemical_success(self, client, auth_headers_materials, db_session, test_warehouse):
        """Test unarchiving a chemical"""
        # Create archived chemical
        chemical = Chemical(
            part_number="PNARCH001",
            lot_number="LNARCH001",
            description="Archived Chemical",
            manufacturer="Test",
            quantity=50,
            unit="ml",
            location="Storage",
            warehouse_id=test_warehouse.id,
            is_archived=True,
            archived_reason="Test archive"
        )
        db_session.add(chemical)
        db_session.commit()

        response = client.post(f"/api/chemicals/{chemical.id}/unarchive",
                               headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "unarchived" in data["message"].lower()


class TestChemicalReorderEndpoint:
    """Test reorder functionality"""

    def test_request_reorder_success(self, client, auth_headers_materials, test_chemical):
        """Test requesting a chemical reorder"""
        response = client.post(f"/api/chemicals/{test_chemical.id}/request-reorder",
                               headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "reorder" in data["message"].lower()

    def test_mark_ordered_success(self, client, auth_headers_materials, db_session, test_warehouse):
        """Test marking chemical as ordered"""
        # Create chemical with reorder requested
        chemical = Chemical(
            part_number="PNORD001",
            lot_number="LNORD001",
            description="Reorder Test",
            manufacturer="Test",
            quantity=5,
            unit="g",
            location="A",
            warehouse_id=test_warehouse.id,
            reorder_status="requested"
        )
        db_session.add(chemical)
        db_session.commit()

        order_data = {
            "po_number": "PO-2024-001",
            "expected_delivery": "2024-12-31"
        }

        response = client.post(f"/api/chemicals/{chemical.id}/mark-ordered",
                               json=order_data,
                               headers=auth_headers_materials)

        assert response.status_code == 200

    def test_mark_delivered_success(self, client, auth_headers_materials, db_session, test_warehouse):
        """Test marking chemical as delivered"""
        chemical = Chemical(
            part_number="PNDEL001",
            lot_number="LNDEL001",
            description="Delivery Test",
            manufacturer="Test",
            quantity=10,
            unit="oz",
            location="B",
            warehouse_id=test_warehouse.id,
            reorder_status="ordered"
        )
        db_session.add(chemical)
        db_session.commit()

        delivery_data = {
            "quantity_received": 50
        }

        response = client.post(f"/api/chemicals/{chemical.id}/mark-delivered",
                               json=delivery_data,
                               headers=auth_headers_materials)

        assert response.status_code == 200


class TestChemicalBarcodeEndpoint:
    """Test barcode generation endpoint"""

    def test_get_barcode_data(self, client, test_chemical):
        """Test getting barcode data for a chemical"""
        response = client.get(f"/api/chemicals/{test_chemical.id}/barcode")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "barcode_data" in data
        assert "qr_url" in data
        assert test_chemical.part_number in data["barcode_data"]

    def test_get_barcode_not_found(self, client):
        """Test getting barcode for non-existent chemical"""
        response = client.get("/api/chemicals/99999/barcode")
        assert response.status_code == 404


class TestChemicalHistoryEndpoints:
    """Test history endpoints"""

    def test_get_chemical_issuances(self, client, auth_headers_materials, test_chemical, db_session):
        """Test getting issuance history for a chemical"""
        # Create an issuance
        client.post(f"/api/chemicals/{test_chemical.id}/issue",
                    json={"quantity": 2, "hangar": "Test"},
                    headers=auth_headers_materials)

        response = client.get(f"/api/chemicals/{test_chemical.id}/issuances")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list) or "issuances" in data

    def test_get_chemical_returns(self, client, test_chemical):
        """Test getting return history for a chemical"""
        response = client.get(f"/api/chemicals/{test_chemical.id}/returns")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list) or "returns" in data


class TestSecurityFeatures:
    """Test security features in chemical routes"""

    def test_xss_prevention_in_description(self, client, auth_headers_materials, test_warehouse):
        """Test XSS prevention in chemical description"""
        chemical_data = {
            "part_number": "PNXSS001",
            "lot_number": "LNXSS001",
            "description": '<script>alert("XSS")</script>',
            "manufacturer": "Test",
            "quantity": 10,
            "unit": "ml",
            "location": "A",
            "warehouse_id": test_warehouse.id
        }

        response = client.post("/api/chemicals",
                               json=chemical_data,
                               headers=auth_headers_materials)

        if response.status_code == 201:
            data = json.loads(response.data)
            # Description should be sanitized
            assert "<script>" not in data.get("description", "")

    def test_sql_injection_prevention(self, client):
        """Test SQL injection prevention in search"""
        # Try SQL injection in search parameter
        response = client.get("/api/chemicals?q='; DROP TABLE chemicals; --")

        # Should not cause an error, just return results (or empty)
        assert response.status_code == 200

    def test_negative_quantity_rejected(self, client, auth_headers_materials, test_warehouse):
        """Test that negative quantities are rejected"""
        chemical_data = {
            "part_number": "PNNEG001",
            "lot_number": "LNNEG001",
            "description": "Negative Test",
            "manufacturer": "Test",
            "quantity": -10,
            "unit": "ml",
            "location": "A",
            "warehouse_id": test_warehouse.id
        }

        response = client.post("/api/chemicals",
                               json=chemical_data,
                               headers=auth_headers_materials)
        assert response.status_code == 400
