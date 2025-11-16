================================================================================
COMPLETE TEST INVENTORY AND ORGANIZATION
SupplyLine-MRO-Suite Pytest System
================================================================================

FILE: /backend/tests/test_auth.py (18 tests, 8.9 KB)
Purpose: JWT authentication and login functionality
Test Classes and Functions:
  - TestJWTAuthentication
    - test_login_success: Valid credentials login
    - test_login_failure_invalid_credentials: Wrong password rejection
    - test_login_failure_invalid_employee: Non-existent employee rejection
    - test_login_includes_tokens: Token generation in response
    - test_logout: Session termination
    - test_logout_clears_cookies: Cookie removal on logout
    - test_repeated_logout: Safe handling of repeated logout
    - test_token_in_request_headers: Token usage in API requests
    - test_invalid_token_rejected: Malformed token rejection
    - test_expired_token_handling: Expired token detection
    - test_token_refresh: Token renewal mechanism
    - test_token_payload_contains_user_id: Token claim validation
    - test_token_payload_contains_expiration: Token expiry in claims
    - test_multiple_concurrent_logins: Multiple session handling
    - test_admin_user_login: Admin authentication
    - test_regular_user_login: Non-admin authentication
    - test_login_preserves_user_details: User info in token
    - test_session_creation_on_login: Session initialization

Key Dependencies: auth, models, db

================================================================================

FILE: /backend/tests/test_auth_security.py (11 tests, 13 KB)
Purpose: JWT token security and expiration
Test Classes and Functions:
  - TestTokenExpiration
    - test_token_expiration_time: Token lifetime validation
    - test_expired_token_rejected: Expired token handling
    - test_token_expiration_in_claims: Exp claim presence
    - test_token_refresh_creates_new_token: Refresh mechanism
    - test_refresh_token_validation: Refresh token security
    - test_token_payload_integrity: Payload tampering detection
    - test_invalid_signature_rejected: Signature verification
    - test_missing_required_claims: Claim validation
    - test_token_type_validation: Token type checking
    - test_algorithm_validation: Algorithm verification
    - test_token_scope_validation: Scope/permission checking

Key Dependencies: auth, models, jwt

================================================================================

FILE: /backend/tests/test_authorization.py (10 tests, 13 KB)
Purpose: Role-Based Access Control (RBAC) and permissions
Test Classes and Functions:
  - TestRoleBasedAccess
    - test_admin_has_all_permissions: Admin privilege checking
    - test_regular_user_limited_permissions: User privilege restriction
    - test_permission_assignment: Role permission assignment
    - test_permission_checking_decorator: Permission validation
    - test_multiple_roles_combined_permissions: Multi-role handling
    - test_permission_inheritance: Role hierarchy
    - test_department_restricted_access: Department-based access
    - test_admin_can_modify_permissions: Admin permission management
    - test_user_cannot_modify_permissions: Permission modification restriction
    - test_permission_caching: Performance optimization

Key Dependencies: models, db

================================================================================

FILE: /backend/tests/test_input_validation.py (9 tests, 12 KB)
Purpose: Security-focused input validation and injection prevention
Test Classes and Functions:
  - TestSQLInjectionPrevention
    - test_login_sql_injection: SQL injection in login
    - test_search_sql_injection: SQL injection in search
    - test_batch_operation_sql_injection: SQL injection in batch ops
  - TestXSSPrevention
    - test_search_xss_prevention: XSS in search fields
    - test_field_xss_prevention: XSS in data fields
    - test_comment_xss_prevention: XSS in comments
  - TestDataValidation
    - test_email_format_validation: Email validation
    - test_phone_number_validation: Phone validation
    - test_url_validation: URL validation

Key Dependencies: models, security

================================================================================

FILE: /backend/tests/test_rate_limiting.py (11 tests, 12 KB)
Purpose: DoS and brute force protection
Test Classes and Functions:
  - TestLoginRateLimiting
    - test_login_brute_force_protection: Multiple failed login blocking
    - test_login_rate_limit_reset: Rate limit reset after timeout
    - test_rate_limit_header: Rate limit response headers
    - test_rate_limit_threshold: Threshold validation
  - TestAPIRateLimiting
    - test_api_request_rate_limiting: API call limiting
    - test_rate_limit_per_ip: IP-based rate limiting
    - test_rate_limit_per_user: User-based rate limiting
    - test_rate_limit_bypass_invalid: Invalid bypass rejection
  - TestDoSProtection
    - test_large_payload_rejection: Payload size limiting
    - test_query_complexity_limiting: Query complexity protection
    - test_concurrent_request_limiting: Concurrent request limiting

