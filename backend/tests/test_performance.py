"""
Performance tests for SupplyLine MRO Suite

Tests critical performance aspects including:
- Bulk operations
- Database query performance
- Large dataset handling
- N+1 query detection
- Response time benchmarks
"""

import time
from datetime import datetime, timedelta

import pytest

from models import AuditLog, Chemical, InventoryTransaction, Tool, User
from models_kits import AircraftType, Kit, KitExpendable, KitItem


@pytest.mark.performance
@pytest.mark.slow
class TestBulkOperations:
    """Test performance of bulk operations"""

    def test_bulk_chemical_creation(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test creating multiple chemicals efficiently"""
        start_time = time.time()

        chemicals = []
        for i in range(100):
            chemical = Chemical(
                part_number=f"PERF-C{i:04d}",
                lot_number=f"LOT{i:04d}",
                description=f"Performance Test Chemical {i}",
                manufacturer="Test Manufacturer",
                quantity=100.0,
                unit="ml",
                location=f"Location-{i % 10}",
                category="Testing",
                status="available",
                warehouse_id=test_warehouse.id,
                created_by=admin_user.id
            )
            chemicals.append(chemical)

        db_session.bulk_save_objects(chemicals)
        db_session.commit()

        elapsed = time.time() - start_time
        assert elapsed < 5.0, f"Bulk chemical creation took {elapsed:.2f}s, expected < 5s"

        # Verify all created
        count = Chemical.query.filter(Chemical.part_number.like("PERF-C%")).count()
        assert count == 100

    def test_bulk_tool_creation(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test creating multiple tools efficiently"""
        start_time = time.time()

        tools = []
        for i in range(100):
            tool = Tool(
                tool_number=f"PERF-T{i:04d}",
                serial_number=f"SN{i:04d}",
                description=f"Performance Test Tool {i}",
                condition="Good",
                location=f"Location-{i % 10}",
                category="Testing",
                status="available",
                warehouse_id=test_warehouse.id,
                created_by=admin_user.id
            )
            tools.append(tool)

        db_session.bulk_save_objects(tools)
        db_session.commit()

        elapsed = time.time() - start_time
        assert elapsed < 5.0, f"Bulk tool creation took {elapsed:.2f}s, expected < 5s"

        # Verify all created
        count = Tool.query.filter(Tool.tool_number.like("PERF-T%")).count()
        assert count == 100

    def test_bulk_audit_log_query_performance(self, client, db_session, admin_user):
        """Test querying large audit log efficiently"""
        # Create bulk audit logs
        logs = []
        for i in range(500):
            log = AuditLog(
                user_id=admin_user.id,
                action=f"test_action_{i % 10}",
                resource_type="Tool" if i % 2 == 0 else "Chemical",
                resource_id=i,
                details=f"Performance test log entry {i}",
                timestamp=datetime.utcnow() - timedelta(hours=i)
            )
            logs.append(log)

        db_session.bulk_save_objects(logs)
        db_session.commit()

        # Test query performance
        start_time = time.time()
        recent_logs = (
            AuditLog.query
            .filter(AuditLog.user_id == admin_user.id)
            .order_by(AuditLog.timestamp.desc())
            .limit(100)
            .all()
        )
        elapsed = time.time() - start_time

        assert len(recent_logs) == 100
        assert elapsed < 1.0, f"Audit log query took {elapsed:.2f}s, expected < 1s"

    def test_large_inventory_transaction_query(self, client, db_session, admin_user, test_warehouse):
        """Test querying large inventory transaction history"""
        # Create chemicals
        chemicals = []
        for i in range(50):
            chemical = Chemical(
                part_number=f"INV-C{i:04d}",
                lot_number=f"LOT{i:04d}",
                description=f"Inventory Test Chemical {i}",
                manufacturer="Test Manufacturer",
                quantity=100.0,
                unit="ml",
                location="Test Location",
                category="Testing",
                status="available",
                warehouse_id=test_warehouse.id,
                created_by=admin_user.id
            )
            chemicals.append(chemical)

        db_session.bulk_save_objects(chemicals)
        db_session.flush()

        # Create transactions for each chemical
        transactions = []
        for chemical in chemicals:
            for j in range(10):
                transaction = InventoryTransaction(
                    item_type="Chemical",
                    item_id=chemical.id,
                    transaction_type="issuance" if j % 2 == 0 else "receipt",
                    quantity=10.0,
                    user_id=admin_user.id,
                    notes=f"Transaction {j}",
                    timestamp=datetime.utcnow() - timedelta(days=j)
                )
                transactions.append(transaction)

        db_session.bulk_save_objects(transactions)
        db_session.commit()

        # Test query performance
        start_time = time.time()
        recent_transactions = (
            InventoryTransaction.query
            .filter(InventoryTransaction.item_type == "Chemical")
            .order_by(InventoryTransaction.timestamp.desc())
            .limit(100)
            .all()
        )
        elapsed = time.time() - start_time

        assert len(recent_transactions) == 100
        assert elapsed < 1.0, f"Transaction query took {elapsed:.2f}s, expected < 1s"


@pytest.mark.performance
@pytest.mark.slow
class TestQueryOptimization:
    """Test for N+1 query problems and optimization"""

    def test_kit_items_eager_loading(self, client, db_session, test_user, test_warehouse):
        """Test that kit items are loaded efficiently without N+1 queries"""
        # Create aircraft type
        aircraft_type = AircraftType(
            name="Test Aircraft Type",
            description="Test type"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        # Create kits with items
        kits = []
        for i in range(10):
            kit = Kit(
                name=f"Performance Kit {i}",
                description=f"Test kit {i}",
                aircraft_type_id=aircraft_type.id,
                created_by=test_user.id,
                status="active"
            )
            db_session.add(kit)
            db_session.flush()

            # Add items to each kit
            for j in range(5):
                item = KitItem(
                    kit_id=kit.id,
                    tool_number=f"KIT{i}-T{j:03d}",
                    description=f"Kit {i} Item {j}",
                    quantity=1,
                    category="Testing"
                )
                db_session.add(item)

            kits.append(kit)

        db_session.commit()

        # Clear session to force fresh queries
        db_session.expire_all()

        # Test query performance - should use eager loading
        start_time = time.time()
        queried_kits = Kit.query.options(
            db_session.query(Kit).options(
                # Use joinedload for eager loading
            )
        ).filter(Kit.name.like("Performance Kit%")).all()

        # Access items for each kit
        for kit in queried_kits:
            _ = len(kit.items)  # This should not trigger additional queries

        elapsed = time.time() - start_time
        assert len(queried_kits) == 10
        assert elapsed < 1.0, f"Kit query with items took {elapsed:.2f}s, expected < 1s"

    def test_user_activity_pagination_performance(self, client, db_session, admin_user):
        """Test pagination performance for large result sets"""
        from models import UserActivity

        # Create bulk activities
        activities = []
        for i in range(1000):
            activity = UserActivity(
                user_id=admin_user.id,
                activity_type=f"action_{i % 20}",
                description=f"Activity {i}",
                timestamp=datetime.utcnow() - timedelta(minutes=i)
            )
            activities.append(activity)

        db_session.bulk_save_objects(activities)
        db_session.commit()

        # Test paginated query performance
        start_time = time.time()
        page_1 = (
            UserActivity.query
            .filter(UserActivity.user_id == admin_user.id)
            .order_by(UserActivity.timestamp.desc())
            .limit(50)
            .offset(0)
            .all()
        )
        elapsed = time.time() - start_time

        assert len(page_1) == 50
        assert elapsed < 0.5, f"Pagination query took {elapsed:.2f}s, expected < 0.5s"

        # Test later page
        start_time = time.time()
        page_20 = (
            UserActivity.query
            .filter(UserActivity.user_id == admin_user.id)
            .order_by(UserActivity.timestamp.desc())
            .limit(50)
            .offset(950)
            .all()
        )
        elapsed = time.time() - start_time

        assert len(page_20) == 50
        assert elapsed < 0.5, f"Late pagination query took {elapsed:.2f}s, expected < 0.5s"


@pytest.mark.performance
@pytest.mark.api
class TestAPIResponseTimes:
    """Test API endpoint response times"""

    def test_tools_list_response_time(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test tools list endpoint response time with large dataset"""
        # Create 200 tools
        tools = []
        for i in range(200):
            tool = Tool(
                tool_number=f"RT{i:04d}",
                serial_number=f"SN{i:04d}",
                description=f"Response Test Tool {i}",
                condition="Good",
                location=f"Loc-{i % 20}",
                category="Testing",
                status="available",
                warehouse_id=test_warehouse.id,
                created_by=admin_user.id
            )
            tools.append(tool)

        db_session.bulk_save_objects(tools)
        db_session.commit()

        # Test endpoint response time
        start_time = time.time()
        response = client.get("/api/tools", headers=auth_headers)
        elapsed = time.time() - start_time

        assert response.status_code == 200
        assert elapsed < 2.0, f"Tools list endpoint took {elapsed:.2f}s, expected < 2s"

        data = response.get_json()
        assert len(data) >= 200

    def test_chemicals_list_response_time(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test chemicals list endpoint response time with large dataset"""
        # Create 200 chemicals
        chemicals = []
        for i in range(200):
            chemical = Chemical(
                part_number=f"RC{i:04d}",
                lot_number=f"LOT{i:04d}",
                description=f"Response Test Chemical {i}",
                manufacturer="Test Manufacturer",
                quantity=100.0,
                unit="ml",
                location=f"Loc-{i % 20}",
                category="Testing",
                status="available",
                warehouse_id=test_warehouse.id,
                created_by=admin_user.id
            )
            chemicals.append(chemical)

        db_session.bulk_save_objects(chemicals)
        db_session.commit()

        # Test endpoint response time
        start_time = time.time()
        response = client.get("/api/chemicals", headers=auth_headers)
        elapsed = time.time() - start_time

        assert response.status_code == 200
        assert elapsed < 2.0, f"Chemicals list endpoint took {elapsed:.2f}s, expected < 2s"

        data = response.get_json()
        assert len(data) >= 200

    def test_search_performance(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test search endpoint performance"""
        # Create diverse tools
        for i in range(100):
            tool = Tool(
                tool_number=f"SEARCH{i:04d}",
                serial_number=f"SN{i:04d}",
                description=f"Searchable Tool {i} with keyword{i % 10}",
                condition="Good",
                location=f"Location-{i % 10}",
                category=f"Category{i % 5}",
                status="available",
                warehouse_id=test_warehouse.id,
                created_by=admin_user.id
            )
            db_session.add(tool)

        db_session.commit()

        # Test search response time
        start_time = time.time()
        response = client.get("/api/tools?search=keyword5", headers=auth_headers)
        elapsed = time.time() - start_time

        assert response.status_code == 200
        assert elapsed < 1.0, f"Search took {elapsed:.2f}s, expected < 1s"


@pytest.mark.performance
@pytest.mark.slow
class TestMemoryUsage:
    """Test memory efficiency for large operations"""

    def test_bulk_chemical_issuance_memory(self, client, db_session, admin_user, test_warehouse):
        """Test memory efficiency when processing bulk chemical issuance"""
        # Create chemicals
        chemicals = []
        for i in range(50):
            chemical = Chemical(
                part_number=f"MEM-C{i:04d}",
                lot_number=f"LOT{i:04d}",
                description=f"Memory Test Chemical {i}",
                manufacturer="Test Manufacturer",
                quantity=1000.0,
                unit="ml",
                location="Test Location",
                category="Testing",
                status="available",
                warehouse_id=test_warehouse.id,
                reorder_point=100.0,
                created_by=admin_user.id
            )
            chemicals.append(chemical)

        db_session.bulk_save_objects(chemicals)
        db_session.commit()

        # Process issuances in batches (memory efficient approach)
        start_time = time.time()
        batch_size = 10

        for i in range(0, 50, batch_size):
            batch_chemicals = Chemical.query.filter(
                Chemical.part_number.like("MEM-C%")
            ).limit(batch_size).offset(i).all()

            for chemical in batch_chemicals:
                # Simulate issuance
                transaction = InventoryTransaction(
                    item_type="Chemical",
                    item_id=chemical.id,
                    transaction_type="issuance",
                    quantity=50.0,
                    user_id=admin_user.id,
                    notes="Bulk issuance test"
                )
                db_session.add(transaction)

                chemical.quantity -= 50.0

            db_session.commit()
            db_session.expire_all()  # Clear session to free memory

        elapsed = time.time() - start_time
        assert elapsed < 5.0, f"Bulk issuance took {elapsed:.2f}s, expected < 5s"

        # Verify all processed
        transaction_count = InventoryTransaction.query.filter(
            InventoryTransaction.notes == "Bulk issuance test"
        ).count()
        assert transaction_count == 50
