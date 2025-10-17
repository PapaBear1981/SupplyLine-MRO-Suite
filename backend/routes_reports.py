from flask import request, jsonify, make_response
from datetime import datetime, timedelta
import logging
from models import db, Tool, User, Checkout
from utils.export_utils import generate_pdf_report, generate_excel_report

logger = logging.getLogger(__name__)


def calculate_date_range(timeframe):
    """Calculate start date based on timeframe parameter."""
    now = datetime.now()
    if timeframe == 'day':
        return now - timedelta(days=1)
    elif timeframe == 'week':
        return now - timedelta(weeks=1)
    elif timeframe == 'month':
        return now - timedelta(days=30)
    elif timeframe == 'quarter':
        return now - timedelta(days=90)
    elif timeframe == 'year':
        return now - timedelta(days=365)
    elif timeframe == 'all':
        return datetime(1970, 1, 1)  # Beginning of time for database purposes
    else:
        return now - timedelta(days=30)  # Default to month
from sqlalchemy import func
from auth import department_required

tool_manager_required = department_required('Materials')


def register_report_routes(app):
    # Export report as PDF
    @app.route('/api/reports/export/pd', methods=['POST'])
    @tool_manager_required
    def export_report_pdf():
        try:
            data = request.get_json()
            report_type = data.get('report_type')
            report_data = data.get('report_data')
            timeframe = data.get('timeframe', 'month')

            if not report_type or not report_data:
                return jsonify({'error': 'Missing report_type or report_data'}), 400

            # Generate PDF using export utilities
            pdf_buffer = generate_pdf_report(report_data, report_type, timeframe)

            # Return PDF as response
            response = make_response(pdf_buffer.getvalue())
            response.headers['Content-Type'] = 'application/pd'
            response.headers['Content-Disposition'] = f'attachment; filename="{report_type}-report.pd"'

            return response

        except Exception:
            logger.exception("Failed to generate PDF report")
            return jsonify({'error': 'Failed to generate PDF'}), 500

    # Export report as Excel
    @app.route('/api/reports/export/excel', methods=['POST'])
    @tool_manager_required
    def export_report_excel():
        try:
            data = request.get_json()
            report_type = data.get('report_type')
            report_data = data.get('report_data')
            timeframe = data.get('timeframe', 'month')

            if not report_type or not report_data:
                return jsonify({'error': 'Missing report_type or report_data'}), 400

            # Generate Excel using export utilities
            excel_buffer = generate_excel_report(report_data, report_type, timeframe)

            # Return Excel as response
            response = make_response(excel_buffer.getvalue())
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename="{report_type}-report.xlsx"'

            return response

        except Exception:
            logger.exception("Failed to generate Excel report")
            return jsonify({'error': 'Failed to generate Excel'}), 500

    # Tool Inventory Report
    @app.route('/api/reports/tools', methods=['GET'])
    @tool_manager_required
    def tool_inventory_report():
        try:
            # Get filter parameters
            category = request.args.get('category')
            status = request.args.get('status')
            location = request.args.get('location')

            # Start with base query
            query = Tool.query

            # Apply filters if provided
            if category:
                query = query.filter(Tool.category == category)

            if status:
                # For 'available' status, we need to check both the tool status and active checkouts
                if status == 'available':
                    # Get IDs of tools that are checked out
                    checked_out_tool_ids = [c.tool_id for c in Checkout.query.filter(Checkout.return_date.is_(None)).all()]
                    # Filter for tools that are not in the checked out list and have status 'available'
                    query = query.filter(~Tool.id.in_(checked_out_tool_ids))
                    query = query.filter(Tool.status.in_(['available', None]))
                elif status == 'checked_out':
                    # Get IDs of tools that are checked out
                    checked_out_tool_ids = [c.tool_id for c in Checkout.query.filter(Checkout.return_date.is_(None)).all()]
                    # Filter for tools that are in the checked out list
                    query = query.filter(Tool.id.in_(checked_out_tool_ids))
                else:
                    # For maintenance and retired, just check the tool status
                    query = query.filter(Tool.status == status)

            if location:
                query = query.filter(Tool.location.ilike(f'%{location}%'))

            # Execute query
            tools = query.all()

            # Get checkout status for each tool
            tool_status = {}
            active_checkouts = Checkout.query.filter(Checkout.return_date.is_(None)).all()

            for checkout in active_checkouts:
                tool_status[checkout.tool_id] = 'checked_out'

            # Format response
            result = [{
                'id': t.id,
                'tool_number': t.tool_number,
                'serial_number': t.serial_number,
                'description': t.description,
                'condition': t.condition,
                'location': t.location,
                'category': getattr(t, 'category', 'General'),
                'status': tool_status.get(t.id, getattr(t, 'status', 'available')),
                'status_reason': getattr(t, 'status_reason', None) if getattr(t, 'status', 'available') in ['maintenance', 'retired'] else None,
                'created_at': t.created_at.isoformat()
            } for t in tools]

            return jsonify(result), 200

        except Exception:
            logger.exception("Error in tool inventory report")
            return jsonify({
                'error': 'An error occurred while generating the tool inventory report'
            }), 500

    # Checkout History Report
    @app.route('/api/reports/checkouts', methods=['GET'])
    @tool_manager_required
    def checkout_history_report():
        try:
            # Get timeframe parameter
            timeframe = request.args.get('timeframe', 'month')

            # Get filter parameters
            department = request.args.get('department')
            checkout_status = request.args.get('checkoutStatus')
            tool_category = request.args.get('toolCategory')

            # Calculate date range based on timeframe
            now = datetime.now()
            if timeframe == 'day':
                start_date = now - timedelta(days=1)
            elif timeframe == 'week':
                start_date = now - timedelta(weeks=1)
            elif timeframe == 'month':
                start_date = now - timedelta(days=30)
            elif timeframe == 'quarter':
                start_date = now - timedelta(days=90)
            elif timeframe == 'year':
                start_date = now - timedelta(days=365)
            elif timeframe == 'all':
                start_date = datetime(1970, 1, 1)  # Beginning of time for database purposes
            else:
                start_date = now - timedelta(weeks=1)  # Default to week

            # Start with base query
            query = Checkout.query.filter(Checkout.checkout_date >= start_date)

            # Apply filters if provided
            if department:
                query = query.join(User).filter(User.department == department)

            if checkout_status:
                if checkout_status == 'active':
                    query = query.filter(Checkout.return_date.is_(None))
                elif checkout_status == 'returned':
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
                    if duration < 0:
                        duration = 0  # Handle case where return_date might be before checkout_date due to data issues
                else:
                    duration = (now - c.checkout_date).days

                checkout_data.append({
                    'id': c.id,
                    'tool_id': c.tool_id,
                    'tool_number': c.tool.tool_number if c.tool else 'Unknown',
                    'serial_number': c.tool.serial_number if c.tool else 'Unknown',
                    'description': c.tool.description if c.tool else '',
                    'category': c.tool.category if c.tool else 'General',
                    'user_id': c.user_id,
                    'user_name': c.user.name if c.user else 'Unknown',
                    'department': c.user.department if c.user else 'Unknown',
                    'checkout_date': c.checkout_date.isoformat(),
                    'return_date': c.return_date.isoformat() if c.return_date else None,
                    'expected_return_date': c.expected_return_date.isoformat() if c.expected_return_date else None,
                    'duration': duration
                })

            # Calculate checkout trends by day
            checkout_trends = db.session.query(
                func.date(Checkout.checkout_date).label('date'),
                func.count().label('checkouts')
            ).filter(
                Checkout.checkout_date >= start_date
            ).group_by(
                func.date(Checkout.checkout_date)
            ).all()

            return_trends = db.session.query(
                func.date(Checkout.return_date).label('date'),
                func.count().label('returns')
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
                if isinstance(date, str):
                    date_str = date
                else:
                    date_str = date.strftime('%Y-%m-%d')

                if date_str not in date_data:
                    date_data[date_str] = {'date': date_str, 'checkouts': 0, 'returns': 0}
                date_data[date_str]['checkouts'] = count

            for date, count in return_trends:
                # Handle case where date might be a string or a datetime object
                if isinstance(date, str):
                    date_str = date
                else:
                    date_str = date.strftime('%Y-%m-%d')

                if date_str not in date_data:
                    date_data[date_str] = {'date': date_str, 'checkouts': 0, 'returns': 0}
                date_data[date_str]['returns'] = count

            # Convert to list and sort by date
            checkout_by_day = sorted(date_data.values(), key=lambda x: x['date'])

            # Calculate summary statistics
            total_checkouts = len(checkouts)
            returned_checkouts = sum(1 for c in checkouts if c.return_date)
            currently_checked_out = total_checkouts - returned_checkouts

            # Calculate average duration for returned checkouts
            durations = [c['duration'] for c in checkout_data if c['return_date']]
            average_duration = sum(durations) / len(durations) if durations else 0

            # Format response
            result = {
                'checkouts': checkout_data,
                'checkoutsByDay': checkout_by_day,
                'stats': {
                    'totalCheckouts': total_checkouts,
                    'returnedCheckouts': returned_checkouts,
                    'currentlyCheckedOut': currently_checked_out,
                    'averageDuration': round(average_duration, 1)
                }
            }

            return jsonify(result), 200

        except Exception:
            logger.exception("Error in checkout history report")
            return jsonify({
                'error': 'An error occurred while generating the checkout history report'
            }), 500

    # Department Usage Report
    @app.route('/api/reports/departments', methods=['GET'])
    @tool_manager_required
    def department_usage_report():
        try:
            # Get timeframe parameter
            timeframe = request.args.get('timeframe', 'month')

            # Calculate date range based on timeframe
            now = datetime.now()
            if timeframe == 'day':
                start_date = now - timedelta(days=1)
            elif timeframe == 'week':
                start_date = now - timedelta(weeks=1)
            elif timeframe == 'month':
                start_date = now - timedelta(days=30)
            elif timeframe == 'quarter':
                start_date = now - timedelta(days=90)
            elif timeframe == 'year':
                start_date = now - timedelta(days=365)
            elif timeframe == 'all':
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
                            if duration < 0:
                                duration = 0  # Handle case where return_date might be before checkout_date
                            durations.append(duration)
                        except Exception:
                            logger.exception("Error calculating checkout duration for department usage report")
                            # Skip this checkout if there's an error

                average_duration = sum(durations) / len(durations) if durations else 0

                # Find most used tool category for this department
                tool_categories = {}
                for c in dept_checkouts:
                    category = c.tool.category if c.tool and hasattr(c.tool, 'category') else 'General'
                    tool_categories[category] = tool_categories.get(category, 0) + 1

                most_used_category = max(tool_categories.items(), key=lambda x: x[1])[0] if tool_categories else None

                # Add department data
                department_data.append({
                    'name': dept,
                    'totalCheckouts': total_checkouts,
                    'currentlyCheckedOut': currently_checked_out,
                    'averageDuration': round(average_duration, 1),
                    'mostUsedCategory': most_used_category
                })

            # Sort departments by total checkouts
            department_data.sort(key=lambda x: x['totalCheckouts'], reverse=True)

            # Calculate checkouts by department for pie chart
            checkouts_by_dept = [{'name': d['name'], 'value': d['totalCheckouts']} for d in department_data]

            # Calculate tool usage by category
            tool_usage = db.session.query(
                Tool.category,
                func.count().label('checkouts')
            ).join(Checkout).filter(
                Checkout.checkout_date >= start_date
            ).group_by(Tool.category).all()

            tool_usage_data = [{'name': t[0] or 'General', 'checkouts': t[1]} for t in tool_usage]

            # Format response
            result = {
                'departments': department_data,
                'checkoutsByDepartment': checkouts_by_dept,
                'toolUsageByCategory': tool_usage_data
            }

            return jsonify(result), 200

        except Exception:
            logger.exception("Error in department usage report")
            return jsonify({
                'error': 'An error occurred while generating the department usage report'
            }), 500

    # Cycle Count Accuracy Report
    @app.route('/api/reports/cycle-counts/accuracy', methods=['GET'])
    @tool_manager_required
    def cycle_count_accuracy_report():
        try:
            # Get filter parameters
            timeframe = request.args.get('timeframe', 'month')
            location = request.args.get('location')
            category = request.args.get('category')

            # Check if cycle count tables exist and have data
            try:
                # Simple check to see if we have any cycle count data
#                 total_results = CycleCountResult.query.count()  # FIXME: CycleCountResult removed
                if total_results == 0:
                    # Return empty report structure when no data exists
                    result = {
                        'summary': {
                            'total_counts': 0,
                            'accurate_counts': 0,
                            'discrepancy_counts': 0,
                            'accuracy_rate': 0
                        },
                        'by_location': [],
                        'trends': []
                    }
                    return jsonify(result), 200
            except Exception:
                # If tables don't exist, return empty report
                result = {
                    'summary': {
                        'total_counts': 0,
                        'accurate_counts': 0,
                        'discrepancy_counts': 0,
                        'accuracy_rate': 0
                    },
                    'by_location': [],
                    'trends': []
                }
                return jsonify(result), 200

            # Calculate date range based on timeframe
            calculate_date_range(timeframe)

            # Get all cycle count results within the timeframe
#             query = CycleCountResult.query.filter(CycleCountResult.counted_at >= start_date)  # FIXME: CycleCountResult removed

            # Join with items to get additional filtering options
            query = query.join(CycleCountItem)

            # Apply filters if provided
            if location:
                query = query.filter(CycleCountItem.expected_location.ilike(f'%{location}%'))

            if category:
                # Filter by tool category (assuming most items are tools)
                query = query.join(Tool, CycleCountItem.item_id == Tool.id).filter(
                    CycleCountItem.item_type == 'tool',
                    Tool.category == category
                )

            results = query.all()

            # Calculate accuracy metrics
            total_counts = len(results)
            accurate_counts = sum(1 for r in results if not r.has_discrepancy)
            discrepancy_counts = total_counts - accurate_counts

            accuracy_rate = (accurate_counts / total_counts * 100) if total_counts > 0 else 0

            # Calculate accuracy by location
            location_accuracy = {}
            for result in results:
                loc = result.item.expected_location or 'Unknown'
                if loc not in location_accuracy:
                    location_accuracy[loc] = {'total': 0, 'accurate': 0}
                location_accuracy[loc]['total'] += 1
                if not result.has_discrepancy:
                    location_accuracy[loc]['accurate'] += 1

            # Calculate accuracy rate for each location
            location_data = []
            for loc, data in location_accuracy.items():
                rate = (data['accurate'] / data['total'] * 100) if data['total'] > 0 else 0
                location_data.append({
                    'location': loc,
                    'total_counts': data['total'],
                    'accurate_counts': data['accurate'],
                    'accuracy_rate': round(rate, 2)
                })

            # Sort by accuracy rate
            location_data.sort(key=lambda x: x['accuracy_rate'], reverse=True)

            # For trends, just return empty array if no data
            trend_data = []

            # Format response
            result = {
                'summary': {
                    'total_counts': total_counts,
                    'accurate_counts': accurate_counts,
                    'discrepancy_counts': discrepancy_counts,
                    'accuracy_rate': round(accuracy_rate, 2)
                },
                'by_location': location_data,
                'trends': trend_data
            }

            return jsonify(result), 200

        except Exception:
            logger.exception("Error in cycle count accuracy report")
            return jsonify({
                'error': 'An error occurred while generating the cycle count accuracy report'
            }), 500

    # Cycle Count Discrepancy Report
    @app.route('/api/reports/cycle-counts/discrepancies', methods=['GET'])
    @tool_manager_required
    def cycle_count_discrepancy_report():
        try:
            # Check if cycle count tables exist and have data
            try:
#                 total_results = CycleCountResult.query.count()  # FIXME: CycleCountResult removed
                if total_results == 0:
                    result = {
                        'discrepancies': [],
                        'summary': {
                            'total_discrepancies': 0,
                            'by_type': []
                        },
                        'trends': []
                    }
                    return jsonify(result), 200
            except Exception:
                result = {
                    'discrepancies': [],
                    'summary': {
                        'total_discrepancies': 0,
                        'by_type': []
                    },
                    'trends': []
                }
                return jsonify(result), 200

            # Get filter parameters
            timeframe = request.args.get('timeframe', 'month')
            discrepancy_type = request.args.get('discrepancy_type')
            location = request.args.get('location')

            # Calculate date range based on timeframe
            calculate_date_range(timeframe)

            # Get all discrepancy results within the timeframe
            # FIXME: CycleCountResult removed - need to implement alternative
            # query = CycleCountResult.query.filter(
            #     CycleCountResult.counted_at >= start_date,
            #     CycleCountResult.has_discrepancy is True
            # ).join(CycleCountItem)
            query = None  # Placeholder until CycleCountResult is restored

            # Apply filters if provided
            if discrepancy_type:
                # query = query.filter(CycleCountResult.discrepancy_type == discrepancy_type)
                pass

            if location:
                query = query.filter(CycleCountItem.expected_location.ilike(f'%{location}%'))

            # TODO: Complete implementation to include actual discrepancies data from query
            # For now, return empty data structure
            result = {
                'discrepancies': [],
                'summary': {
                    'total_discrepancies': 0,
                    'by_type': []
                },
                'trends': []
            }

            return jsonify(result), 200

        except Exception:
            logger.exception("Error in cycle count discrepancy report")
            return jsonify({
                'error': 'An error occurred while generating the cycle count discrepancy report'
            }), 500

    # Cycle Count Performance Report
    @app.route('/api/reports/cycle-counts/performance', methods=['GET'])
    @tool_manager_required
    def cycle_count_performance_report():
        try:
            # Check if cycle count tables exist and have data
            try:
                total_results = CycleCountBatch.query.count()
                if total_results == 0:
                    result = {
                        'batches': [],
                        'summary': {
                            'total_batches': 0,
                            'completed_batches': 0,
                            'average_completion_time_days': 0
                        },
                        'user_performance': [],
                        'trends': []
                    }
                    return jsonify(result), 200
            except Exception:
                result = {
                    'batches': [],
                    'summary': {
                        'total_batches': 0,
                        'completed_batches': 0,
                        'average_completion_time_days': 0
                    },
                    'user_performance': [],
                    'trends': []
                }
                return jsonify(result), 200
            # Get filter parameters
            timeframe = request.args.get('timeframe', 'month')

            # Calculate date range based on timeframe
            start_date = calculate_date_range(timeframe)

            # Get all batches within the timeframe
            batches = CycleCountBatch.query.filter(
                CycleCountBatch.created_at >= start_date
            ).all()

            # Calculate batch performance metrics
            batch_data = []
            total_completion_time = 0
            completed_batches = 0

            for batch in batches:
                # Get items for this batch
                items = CycleCountItem.query.filter_by(batch_id=batch.id).all()
                total_items = len(items)
                counted_items = sum(1 for item in items if item.status == 'counted')

                completion_rate = (counted_items / total_items * 100) if total_items > 0 else 0

                # Calculate completion time if batch is completed
                completion_time = None
                if batch.status == 'completed' and batch.start_date and batch.end_date:
                    completion_time = (batch.end_date - batch.start_date).days
                    total_completion_time += completion_time
                    completed_batches += 1

                batch_data.append({
                    'id': batch.id,
                    'name': batch.name,
                    'status': batch.status,
                    'start_date': batch.start_date.isoformat() if batch.start_date else None,
                    'end_date': batch.end_date.isoformat() if batch.end_date else None,
                    'total_items': total_items,
                    'counted_items': counted_items,
                    'completion_rate': round(completion_rate, 2),
                    'completion_time_days': completion_time,
                    'created_by': batch.creator.name if batch.creator else 'Unknown'
                })

            # Calculate average completion time
            avg_completion_time = (total_completion_time / completed_batches) if completed_batches > 0 else 0

            # Get performance by user
            user_performance = db.session.query(
#                 CycleCountResult.counted_by,  # FIXME: CycleCountResult removed
                User.name,
                func.count().label('counts_performed'),
#                 func.sum(func.case([(CycleCountResult.has_discrepancy.is_(False), 1)], else_=0)).label('accurate_counts')  # FIXME: CycleCountResult removed
#             ).join(User, CycleCountResult.counted_by == User.id).filter(  # FIXME: CycleCountResult removed
#                 CycleCountResult.counted_at >= start_date  # FIXME: CycleCountResult removed
            ).group_by(
#                 CycleCountResult.counted_by,  # FIXME: CycleCountResult removed
                User.name
            ).all()

            user_data = []
            for user_id, name, total_counts, accurate_counts in user_performance:
                accuracy_rate = (accurate_counts / total_counts * 100) if total_counts > 0 else 0
                user_data.append({
                    'user_id': user_id,
                    'name': name,
                    'counts_performed': total_counts,
                    'accurate_counts': accurate_counts,
                    'accuracy_rate': round(accuracy_rate, 2)
                })

            # Sort by counts performed
            user_data.sort(key=lambda x: x['counts_performed'], reverse=True)

            # Calculate batch completion trends
            batch_trends = db.session.query(
                func.date(CycleCountBatch.created_at).label('date'),
                func.count().label('batches_created'),
                func.sum(func.case([(CycleCountBatch.status == 'completed', 1)], else_=0)).label('batches_completed')
            ).filter(
                CycleCountBatch.created_at >= start_date
            ).group_by(
                func.date(CycleCountBatch.created_at)
            ).all()

            trend_data = []
            for date, created, completed in batch_trends:
                date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
                trend_data.append({
                    'date': date_str,
                    'batches_created': created,
                    'batches_completed': completed
                })

            # Sort by date
            trend_data.sort(key=lambda x: x['date'])

            # Format response
            result = {
                'batches': batch_data,
                'summary': {
                    'total_batches': len(batches),
                    'completed_batches': completed_batches,
                    'average_completion_time_days': round(avg_completion_time, 1)
                },
                'user_performance': user_data,
                'trends': trend_data
            }

            return jsonify(result), 200

        except Exception:
            logger.exception("Error in cycle count performance report")
            return jsonify({
                'error': 'An error occurred while generating the cycle count performance report'
            }), 500

    # Cycle Count Coverage Report
    @app.route('/api/reports/cycle-counts/coverage', methods=['GET'])
    @tool_manager_required
    def cycle_count_coverage_report():
        try:
            # Check if cycle count tables exist and have data
            try:
#                 total_results = CycleCountResult.query.count()  # FIXME: CycleCountResult removed
                if total_results == 0:
                    result = {
                        'summary': {
                            'total_inventory': Tool.query.count(),
                            'counted_items': 0,
                            'uncounted_items': Tool.query.count(),
                            'coverage_rate': 0
                        },
                        'uncounted_items': [],
                        'by_location': [],
                        'trends': []
                    }
                    return jsonify(result), 200
            except Exception:
                result = {
                    'summary': {
                        'total_inventory': 0,
                        'counted_items': 0,
                        'uncounted_items': 0,
                        'coverage_rate': 0
                    },
                    'uncounted_items': [],
                    'by_location': [],
                    'trends': []
                }
                return jsonify(result), 200

            # Get filter parameters
            timeframe = request.args.get('timeframe', 'month')
            item_type = request.args.get('item_type', 'tool')  # tool or chemical

            # Calculate date range based on timeframe
            calculate_date_range(timeframe)

            # Get total inventory count based on item type
            if item_type != 'tool':
                # Currently only tools are supported
                return jsonify({
                    'error': f'Unsupported item_type: {item_type}. Only "tool" is currently supported.'
                }), 400

            total_inventory = Tool.query.count()
            inventory_items = Tool.query.all()

            # Get items that have been counted within the timeframe
            # FIXME: CycleCountResult removed - need to implement alternative
            # counted_items = db.session.query(
            #     CycleCountItem.item_id
            # ).join(CycleCountResult).filter(
            #     CycleCountItem.item_type == item_type,
            #     CycleCountResult.counted_at >= start_date
            # ).distinct().all()
            counted_items = []  # Placeholder

            counted_item_ids = {item_id for (item_id,) in counted_items}
            coverage_count = len(counted_item_ids)
            coverage_rate = (coverage_count / total_inventory * 100) if total_inventory > 0 else 0

            # Get last count dates for all items in a single query
            last_counts = {}
            all_last_counts = db.session.query(
                CycleCountItem.item_id,
#                 func.max(CycleCountResult.counted_at).label('last_counted')  # FIXME: CycleCountResult removed
#             ).join(CycleCountResult).filter(  # FIXME: CycleCountResult removed
                CycleCountItem.item_type == item_type
            ).group_by(CycleCountItem.item_id).all()

            for item_id, last_counted in all_last_counts:
                last_counts[item_id] = last_counted

            # Get items that haven't been counted recently
            uncounted_items = []
            for item in inventory_items:
                if item.id not in counted_item_ids:
                    uncounted_items.append({
                        'id': item.id,
                        'number': getattr(item, 'tool_number', 'N/A'),
                        'serial_number': getattr(item, 'serial_number', 'N/A'),
                        'description': item.description,
                        'location': getattr(item, 'location', 'Unknown'),
                        'category': getattr(item, 'category', 'General'),
                        'last_counted': last_counts.get(item.id).isoformat() if last_counts.get(item.id) else None
                    })

            # Sort uncounted items by last counted date (oldest first)
            uncounted_items.sort(key=lambda x: x['last_counted'] or '1970-01-01')

            # Calculate coverage by location
            location_coverage = {}
            for item in inventory_items:
                location = getattr(item, 'location', 'Unknown')
                if location not in location_coverage:
                    location_coverage[location] = {'total': 0, 'counted': 0}
                location_coverage[location]['total'] += 1
                if item.id in counted_item_ids:
                    location_coverage[location]['counted'] += 1

            location_data = []
            for loc, data in location_coverage.items():
                rate = (data['counted'] / data['total'] * 100) if data['total'] > 0 else 0
                location_data.append({
                    'location': loc,
                    'total_items': data['total'],
                    'counted_items': data['counted'],
                    'coverage_rate': round(rate, 2)
                })

            # Sort by coverage rate
            location_data.sort(key=lambda x: x['coverage_rate'])

            # Calculate coverage trends over time
            coverage_trends = db.session.query(
#                 func.date(CycleCountResult.counted_at).label('date'),  # FIXME: CycleCountResult removed
                func.count(func.distinct(CycleCountItem.item_id)).label('items_counted')
            ).join(CycleCountItem).filter(
                CycleCountItem.item_type == item_type,
#                 CycleCountResult.counted_at >= start_date  # FIXME: CycleCountResult removed
            ).group_by(
#                 func.date(CycleCountResult.counted_at)  # FIXME: CycleCountResult removed
            ).all()

            trend_data = []
            for date, count in coverage_trends:
                date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
                trend_data.append({
                    'date': date_str,
                    'items_counted': count
                })

            # Sort by date
            trend_data.sort(key=lambda x: x['date'])

            # Format response
            result = {
                'summary': {
                    'total_inventory': total_inventory,
                    'counted_items': coverage_count,
                    'uncounted_items': total_inventory - coverage_count,
                    'coverage_rate': round(coverage_rate, 2)
                },
                'uncounted_items': uncounted_items[:50],  # Limit to first 50 for performance
                'by_location': location_data,
                'trends': trend_data
            }

            return jsonify(result), 200

        except Exception:
            logger.exception("Error in cycle count coverage report")
            return jsonify({
                'error': 'An error occurred while generating the cycle count coverage report'
            }), 500