Key Dependencies: models, rate_limiter

================================================================================

FILE: /backend/tests/test_security_assessment.py (8 tests, 12 KB)
Purpose: General security vulnerability assessment
Test Classes and Functions:
  - TestSecurityHeaders: Response header validation
  - TestEndpointSecurity: Endpoint-level security checks
  - TestDataExposure: Sensitive data exposure prevention
  - TestErrorMessages: Error message sanitization

Key Dependencies: app, models

================================================================================

FILE: /backend/tests/test_models.py (15 tests, 13 KB)
Purpose: Core domain model functionality
Test Classes and Functions:
  - TestUserModel
    - test_create_user: User creation
    - test_user_password_hashing: Password hashing
    - test_password_verification: Password checking
    - test_user_permissions: Permission association
    - test_user_is_admin: Admin flag behavior
    - test_user_is_active: Active status
  - TestToolModel
    - test_create_tool: Tool creation
    - test_tool_status_transitions: Status changes
    - test_tool_checkout: Tool issuance
    - test_tool_return: Tool return
  - TestChemicalModel
    - test_create_chemical: Chemical creation
    - test_chemical_quantity_tracking: Quantity management
    - test_chemical_expiry: Expiry handling
  - TestPermissionModel
    - test_permission_creation: Permission setup
    - test_role_creation: Role creation

Key Dependencies: models, db, sqlalchemy

================================================================================

FILE: /backend/tests/test_models_kits.py (22 tests, 27 KB)
Purpose: Kit domain-specific models
Test Classes and Functions:
  - TestAircraftTypeModel
    - test_create_aircraft_type: Aircraft type creation
    - test_aircraft_type_name: Name validation
  - TestKitModel
    - test_create_kit: Kit creation
    - test_kit_status: Status management
    - test_kit_boxes: Box association
    - test_kit_assignment: User assignment
    - test_kit_transfer: Transfer tracking
    - test_kit_reorder: Reorder request
    - test_kit_expiry: Expiry handling
  - TestKitBoxModel
    - test_box_creation: Box creation
    - test_box_contents: Content tracking
    - test_box_organization: Organization structure
  - TestKitExpendableModel
    - test_expendable_creation: Expendable item creation
    - test_expendable_quantity: Quantity tracking
    - test_expendable_consumption: Usage tracking
  - TestKitTransferModel
    - test_transfer_creation: Transfer creation
    - test_transfer_tracking: Transfer history
  - TestKitReorderModel
    - test_reorder_request: Reorder creation
    - test_reorder_status: Status transitions
    - test_reorder_approval: Approval workflow

Key Dependencies: models_kits, models, db

================================================================================

FILE: /backend/tests/test_models_messaging.py (18 tests, 14 KB)
Purpose: Real-time messaging and communication models
Test Classes and Functions:
  - TestChannelModel
    - test_channel_creation: Channel creation
    - test_channel_types: Channel type support
    - test_channel_members: Member management
    - test_channel_permissions: Permission checking
    - test_channel_archival: Channel archiving
  - TestChannelMessageModel
    - test_message_creation: Message storage
    - test_message_timestamp: Timestamp accuracy
    - test_message_editing: Message editing
    - test_message_deletion: Message removal
  - TestChannelMemberModel
    - test_member_addition: Member addition
    - test_member_removal: Member removal
    - test_member_roles: Role assignment
  - TestMessageReactionModel
    - test_reaction_addition: Emoji reaction adding
    - test_reaction_counting: Reaction counting
  - TestUserPresenceModel
    - test_presence_tracking: Online status
    - test_presence_updates: Status updates
    - test_presence_timeout: Session timeout

Key Dependencies: models_messaging, models, models_kits, db

================================================================================

FILE: /backend/tests/test_routes.py (23 tests, 17 KB)
Purpose: General API endpoints and routes
Test Classes and Functions:
  - TestHealthEndpoints
    - test_health_check: Application health
  - TestToolRoutes
    - test_get_tools_authenticated: Tool listing
    - test_create_tool: Tool creation endpoint
    - test_update_tool: Tool updates
    - test_delete_tool: Tool deletion
  - TestChemicalRoutes
    - test_get_chemicals: Chemical listing
    - test_create_chemical: Chemical creation
    - test_update_chemical: Chemical updates
  - TestGeneralEndpoints
    - test_404_not_found: 404 handling
    - test_405_method_not_allowed: 405 handling
    - test_json_content_type: Content type checking
    - test_cors_headers: CORS header presence
    - test_api_versioning: Version handling
    - test_pagination_defaults: Pagination behavior
    - test_search_functionality: Search capability
    - test_filtering_functionality: Filter capability
    - test_sorting_functionality: Sort capability
    - test_export_functionality: Data export
    - test_import_functionality: Data import
    - test_batch_operations: Batch processing
    - test_error_response_format: Error formatting

