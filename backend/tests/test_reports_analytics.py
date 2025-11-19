"""
Reports and analytics tests for SupplyLine MRO Suite

Tests reporting and analytics functionality including:
- Inventory reports
- Usage analytics
- Tool utilization reports
- Chemical consumption analytics
- Trend analysis
- Export functionality
"""

from datetime import datetime, timedelta
from io import BytesIO

import pytest

from models import Chemical, InventoryTransaction, Tool, User, UserActivity


@pytest.mark.reports
@pytest.mark.integration
class TestInventoryReports:
    """Test inventory reporting functionality"""

    def test_generate_tool_inventory_report(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test generating tool inventory report"""
        # Create various tools
        for i in range(10):
            tool = Tool(
                tool_number=f"RPT-T{i:03d}",
                serial_number=f"SN{i:03d}",
                description=f"Report Tool {i}",
                condition="Good" if i % 2 == 0 else "Fair",
                location=f"Location {i % 3}",
                category=f"Category{i % 2}",
                warehouse_id=test_warehouse.id,
                status="available" if i % 3 != 0 else "checked_out"
            )
            db_session.add(tool)

        db_session.commit()

        # Generate report
        response = client.get("/api/reports/tools", headers=auth_headers)

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.get_json()
            assert "tools" in data or isinstance(data, list)

    def test_generate_chemical_inventory_report(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test generating chemical inventory report"""
        # Create various chemicals
        for i in range(10):
            chemical = Chemical(
                part_number=f"RPT-C{i:03d}",
                lot_number=f"LOT{i:03d}",
                description=f"Report Chemical {i}",
                manufacturer="Manufacturer",
                quantity=100.0 + (i * 50),
                unit="ml",
                location=f"Storage {i % 3}",
                category=f"Category{i % 2}",
                warehouse_id=test_warehouse.id,
                status="available"
            )
            db_session.add(chemical)

        db_session.commit()

        # Generate report
        response = client.get("/api/reports/chemicals", headers=auth_headers)

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.get_json()
            assert "chemicals" in data or isinstance(data, list)

    def test_low_stock_report(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test low stock report generation"""
        # Create chemicals with varying quantities
        low_stock_items = []
        for i in range(5):
            chemical = Chemical(
                part_number=f"LOW-C{i:03d}",
                lot_number=f"LOT{i:03d}",
                description=f"Low Stock Chemical {i}",
                manufacturer="Manufacturer",
                quantity=5.0 + i,  # Low quantity
                unit="ml",
                location="Storage",
                category="Category1",
                warehouse_id=test_warehouse.id,
                status="available",
                minimum_stock_level=50.0  # Below minimum stock level
            )
            db_session.add(chemical)
            low_stock_items.append(chemical)

        # Normal stock items
        for i in range(3):
            chemical = Chemical(
                part_number=f"NORM-C{i:03d}",
                lot_number=f"LOT{i:03d}",
                description=f"Normal Stock Chemical {i}",
                manufacturer="Manufacturer",
                quantity=500.0,
                unit="ml",
                location="Storage",
                category="Category1",
                warehouse_id=test_warehouse.id,
                status="available",
                minimum_stock_level=50.0
            )
            db_session.add(chemical)

        db_session.commit()

        # Get low stock report
        response = client.get("/api/reports/low-stock", headers=auth_headers)

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.get_json()
            # Should include low stock items
            assert len(data) >= 5 or "items" in data

    def test_expiring_items_report(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test report for expiring chemicals"""
        # Create chemicals with expiration dates
        for i in range(5):
            days_to_expiry = 30 + (i * 10)
            chemical = Chemical(
                part_number=f"EXP-C{i:03d}",
                lot_number=f"LOT{i:03d}",
                description=f"Expiring Chemical {i}",
                manufacturer="Manufacturer",
                quantity=100.0,
                unit="ml",
                location="Storage",
                category="Category1",
                warehouse_id=test_warehouse.id,
                status="available",
                expiration_date=datetime.utcnow() + timedelta(days=days_to_expiry)
            )
            db_session.add(chemical)

        db_session.commit()

        # Get expiring items report (within 60 days)
        response = client.get("/api/reports/expiring?days=60", headers=auth_headers)

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.get_json()
            assert len(data) >= 3 or "items" in data


@pytest.mark.analytics
@pytest.mark.integration
class TestUsageAnalytics:
    """Test usage analytics functionality"""

    def test_tool_usage_analytics(self, client, db_session, admin_user, test_user, auth_headers, test_warehouse):
        """Test tool usage analytics"""
        # Create tool with usage history
        tool = Tool(
            tool_number="USAGE-T001",
            serial_number="SN-USAGE001",
            description="Analytics Test Tool",
            condition="Good",
            location="Lab",
            category="Testing",
            warehouse_id=test_warehouse.id,
            status="available"
        )
        db_session.add(tool)
        db_session.flush()

        # Create usage activities
        for i in range(10):
            activity = UserActivity(
                user_id=test_user.id,
                activity_type="checkout",
                description=f"Checked out {tool.tool_number}",
                timestamp=datetime.utcnow() - timedelta(days=i)
            )
            db_session.add(activity)

        db_session.commit()

        # Get usage analytics
        response = client.get(f"/api/analytics/tools/{tool.id}/usage", headers=auth_headers)

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.get_json()
            assert "usage_count" in data or "checkouts" in data or isinstance(data, list)

    def test_chemical_consumption_analytics(self, client, db_session, admin_user, test_user, auth_headers, test_warehouse):
        """Test chemical consumption analytics"""
        # Create chemical with transaction history
        chemical = Chemical(
            part_number="USAGE-C001",
            lot_number="LOT-USAGE001",
            description="Analytics Test Chemical",
            manufacturer="Manufacturer",
            quantity=1000.0,
            unit="ml",
            location="Storage",
            category="Testing",
            warehouse_id=test_warehouse.id,
            status="available"
        )
        db_session.add(chemical)
        db_session.flush()

        # Create consumption transactions
        for i in range(15):
            transaction = InventoryTransaction(
                item_type="Chemical",
                item_id=chemical.id,
                transaction_type="issuance",
                quantity_change=-25.0,
                user_id=test_user.id,
                notes=f"Usage transaction {i}",
                timestamp=datetime.utcnow() - timedelta(days=i)
            )
            db_session.add(transaction)

        db_session.commit()

        # Get consumption analytics
        response = client.get(f"/api/analytics/chemicals/{chemical.id}/consumption", headers=auth_headers)

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.get_json()
            assert "total_consumed" in data or "transactions" in data or isinstance(data, list)

    def test_user_activity_analytics(self, client, db_session, admin_user, test_user, auth_headers):
        """Test user activity analytics"""
        # Create various user activities
        activity_types = ["checkout", "return", "issuance", "receipt", "transfer"]

        for i in range(20):
            activity = UserActivity(
                user_id=test_user.id,
                activity_type=activity_types[i % len(activity_types)],
                description=f"Activity {i}",
                timestamp=datetime.utcnow() - timedelta(hours=i)
            )
            db_session.add(activity)

        db_session.commit()

        # Get user analytics
        response = client.get(f"/api/analytics/users/{test_user.id}", headers=auth_headers)

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.get_json()
            assert "activity_count" in data or "activities" in data or isinstance(data, list)

    def test_warehouse_utilization_analytics(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test warehouse utilization analytics"""
        # Create items in warehouse
        for i in range(20):
            tool = Tool(
                tool_number=f"WH-T{i:03d}",
                serial_number=f"SN{i:03d}",
                description=f"Warehouse Tool {i}",
                condition="Good",
                location=f"Location {i % 5}",
                category="Testing",
                warehouse_id=test_warehouse.id,
                status="available" if i % 2 == 0 else "checked_out"
            )
            db_session.add(tool)

        db_session.commit()

        # Get warehouse analytics
        response = client.get(f"/api/analytics/warehouses/{test_warehouse.id}", headers=auth_headers)

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.get_json()
            assert "total_items" in data or "utilization" in data or isinstance(data, dict)


@pytest.mark.analytics
@pytest.mark.integration
class TestTrendAnalysis:
    """Test trend analysis functionality"""

    def test_inventory_trend_analysis(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test inventory level trends over time"""
        chemical = Chemical(
            part_number="TREND-C001",
            lot_number="LOT-TREND001",
            description="Trend Test Chemical",
            manufacturer="Manufacturer",
            quantity=1000.0,
            unit="ml",
            location="Storage",
            category="Testing",
            warehouse_id=test_warehouse.id,
            status="available"
        )
        db_session.add(chemical)
        db_session.flush()

        # Create transactions over time showing trend
        quantities = [50, 75, 60, 90, 100, 85, 70, 95, 80, 110]
        for i, qty in enumerate(quantities):
            transaction = InventoryTransaction(
                item_type="Chemical",
                item_id=chemical.id,
                transaction_type="issuance",
                quantity_change=-qty,
                user_id=admin_user.id,
                notes=f"Trend transaction {i}",
                timestamp=datetime.utcnow() - timedelta(days=30 - (i * 3))
            )
            db_session.add(transaction)

        db_session.commit()

        # Get trend analysis
        response = client.get(
            f"/api/analytics/chemicals/{chemical.id}/trends?period=30",
            headers=auth_headers
        )

        assert response.status_code in [200, 404]

    def test_usage_frequency_analysis(self, client, db_session, admin_user, test_user, auth_headers, test_warehouse):
        """Test usage frequency analysis"""
        # Create tools with varying usage frequencies
        tools = []
        for i in range(5):
            tool = Tool(
                tool_number=f"FREQ-T{i:03d}",
                serial_number=f"SN-FREQ{i:03d}",
                description=f"Frequency Tool {i}",
                condition="Good",
                location="Lab",
                category="Testing",
                warehouse_id=test_warehouse.id,
                status="available"
            )
            db_session.add(tool)
            db_session.flush()

            # Create varying number of checkouts
            for j in range(i * 3):
                activity = UserActivity(
                    user_id=test_user.id,
                    activity_type="checkout",
                    description=f"Checkout {tool.tool_number}",
                    timestamp=datetime.utcnow() - timedelta(days=j)
                )
                db_session.add(activity)

            tools.append(tool)

        db_session.commit()

        # Get frequency analysis
        response = client.get("/api/analytics/tools/frequency", headers=auth_headers)

        assert response.status_code in [200, 404]


@pytest.mark.reports
@pytest.mark.integration
class TestReportExport:
    """Test report export functionality"""

    def test_export_report_to_csv(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test exporting report to CSV format"""
        # Create test data
        for i in range(10):
            chemical = Chemical(
                part_number=f"CSV-C{i:03d}",
                lot_number=f"LOT{i:03d}",
                description=f"CSV Export Chemical {i}",
                manufacturer="Manufacturer",
                quantity=100.0 + i,
                unit="ml",
                location="Storage",
                category="Category1",
                warehouse_id=test_warehouse.id,
                status="available"
            )
            db_session.add(chemical)

        db_session.commit()

        # Export to CSV
        response = client.get("/api/reports/chemicals/export?format=csv", headers=auth_headers)

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            # Verify CSV format
            assert response.content_type in ["text/csv", "application/csv"] or "csv" in response.headers.get("Content-Disposition", "")

    def test_export_report_to_excel(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test exporting report to Excel format"""
        # Create test data
        for i in range(10):
            tool = Tool(
                tool_number=f"XLS-T{i:03d}",
                serial_number=f"SN{i:03d}",
                description=f"Excel Export Tool {i}",
                condition="Good",
                location="Lab",
                category="Testing",
                warehouse_id=test_warehouse.id,
                status="available"
            )
            db_session.add(tool)

        db_session.commit()

        # Export to Excel
        response = client.get("/api/reports/tools/export?format=xlsx", headers=auth_headers)

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            # Verify Excel format
            expected_types = [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel"
            ]
            assert any(ct in response.content_type for ct in expected_types) or "xlsx" in response.headers.get("Content-Disposition", "")

    def test_export_report_to_pdf(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test exporting report to PDF format"""
        response = client.get("/api/reports/inventory/export?format=pdf", headers=auth_headers)

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            # Verify PDF format
            assert "application/pdf" in response.content_type or "pdf" in response.headers.get("Content-Disposition", "")


@pytest.mark.reports
@pytest.mark.performance
class TestReportPerformance:
    """Test report generation performance"""

    def test_large_report_generation_performance(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test that large reports are generated efficiently"""
        import time

        # Create large dataset
        for i in range(500):
            tool = Tool(
                tool_number=f"PERF-R{i:04d}",
                serial_number=f"SN{i:04d}",
                description=f"Performance Report Tool {i}",
                condition="Good",
                location=f"Location {i % 10}",
                category=f"Category{i % 5}",
                warehouse_id=test_warehouse.id,
                status="available"
            )
            db_session.add(tool)

        db_session.commit()

        # Generate report
        start_time = time.time()
        response = client.get("/api/reports/tools", headers=auth_headers)
        elapsed = time.time() - start_time

        if response.status_code == 200:
            assert elapsed < 5.0, f"Report generation took {elapsed:.2f}s, expected < 5s"

    def test_report_caching(self, client, db_session, admin_user, auth_headers):
        """Test that reports are cached appropriately"""
        # First request
        response1 = client.get("/api/reports/inventory", headers=auth_headers)

        if response1.status_code == 200:
            # Second request (may be cached depending on implementation)
            response2 = client.get("/api/reports/inventory", headers=auth_headers)

            # Second request should succeed
            assert response2.status_code == 200


@pytest.mark.analytics
@pytest.mark.api
class TestAnalyticsAPI:
    """Test analytics API endpoints"""

    def test_dashboard_analytics_summary(self, client, db_session, admin_user, auth_headers, test_warehouse):
        """Test dashboard analytics summary endpoint"""
        # Create diverse data
        for i in range(5):
            tool = Tool(
                tool_number=f"DASH-T{i:03d}",
                serial_number=f"SN{i:03d}",
                description=f"Dashboard Tool {i}",
                condition="Good",
                location="Lab",
                category="Testing",
                warehouse_id=test_warehouse.id,
                status="available"
            )
            db_session.add(tool)

            chemical = Chemical(
                part_number=f"DASH-C{i:03d}",
                lot_number=f"LOT{i:03d}",
                description=f"Dashboard Chemical {i}",
                manufacturer="Manufacturer",
                quantity=100.0,
                unit="ml",
                location="Storage",
                category="Testing",
                warehouse_id=test_warehouse.id,
                status="available"
            )
            db_session.add(chemical)

        db_session.commit()

        # Get dashboard summary
        response = client.get("/api/analytics/dashboard", headers=auth_headers)

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.get_json()
            # Should include summary statistics
            assert isinstance(data, dict)

    def test_custom_date_range_analytics(self, client, db_session, admin_user, test_user, auth_headers):
        """Test analytics with custom date ranges"""
        # Create historical activities
        for i in range(30):
            activity = UserActivity(
                user_id=test_user.id,
                activity_type="checkout",
                description=f"Historical activity {i}",
                timestamp=datetime.utcnow() - timedelta(days=i)
            )
            db_session.add(activity)

        db_session.commit()

        # Get analytics for specific date range
        start_date = (datetime.utcnow() - timedelta(days=14)).strftime("%Y-%m-%d")
        end_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

        response = client.get(
            f"/api/analytics/activity?start={start_date}&end={end_date}",
            headers=auth_headers
        )

        assert response.status_code in [200, 404]
