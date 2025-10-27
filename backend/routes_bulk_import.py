"""
Bulk import routes for tools and chemicals
"""
import logging
from functools import wraps

from flask import current_app, jsonify, make_response, request

from auth import admin_required as auth_admin_required
from utils.bulk_import import (
    BulkImportError,
    bulk_import_chemicals,
    bulk_import_tools,
    generate_chemical_template,
    generate_tool_template,
)
from utils.file_validation import FileValidationError, validate_csv_upload
from utils.validation import ValidationError


logger = logging.getLogger(__name__)


def handle_errors(f):
    """Decorator to handle common errors in bulk import routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {f.__name__}: {e!s}")
            return jsonify({"error": str(e)}), 400
        except BulkImportError as e:
            logger.error(f"Bulk import error in {f.__name__}: {e!s}")
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e!s}")
            return jsonify({"error": "An unexpected error occurred"}), 500
    return decorated_function


# Use the admin_required decorator from auth module
admin_required = auth_admin_required


def register_bulk_import_routes(app):
    """Register bulk import routes"""

    @app.route("/api/tools/bulk-import/template", methods=["GET"])
    @admin_required
    @handle_errors
    def download_tool_template():
        """Download CSV template for tool bulk import"""
        try:
            template_content = generate_tool_template()

            response = make_response(template_content)
            response.headers["Content-Type"] = "text/csv"
            response.headers["Content-Disposition"] = "attachment; filename=tool_import_template.csv"

            logger.info("Tool import template downloaded")
            return response

        except Exception as e:
            logger.error(f"Error generating tool template: {e!s}")
            return jsonify({"error": "Failed to generate template"}), 500

    @app.route("/api/chemicals/bulk-import/template", methods=["GET"])
    @admin_required
    @handle_errors
    def download_chemical_template():
        """Download CSV template for chemical bulk import"""
        try:
            template_content = generate_chemical_template()

            response = make_response(template_content)
            response.headers["Content-Type"] = "text/csv"
            response.headers["Content-Disposition"] = "attachment; filename=chemical_import_template.csv"

            logger.info("Chemical import template downloaded")
            return response

        except Exception as e:
            logger.error(f"Error generating chemical template: {e!s}")
            return jsonify({"error": "Failed to generate template"}), 500

    @app.route("/api/tools/bulk-import", methods=["POST"])
    @admin_required
    @handle_errors
    def bulk_import_tools_route():
        """Bulk import tools from CSV file"""
        try:
            # Check if file was uploaded
            if "file" not in request.files:
                return jsonify({"error": "No file uploaded"}), 400

            file = request.files["file"]
            if file.filename == "":
                return jsonify({"error": "No file selected"}), 400

            try:
                max_size = current_app.config.get("MAX_BULK_IMPORT_FILE_SIZE")
                validate_csv_upload(file, max_size=max_size)
            except FileValidationError as exc:
                return jsonify({"error": str(exc)}), getattr(exc, "status_code", 400)

            # Get import options
            skip_duplicates = request.form.get("skip_duplicates", "true").lower() == "true"

            # Read file content
            try:
                csv_content = file.read().decode("utf-8")
            except UnicodeDecodeError:
                try:
                    # Try with different encoding
                    file.seek(0)
                    csv_content = file.read().decode("latin-1")
                except Exception as e:
                    logger.error(f"Error reading CSV file: {e!s}")
                    return jsonify({"error": "Unable to read CSV file. Please ensure it is properly encoded."}), 400

            if not csv_content.strip():
                return jsonify({"error": "CSV file is empty"}), 400

            # PERFORMANCE: Validate row count to prevent excessive processing
            row_count = len(csv_content.strip().split("\n")) - 1  # Subtract header row
            max_rows = current_app.config.get("MAX_BULK_IMPORT_ROWS", 10000)
            if row_count > max_rows:
                return jsonify({
                    "error": f"CSV file contains too many rows ({row_count}). Maximum allowed: {max_rows}"
                }), 400

            # Perform bulk import
            logger.info(f"Starting bulk import of {row_count} tools, skip_duplicates={skip_duplicates}")
            result = bulk_import_tools(csv_content, skip_duplicates=skip_duplicates)

            # Log results
            logger.info(f"Bulk import completed: {result.success_count} success, {result.error_count} errors")

            # Return results
            response_data = result.to_dict()
            response_data["message"] = f"Import completed: {result.success_count} tools imported successfully"

            if result.error_count > 0:
                response_data["message"] += f", {result.error_count} errors occurred"

            if len(result.skipped_items) > 0:
                response_data["message"] += f", {len(result.skipped_items)} items skipped"

            # Return appropriate status code
            if result.error_count > 0 and result.success_count == 0:
                return jsonify(response_data), 400
            if result.error_count > 0:
                return jsonify(response_data), 207  # Multi-status
            return jsonify(response_data), 200

        except Exception as e:
            logger.error(f"Unexpected error in bulk import tools: {e!s}")
            return jsonify({"error": "An unexpected error occurred during import"}), 500

    @app.route("/api/chemicals/bulk-import", methods=["POST"])
    @admin_required
    @handle_errors
    def bulk_import_chemicals_route():
        """Bulk import chemicals from CSV file"""
        try:
            # Check if file was uploaded
            if "file" not in request.files:
                return jsonify({"error": "No file uploaded"}), 400

            file = request.files["file"]
            if file.filename == "":
                return jsonify({"error": "No file selected"}), 400

            try:
                max_size = current_app.config.get("MAX_BULK_IMPORT_FILE_SIZE")
                validate_csv_upload(file, max_size=max_size)
            except FileValidationError as exc:
                return jsonify({"error": str(exc)}), getattr(exc, "status_code", 400)

            # Get import options
            skip_duplicates = request.form.get("skip_duplicates", "true").lower() == "true"

            # Read file content
            try:
                csv_content = file.read().decode("utf-8")
            except UnicodeDecodeError:
                try:
                    # Try with different encoding
                    file.seek(0)
                    csv_content = file.read().decode("latin-1")
                except Exception as e:
                    logger.error(f"Error reading CSV file: {e!s}")
                    return jsonify({"error": "Unable to read CSV file. Please ensure it is properly encoded."}), 400

            if not csv_content.strip():
                return jsonify({"error": "CSV file is empty"}), 400

            # PERFORMANCE: Validate row count to prevent excessive processing
            row_count = len(csv_content.strip().split("\n")) - 1  # Subtract header row
            max_rows = current_app.config.get("MAX_BULK_IMPORT_ROWS", 10000)
            if row_count > max_rows:
                return jsonify({
                    "error": f"CSV file contains too many rows ({row_count}). Maximum allowed: {max_rows}"
                }), 400

            # Perform bulk import
            logger.info(f"Starting bulk import of {row_count} chemicals, skip_duplicates={skip_duplicates}")
            result = bulk_import_chemicals(csv_content, skip_duplicates=skip_duplicates)

            # Log results
            logger.info(f"Bulk import completed: {result.success_count} success, {result.error_count} errors")

            # Return results
            response_data = result.to_dict()
            response_data["message"] = f"Import completed: {result.success_count} chemicals imported successfully"

            if result.error_count > 0:
                response_data["message"] += f", {result.error_count} errors occurred"

            if len(result.skipped_items) > 0:
                response_data["message"] += f", {len(result.skipped_items)} items skipped"

            # Return appropriate status code
            if result.error_count > 0 and result.success_count == 0:
                return jsonify(response_data), 400
            if result.error_count > 0:
                return jsonify(response_data), 207  # Multi-status
            return jsonify(response_data), 200

        except Exception as e:
            logger.error(f"Unexpected error in bulk import chemicals: {e!s}")
            return jsonify({"error": "An unexpected error occurred during import"}), 500

    @app.route("/api/bulk-import/validate", methods=["POST"])
    @admin_required
    @handle_errors
    def validate_bulk_import():
        """Validate CSV file without importing (preview mode)"""
        try:
            # Check if file was uploaded
            if "file" not in request.files:
                return jsonify({"error": "No file uploaded"}), 400

            file = request.files["file"]
            if file.filename == "":
                return jsonify({"error": "No file selected"}), 400

            # Check file type
            if not file.filename.lower().endswith(".csv"):
                return jsonify({"error": "Only CSV files are supported"}), 400

            # Get import type
            import_type = request.form.get("type", "tools")  # 'tools' or 'chemicals'

            # Read file content
            try:
                csv_content = file.read().decode("utf-8")
            except UnicodeDecodeError:
                try:
                    # Try with different encoding
                    file.seek(0)
                    csv_content = file.read().decode("latin-1")
                except Exception as e:
                    logger.error(f"Error reading CSV file: {e!s}")
                    return jsonify({"error": "Unable to read CSV file. Please ensure it is properly encoded."}), 400

            if not csv_content.strip():
                return jsonify({"error": "CSV file is empty"}), 400

            # Perform validation only (no database operations)
            if import_type == "tools":
                from utils.bulk_import import check_duplicate_tool, parse_csv_content, validate_tool_data
                expected_headers = ["tool_number", "serial_number", "description"]
                rows, parse_errors = parse_csv_content(csv_content, expected_headers)

                validation_results = {
                    "valid_rows": 0,
                    "invalid_rows": 0,
                    "duplicate_rows": 0,
                    "errors": parse_errors,
                    "sample_data": []
                }

                if not parse_errors:
                    for row in rows[:10]:  # Preview first 10 rows
                        row_number = row.pop("_row_number")
                        try:
                            tool_data = validate_tool_data(row)
                            existing = check_duplicate_tool(tool_data)

                            validation_results["sample_data"].append({
                                "row": row_number,
                                "data": tool_data,
                                "is_duplicate": existing is not None,
                                "valid": True
                            })

                            if existing:
                                validation_results["duplicate_rows"] += 1
                            else:
                                validation_results["valid_rows"] += 1

                        except Exception as e:
                            validation_results["sample_data"].append({
                                "row": row_number,
                                "data": row,
                                "error": str(e),
                                "valid": False
                            })
                            validation_results["invalid_rows"] += 1

            elif import_type == "chemicals":
                from utils.bulk_import import check_duplicate_chemical, parse_csv_content, validate_chemical_data
                expected_headers = ["part_number", "lot_number", "quantity", "unit"]
                rows, parse_errors = parse_csv_content(csv_content, expected_headers)

                validation_results = {
                    "valid_rows": 0,
                    "invalid_rows": 0,
                    "duplicate_rows": 0,
                    "errors": parse_errors,
                    "sample_data": []
                }

                if not parse_errors:
                    for row in rows[:10]:  # Preview first 10 rows
                        row_number = row.pop("_row_number")
                        try:
                            chemical_data = validate_chemical_data(row)
                            existing = check_duplicate_chemical(chemical_data)

                            validation_results["sample_data"].append({
                                "row": row_number,
                                "data": chemical_data,
                                "is_duplicate": existing is not None,
                                "valid": True
                            })

                            if existing:
                                validation_results["duplicate_rows"] += 1
                            else:
                                validation_results["valid_rows"] += 1

                        except Exception as e:
                            validation_results["sample_data"].append({
                                "row": row_number,
                                "data": row,
                                "error": str(e),
                                "valid": False
                            })
                            validation_results["invalid_rows"] += 1

            else:
                return jsonify({"error": 'Invalid import type. Must be "tools" or "chemicals"'}), 400

            return jsonify(validation_results), 200

        except Exception as e:
            logger.error(f"Unexpected error in validate bulk import: {e!s}")
            return jsonify({"error": "An unexpected error occurred during validation"}), 500