Key Dependencies: models, db, app

================================================================================

FILE: /backend/tests/test_routes_kits.py (48 tests, 29 KB)
Purpose: Kit management API endpoints
Test Classes and Functions:
  - TestKitCRUD
    - test_create_kit: Kit creation
    - test_get_kit: Kit retrieval
    - test_update_kit: Kit updates
    - test_delete_kit: Kit deletion
    - test_list_kits_pagination: Kit listing with pagination
  - TestKitAssignment
    - test_assign_kit_to_user: Kit assignment
    - test_unassign_kit: Kit unassignment
    - test_kit_allocation_tracking: Allocation tracking
  - TestKitStatus
    - test_kit_status_transitions: Status changes
    - test_kit_in_use: In-use status
    - test_kit_available: Available status
    - test_kit_archived: Archived status
  - TestKitSearch
    - test_search_by_name: Name search
    - test_search_by_aircraft: Aircraft search
    - test_filter_by_status: Status filtering
    - test_filter_by_location: Location filtering
  - TestKitValidation
    - test_kit_name_required: Required field checking
    - test_kit_aircraft_required: Required field checking
    - test_kit_duplicate_prevention: Duplicate prevention
  - TestKitRelations
    - test_kit_boxes_association: Box relationship
    - test_kit_expendables_association: Expendable association
    - test_kit_transfer_history: Transfer tracking
    - test_kit_reorder_history: Reorder tracking
    - test_kit_issuance_history: Issuance tracking
    - And more...

Key Dependencies: models_kits, models, routes_kits

================================================================================

FILE: /backend/tests/test_routes_kit_messages.py (51 tests, 26 KB)
Purpose: Kit real-time messaging endpoints
Test Classes and Functions:
  - TestMessageCRUD
    - test_send_message: Message creation
    - test_get_messages: Message retrieval
    - test_get_message_history: History retrieval
    - test_delete_message: Message deletion
    - test_edit_message: Message editing
  - TestMessageSearch
    - test_search_by_content: Content search
    - test_search_by_author: Author search
    - test_search_by_date: Date search
    - test_search_pagination: Search pagination
  - TestMessageThreads
    - test_create_thread: Thread creation
    - test_thread_nesting: Nested replies
    - test_thread_history: Thread history
  - TestMessageReactions
    - test_add_reaction: Emoji reaction
    - test_remove_reaction: Reaction removal
    - test_reaction_count: Reaction counting
  - TestMessageNotifications
    - test_mention_notifications: @mention notifications
    - test_reply_notifications: Reply notifications
  - TestMessagePermissions
    - test_message_author_can_delete: Author deletion rights
    - test_admin_can_delete_any: Admin rights
    - test_user_cannot_delete_others: Permission restriction
  - And more...

Key Dependencies: models_kits, models, routes_kit_messages

================================================================================

FILE: /backend/tests/test_routes_kit_reorders.py (49 tests, 28 KB)
Purpose: Kit reorder request management
Test Classes and Functions:
  - TestReorderCreation
    - test_create_reorder_request: Request creation
    - test_reorder_validation: Validation checks
    - test_duplicate_prevention: Duplicate prevention
  - TestReorderStatus
    - test_status_pending: Pending status
    - test_status_approved: Approval status
    - test_status_rejected: Rejection handling
    - test_status_completed: Completion status
  - TestReorderWorkflow
    - test_reorder_approval_flow: Approval workflow
    - test_reorder_rejection_flow: Rejection workflow
    - test_reorder_notification: Notification sending
  - TestReorderTracking
    - test_reorder_history: History tracking
    - test_reorder_timeline: Timeline tracking
  - TestReorderPermissions
    - test_user_can_create_reorder: Creation rights
    - test_admin_can_approve: Approval rights
    - test_user_cannot_approve_own: Self-approval prevention
  - TestReorderSearch
    - test_search_by_kit: Kit search
    - test_search_by_status: Status search
    - test_search_by_date: Date search
  - TestReorderValidation
    - test_kit_must_exist: Validation checking
    - test_quantity_required: Quantity validation
  - And more...

Key Dependencies: models_kits, models, routes_kit_reorders

================================================================================

