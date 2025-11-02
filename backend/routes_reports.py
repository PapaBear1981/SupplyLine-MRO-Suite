import logging
from datetime import datetime, timedelta

from flask import jsonify, make_response, request
from sqlalchemy import func

from auth import department_required
from models import Checkout, Tool, User, db
from utils.export_utils import generate_excel_report, generate_pdf_report


logger = logging.getLogger(__name__)


def calculate_date_range(timeframe):
    """Calculate start date based on timeframe parameter."""
    now = datetime.now()
    if timeframe == "day":
        return now - timedelta(days=1)
    if timeframe == "week":
        return now - timedelta(weeks=1)
    if timeframe == "month":
        return now - timedelta(days=30)
    if timeframe == "quarter":
        return now - timedelta(days=90)
    if timeframe == "year":
        return now - timedelta(days=365)
    if timeframe == "all":
        return datetime(1970, 1, 1)  # Beginning of time for database purposes
    return now - timedelta(days=30)  # Default to month


tool_manager_required = department_required("Materials")


def register_report_routes(app):
    # Export report as PDF
    @app.route("/api/reports/export/pd", methods=["POST"])
    @tool_manager_required
    def export_report_pdf():
        try:
            data = request.get_json()
            report_type = data.get("report_type")
            report_data = data.get("report_data")
            timeframe = data.get("timeframe", "month")

            if not report_type or not report_data:
                return jsonify({"error": "Missing report_type or report_data"}), 400

            # Generate PDF using export utilities
            pdf_buffer = generate_pdf_report(report_data, report_type, timeframe)

            # Return PDF as response
            response = make_response(pdf_buffer.getvalue())
            response.headers["Content-Type"] = "application/pd"
            response.headers["Content-Disposition"] = f'attachment; filename="{report_type}-report.pd"'

            return response

        except Exception:
            logger.exception("Failed to generate PDF report")
            return jsonify({"error": "Failed to generate PDF"}), 500

    # Export report as Excel
    @app.route("/api/reports/export/excel", methods=["POST"])
    @tool_manager_required
    def export_report_excel():
        try:
            data = request.get_json()
            report_type = data.get("report_type")
            report_data = data.get("report_data")
            timeframe = data.get("timeframe", "month")

            if not report_type or not report_data:
                return jsonify({"error": "Missing report_type or report_data"}), 400

            # Generate Excel using export utilities
            excel_buffer = generate_excel_report(report_data, report_type, timeframe)

            # Return Excel as response
            response = make_response(excel_buffer.getvalue())
            response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response.headers["Content-Disposition"] = f'attachment; filename="{report_type}-report.xlsx"'

            return response

        except Exception:
            logger.exception("Failed to generate Excel report")
            return jsonify({"error": "Failed to generate Excel"}), 500

    # Tool Inventory Report
    @app.route("/api/reports/tools", methods=["GET"])
    @tool_manager_required
    def tool_inventory_report():
        try:
            # Get filter parameters
            category = request.args.get("category")
            status = request.args.get("status")
            location = request.args.get("location")

            # Start with base query
            query = Tool.query

            # Apply filters if provided
            if category:
                query = query.filter(Tool.category == category)

            if status:
                # For 'available' status, we need to check both the tool status and active checkouts
                if status == "available":
                    # Get IDs of tools that are checked out
                    checked_out_tool_ids = [c.tool_id for c in Checkout.query.filter(Checkout.return_date.is_(None)).all()]
                    # Filter for tools that are not in the checked out list and have status 'available'
                    query = query.filter(~Tool.id.in_(checked_out_tool_ids))
                    query = query.filter(Tool.status.in_(["available", None]))
                elif status == "checked_out":
                    # Get IDs of tools that are checked out
                    checked_out_tool_ids = [c.tool_id for c in Checkout.query.filter(Checkout.return_date.is_(None)).all()]
                    # Filter for tools that are in the checked out list
                    query = query.filter(Tool.id.in_(checked_out_tool_ids))
                else:
                    # For maintenance and retired, just check the tool status
                    query = query.filter(Tool.status == status)

            if location:
                query = query.filter(Tool.location.ilike(f"%{location}%"))

            # Execute query
            tools = query.all()

            # Get checkout status for each tool
            tool_status = {}
            active_checkouts = Checkout.query.filter(Checkout.return_date.is_(None)).all()

            for checkout in active_checkouts:
                tool_status[checkout.tool_id] = "checked_out"

            # Format response
            result = [{
                "id": t.id,
                "tool_number": t.tool_number,
                "serial_number": t.serial_number,
                "description": t.description,
                "condition": t.condition,
                "location": t.location,
                "category": getattr(t, "category", "General"),
                "status": tool_status.get(t.id, getattr(t, "status", "available")),
                "status_reason": getattr(t, "status_reason", None) if getattr(t, "status", "available") in ["maintenance", "retired"] else None,
                "created_at": t.created_at.isoformat()
            } for t in tools]

            return jsonify(result), 200

        except Exception:
            logger.exception("Error in tool inventory report")
            return jsonify({
                "error": "An error occurred while generating the tool inventory report"
            }), 500

    # Checkout History Report
    @app.route("/api/reports/checkouts", methods=["GET"])
    @tool_manager_required
    def checkout_history_report():
        try:
            # Get timeframe parameter
            timeframe = request.args.get("timeframe", "month")

            # Get filter parameters
            department = request.args.get("department")
            checkout_status = request.args.get("checkoutStatus")
            tool_category = request.args.get("toolCategory")

            # Calculate date range based on timeframe
            now = datetime.now()
            if timeframe == "day":
                start_date = now - timedelta(days=1)
            elif timeframe == "week":
                start_date = now - timedelta(weeks=1)
            elif timeframe == "month":
                start_date = now - timedelta(days=30)
            elif timeframe == "quarter":
                start_date = now - timedelta(days=90)
            elif timeframe == "year":
                start_date = now - timedelta(days=365)
            elif timeframe == "all":
                start_date = datetime(1970, 1, 1)  # Beginning of time for database purposes
            else:
                start_date = now - timedelta(weeks=1)  # Default to week

            # Start with base query
            query = Checkout.query.filter(Checkout.checkout_date >= start_date)

            # Apply filters if provided
            if department:
                query = query.join(User).filter(User.department == department)

            if checkout_status:
                if checkout_status == "active":
                    query = query.filter(Checkout.return_date.is_(None))
                elif checkout_status == "returned":
                    query = query.filter(Checkout.return_date.isnot(None))

            if tool_category:
                query = query.join(Tool).filter(Tool.category == tool_category)

            # Execute query
            checkouts = query.order_by(Checkout.checkout_date.desc()).all()

            # Calculate duration for each checkout
            checkout_data = []
            for c in checkouts:
                # Calculate duration in days
                if c.return_date:
                    duration = (c.return_date - c.checkout_date).days
                    duration = max(duration, 0)  # Handle case where return_date might be before checkout_date due to data issues
                else:
                    duration = (now - c.checkout_date).days

                checkout_data.append({
                    "id": c.id,
                    "tool_id": c.tool_id,
                    "tool_number": c.tool.tool_number if c.tool else "Unknown",
                    "serial_number": c.tool.serial_number if c.tool else "Unknown",
                    "description": c.tool.description if c.tool else "",
                    "category": c.tool.category if c.tool else "General",
                    "user_id": c.user_id,
                    "user_name": c.user.name if c.user else "Unknown",
                    "department": c.user.department if c.user else "Unknown",
                    "checkout_date": c.checkout_date.isoformat(),
                    "return_date": c.return_date.isoformat() if c.return_date else None,
                    "expected_return_date": c.expected_return_date.isoformat() if c.expected_return_date else None,
                    "duration": duration
                })

            # Calculate checkout trends by day
            checkout_trends = db.session.query(
                func.date(Checkout.checkout_date).label("date"),
                func.count().label("checkouts")
            ).filter(
                Checkout.checkout_date >= start_date
            ).group_by(
                func.date(Checkout.checkout_date)
            ).all()

            return_trends = db.session.query(
                func.date(Checkout.return_date).label("date"),
                func.count().label("returns")
            ).filter(
                Checkout.return_date >= start_date,
                Checkout.return_date.isnot(None)
            ).group_by(
                func.date(Checkout.return_date)
            ).all()

            # Combine checkout and return trends
            date_data = {}

            for date, count in checkout_trends:
                # Handle case where date might be a string or a datetime object
                date_str = date if isinstance(date, str) else date.strftime("%Y-%m-%d")

                if date_str not in date_data:
                    date_data[date_str] = {"date": date_str, "checkouts": 0, "returns": 0}
                date_data[date_str]["checkouts"] = count

            for date, count in return_trends:
                # Handle case where date might be a string or a datetime object
                date_str = date if isinstance(date, str) else date.strftime("%Y-%m-%d")

                if date_str not in date_data:
                    date_data[date_str] = {"date": date_str, "checkouts": 0, "returns": 0}
                date_data[date_str]["returns"] = count

            # Convert to list and sort by date
            checkout_by_day = sorted(date_data.values(), key=lambda x: x["date"])

            # Calculate summary statistics
            total_checkouts = len(checkouts)
            returned_checkouts = sum(1 for c in checkouts if c.return_date)
            currently_checked_out = total_checkouts - returned_checkouts

            # Calculate average duration for returned checkouts
            durations = [c["duration"] for c in checkout_data if c["return_date"]]
            average_duration = sum(durations) / len(durations) if durations else 0

            # Format response
            result = {
                "checkouts": checkout_data,
                "checkoutsByDay": checkout_by_day,
                "stats": {
                    "totalCheckouts": total_checkouts,
                    "returnedCheckouts": returned_checkouts,
                    "currentlyCheckedOut": currently_checked_out,
                    "averageDuration": round(average_duration, 1)
                }
            }

            return jsonify(result), 200

        except Exception:
            logger.exception("Error in checkout history report")
            return jsonify({
                "error": "An error occurred while generating the checkout history report"
            }), 500

    # Department Usage Report
    @app.route("/api/reports/departments", methods=["GET"])
    @tool_manager_required
    def department_usage_report():
        try:
            # Get timeframe parameter
            timeframe = request.args.get("timeframe", "month")

            # Calculate date range based on timeframe
            now = datetime.now()
            if timeframe == "day":
                start_date = now - timedelta(days=1)
            elif timeframe == "week":
                start_date = now - timedelta(weeks=1)
            elif timeframe == "month":
                start_date = now - timedelta(days=30)
            elif timeframe == "quarter":
                start_date = now - timedelta(days=90)
            elif timeframe == "year":
                start_date = now - timedelta(days=365)
            elif timeframe == "all":
                start_date = datetime(1970, 1, 1)  # Beginning of time for database purposes
            else:
                start_date = now - timedelta(weeks=1)  # Default to week

            # Get all departments
            departments = db.session.query(User.department).distinct().all()
            department_names = [d[0] for d in departments if d[0]]

            # Initialize response data
            department_data = []

            # For each department, calculate usage statistics
            for dept in department_names:
                # Get all checkouts for this department
                dept_checkouts = Checkout.query.join(User).filter(
                    User.department == dept,
                    Checkout.checkout_date >= start_date
                ).all()

                # Calculate total checkouts
                total_checkouts = len(dept_checkouts)

                # Skip departments with no checkouts
                if total_checkouts == 0:
                    continue

                # Calculate currently checked out
                currently_checked_out = sum(1 for c in dept_checkouts if not c.return_date)

                # Calculate average duration for returned checkouts
                durations = []
                for c in dept_checkouts:
                    if c.return_date:
                        try:
                            duration = (c.return_date - c.checkout_date).days
                            duration = max(duration, 0)  # Handle case where return_date might be before checkout_date
                            durations.append(duration)
                        except Exception:
                            logger.exception("Error calculating checkout duration for department usage report")
                            # Skip this checkout if there's an error

                average_duration = sum(durations) / len(durations) if durations else 0

                # Find most used tool category for this department
                tool_categories = {}
                for c in dept_checkouts:
                    category = c.tool.category if c.tool and hasattr(c.tool, "category") else "General"
                    tool_categories[category] = tool_categories.get(category, 0) + 1

                most_used_category = max(tool_categories.items(), key=lambda x: x[1])[0] if tool_categories else None

                # Add department data
                department_data.append({
                    "name": dept,
                    "totalCheckouts": total_checkouts,
                    "currentlyCheckedOut": currently_checked_out,
                    "averageDuration": round(average_duration, 1),
                    "mostUsedCategory": most_used_category
                })

            # Sort departments by total checkouts
            department_data.sort(key=lambda x: x["totalCheckouts"], reverse=True)

            # Calculate checkouts by department for pie chart
            checkouts_by_dept = [{"name": d["name"], "value": d["totalCheckouts"]} for d in department_data]

            # Calculate tool usage by category
            tool_usage = db.session.query(
                Tool.category,
                func.count().label("checkouts")
            ).join(Checkout).filter(
                Checkout.checkout_date >= start_date
            ).group_by(Tool.category).all()

            tool_usage_data = [{"name": t[0] or "General", "checkouts": t[1]} for t in tool_usage]

            # Format response
            result = {
                "departments": department_data,
                "checkoutsByDepartment": checkouts_by_dept,
                "toolUsageByCategory": tool_usage_data
            }

            return jsonify(result), 200

        except Exception:
            logger.exception("Error in department usage report")
            return jsonify({
                "error": "An error occurred while generating the department usage report"
            }), 500

    # Cycle Count Accuracy Report
    @app.route("/api/reports/cycle-counts/accuracy", methods=["GET"])
    @tool_manager_required
    def cycle_count_accuracy_report():
        try:
            # Get filter parameters
            request.args.get("timeframe", "month")
            request.args.get("location")
            request.args.get("category")

            # Check if cycle count tables exist and have data
            try:
                # CycleCountResult removed - always return empty report
                # Return empty report structure when no data exists
                result = {
                    "summary": {
                        "total_counts": 0,
                        "accurate_counts": 0,
                        "discrepancy_counts": 0,
                        "accuracy_rate": 0
                    },
                    "by_location": [],
                    "trends": []
                }
                return jsonify(result), 200
            except Exception:
                # If tables don't exist, return empty report
                result = {
                    "summary": {
                        "total_counts": 0,
                        "accurate_counts": 0,
                        "discrepancy_counts": 0,
                        "accuracy_rate": 0
                    },
                    "by_location": [],
                    "trends": []
                }
                return jsonify(result), 200

        except Exception:
            logger.exception("Error in cycle count accuracy report")
            return jsonify({
                "error": "An error occurred while generating the cycle count accuracy report"
            }), 500

    # Cycle Count Discrepancy Report
    @app.route("/api/reports/cycle-counts/discrepancies", methods=["GET"])
    @tool_manager_required
    def cycle_count_discrepancy_report():
        try:
            # Check if cycle count tables exist and have data
            try:
                # CycleCountResult removed - always return empty report
                result = {
                    "discrepancies": [],
                    "summary": {
                        "total_discrepancies": 0,
                        "by_type": []
                    },
                    "trends": []
                }
                return jsonify(result), 200
            except Exception:
                result = {
                    "discrepancies": [],
                    "summary": {
                        "total_discrepancies": 0,
                        "by_type": []
                    },
                    "trends": []
                }
                return jsonify(result), 200

        except Exception:
            logger.exception("Error in cycle count discrepancy report")
            return jsonify({
                "error": "An error occurred while generating the cycle count discrepancy report"
            }), 500

    # Cycle Count Performance Report
    @app.route("/api/reports/cycle-counts/performance", methods=["GET"])
    @tool_manager_required
    def cycle_count_performance_report():
        try:
            # Check if cycle count tables exist and have data
            try:
                # CycleCountBatch removed - always return empty report
                # total_results = CycleCountBatch.query.count()
                if True:  # Always return empty report
                    result = {
                        "batches": [],
                        "summary": {
                            "total_batches": 0,
                            "completed_batches": 0,
                            "average_completion_time_days": 0
                        },
                        "user_performance": [],
                        "trends": []
                    }
                    return jsonify(result), 200
            except Exception:
                result = {
                    "batches": [],
                    "summary": {
                        "total_batches": 0,
                        "completed_batches": 0,
                        "average_completion_time_days": 0
                    },
                    "user_performance": [],
                    "trends": []
                }
                return jsonify(result), 200

        except Exception:
            logger.exception("Error in cycle count performance report")
            return jsonify({
                "error": "An error occurred while generating the cycle count performance report"
            }), 500

    # Cycle Count Coverage Report
    @app.route("/api/reports/cycle-counts/coverage", methods=["GET"])
    @tool_manager_required
    def cycle_count_coverage_report():
        try:
            # Check if cycle count tables exist and have data
            try:
                # CycleCountResult removed - always return empty report
                result = {
                    "summary": {
                        "total_inventory": Tool.query.count(),
                        "counted_items": 0,
                        "uncounted_items": Tool.query.count(),
                        "coverage_rate": 0
                    },
                    "uncounted_items": [],
                    "by_location": [],
                    "trends": []
                }
                return jsonify(result), 200
            except Exception:
                result = {
                    "summary": {
                        "total_inventory": 0,
                        "counted_items": 0,
                        "uncounted_items": 0,
                        "coverage_rate": 0
                    },
                    "uncounted_items": [],
                    "by_location": [],
                    "trends": []
                }
                return jsonify(result), 200

        except Exception:
            logger.exception("Error in cycle count coverage report")
            return jsonify({
                "error": "An error occurred while generating the cycle count coverage report"
            }), 500