FILE: /backend/tests/test_routes_kit_transfers.py (30 tests, 26 KB)
Purpose: Kit transfer and movement tracking
Test Classes and Functions:
  - TestTransferCreation
    - test_create_transfer: Transfer creation
    - test_transfer_from_location: Location tracking
    - test_transfer_to_location: Location tracking
  - TestTransferStatus
    - test_transfer_in_transit: In-transit status
    - test_transfer_completed: Completed status
    - test_transfer_cancelled: Cancellation handling
  - TestTransferTracking
    - test_transfer_history: History tracking
    - test_transfer_location_changes: Location change tracking
  - TestTransferValidation
    - test_source_location_required: Validation
    - test_destination_location_required: Validation
    - test_kit_must_exist: Validation
  - TestTransferPermissions
    - test_warehouse_staff_can_transfer: Permission checking
    - test_others_cannot_transfer: Restriction checking
  - And more...

Key Dependencies: models_kits, models, routes_kit_transfers

================================================================================

FILE: /backend/tests/test_routes_channels.py (22 tests, 16 KB)
Purpose: Communication channel management
Test Classes and Functions:
  - TestChannelCRUD
    - test_create_channel: Channel creation
    - test_get_channel: Channel retrieval
    - test_update_channel: Channel updates
    - test_delete_channel: Channel deletion
    - test_list_channels: Channel listing
  - TestChannelTypes
    - test_create_department_channel: Department channel
    - test_create_project_channel: Project channel
    - test_create_direct_message: DM creation
  - TestChannelMembers
    - test_add_member: Member addition
    - test_remove_member: Member removal
    - test_list_members: Member listing
  - TestChannelPermissions
    - test_only_creator_can_delete: Deletion rights
    - test_members_can_message: Messaging rights
    - test_non_members_cannot_message: Restriction
  - TestChannelSearch
    - test_search_by_name: Name search
  - And more...

Key Dependencies: models_messaging, models, routes_channels

================================================================================

FILE: /backend/tests/test_routes_orders.py (11 tests, 10 KB)
Purpose: Procurement order management
Test Classes and Functions:
  - TestOrderCreation
    - test_create_order: Order creation
    - test_order_validation: Validation
  - TestOrderStatus
    - test_order_pending: Pending status
    - test_order_confirmed: Confirmation
    - test_order_delivered: Delivery tracking
  - TestOrderTracking
    - test_order_history: History tracking
  - And more...

Key Dependencies: models, routes_orders

================================================================================

FILE: /backend/tests/test_kit_workflows.py (6 tests, 22 KB)
Purpose: End-to-end kit workflow integration tests
Test Classes and Functions:
  - TestKitWorkflows
    - test_complete_kit_creation_workflow: Complete kit creation
    - test_kit_assignment_workflow: Full assignment flow
    - test_kit_reorder_workflow: Complete reorder process
    - test_kit_transfer_workflow: Complete transfer process
    - test_multi_step_kit_operations: Multi-step operations
    - test_kit_messaging_workflow: Messaging integration

Key Dependencies: models_kits, models, all routes_kit_*.py

================================================================================

FILE: /backend/tests/test_no_sessions.py (1 test, 1.9 KB)
Purpose: Session-less operation testing
Test Classes and Functions:
  - TestNoSessions
    - test_application_runs_without_sessions: Session-free operation

Key Dependencies: app, config, models

================================================================================

FILE: /backend/tests/test_issue_410_secret_keys.py (6 tests, 12 KB)
Purpose: Issue #410 - Secret key management regression tests
Test Classes and Functions:
  - TestSecretKeyManagement
    - test_secret_key_in_environment: Environment variable
    - test_jwt_secret_key_separate: JWT key separation
    - test_secret_key_not_in_code: Code security
    - test_secret_key_length: Key length validation
    - test_secret_key_rotation: Key rotation
    - test_different_envs_different_keys: Environment isolation

Key Dependencies: config, security_config

================================================================================

FILE: /backend/tests/test_issue_411_password_reset.py (9 tests, 11 KB)
Purpose: Issue #411 - Password reset security regression tests
Test Classes and Functions:
  - TestPasswordReset
    - test_password_reset_token_generation: Token creation
    - test_password_reset_token_expiry: Token expiry
    - test_password_reset_with_valid_token: Valid reset
    - test_password_reset_with_expired_token: Expired token
    - test_password_reset_with_invalid_token: Invalid token
    - test_password_reset_rate_limiting: Rate limiting
    - test_password_reset_notification: Email notification
    - test_password_reset_invalidates_old_tokens: Token invalidation
    - test_password_reset_forces_relogin: Login requirement

Key Dependencies: utils/password_reset_security, models, rate_limiter

================================================================================

FILE: /backend/tests/test_issue_412_weak_token.py (6 tests, 6.1 KB)
Purpose: Issue #412 - Weak token detection regression tests
Test Classes and Functions:
  - TestWeakTokenDetection
    - test_detect_short_tokens: Short token detection
    - test_detect_poorly_randomized_tokens: Randomness check
    - test_detect_predictable_patterns: Pattern detection
    - test_token_strength_validation: Strength validation
    - test_token_entropy_check: Entropy validation
    - test_reject_weak_tokens: Weak token rejection

Key Dependencies: auth, models

================================================================================

FILE: /backend/tests/test_issue_413_dependencies.py (14 tests, 6.1 KB)
Purpose: Issue #413 - Dependency compatibility regression tests
Test Classes and Functions:
  - TestDependencyVersions
    - test_flask_version: Flask version check
    - test_sqlalchemy_version: SQLAlchemy version
    - test_jwt_version: JWT library version
    - test_python_version: Python compatibility
    - test_all_dependencies_installed: Dependency presence
    - test_no_version_conflicts: Conflict detection
    - test_security_patches_applied: Security update checking
    - And more...

Key Dependencies: importlib.metadata, app

================================================================================

FILE: /backend/tests/test_issue_415_file_validation.py (6 tests, 5.6 KB)
Purpose: Issue #415 - File upload validation regression tests
Test Classes and Functions:
  - TestFileValidation
    - test_file_size_limit: Size validation
    - test_file_type_validation: Type checking
    - test_malicious_file_rejection: Malware prevention
    - test_file_extension_validation: Extension checking
    - test_mime_type_validation: MIME type checking
    - test_virus_scan_integration: Virus scanning

Key Dependencies: utils/file_validation, models

================================================================================

FIXTURE SUMMARY (from conftest.py - 557 lines)
================================================================================

Session-level Fixtures:
  - app: Flask application with test configuration
  - _db: Database session with cleanup and table management

Function-level Fixtures:
  - db_session: Clean database session for each test
  - client: Flask test client for HTTP requests
  - jwt_manager: JWT authentication manager instance
  - admin_user: Pre-created admin user (ADMIN001)
  - test_user: Non-admin test user (USER001)
  - regular_user: Alias for non-admin user
  - test_warehouse: Test warehouse instance
  - sample_tool: Sample tool for testing
  - sample_chemical: Sample chemical for testing
  - auth_headers: Authorization headers for admin user
  - user_auth_headers: Authorization headers for regular user
  - materials_user: Materials department user
  - auth_headers_materials: Materials user auth headers
  - auth_headers_return_manager: Return manager role auth headers
  - auth_headers_requests_user: Requests page permission auth headers
  - sample_data: Comprehensive sample data (tools, chemicals, activities)
  - test_utils: TestUtils utility class with helper methods
  - test_user_2: Second test user for multi-user testing
  - test_channel: Test communication channel
  - test_kit: Test kit with aircraft type

Test Utilities (TestUtils class):
  - assert_json_response(response, expected_status)
  - assert_error_response(response, expected_status)
  - create_test_user(db_session, employee_number, name, is_admin)

================================================================================

PYTEST CONFIGURATION (pytest.ini)
================================================================================

Test Discovery:
  - testpaths: tests/
  - python_files: test_*.py
  - python_classes: Test*
  - python_functions: test_*

Output Options:
  - -v: Verbose output
  - --tb=short: Short traceback format
  - --strict-markers: Enforce marker registration
  - --disable-warnings: Suppress warnings
  - --color=yes: Colored output
  - --durations=10: Show 10 slowest tests

Markers Defined:
  - slow: Marks slow tests
  - integration: Integration tests
  - unit: Unit tests
  - auth: Authentication-related tests
  - api: API endpoint tests
  - models: Database model tests

Filtered Warnings:
  - DeprecationWarning ignored
  - PendingDeprecationWarning ignored

================================================================================

TOTAL TEST STATISTICS
================================================================================

Test Files: 23
Test Functions: 404
Test Code Lines: 9,638
Source Code Files: 75
Source Code Lines: ~19,602

Coverage by Category:
  - Models: 100% (3/3 tested)
  - Routes: 26% (7/27 tested)
  - Security: 0% (0/2 tested)
  - Utilities: 9% (2/23 tested)
  - Auth: 100% (1/1 tested)
  - Other: 17% (1/6 tested)

Overall Coverage: 19% of source files have dedicated tests

================================================================================
