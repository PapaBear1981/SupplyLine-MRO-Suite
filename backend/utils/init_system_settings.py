"""
Initialize default system settings in the database
"""

from models import db, SystemSettings, get_current_time
import logging

logger = logging.getLogger(__name__)

def initialize_default_settings():
    """Initialize default system settings if they don't exist"""
    
    default_settings = [
        # General Settings
        {
            'key': 'company_name',
            'value': 'SupplyLine MRO Suite',
            'value_type': 'string',
            'description': 'Company name displayed in the application',
            'category': 'general',
            'is_system': True
        },
        {
            'key': 'default_department',
            'value': 'Maintenance',
            'value_type': 'string',
            'description': 'Default department for new users',
            'category': 'general',
            'is_system': True
        },
        
        # Tool Settings
        {
            'key': 'tool_checkout_duration',
            'value': '7',
            'value_type': 'integer',
            'description': 'Default tool checkout duration in days',
            'category': 'tools',
            'is_system': True
        },
        
        # Security Settings
        {
            'key': 'auto_logout_timeout',
            'value': '30',
            'value_type': 'integer',
            'description': 'Auto logout timeout in minutes',
            'category': 'security',
            'is_system': True
        },
        {
            'key': 'enable_auto_logout',
            'value': 'true',
            'value_type': 'boolean',
            'description': 'Enable automatic logout on inactivity',
            'category': 'security',
            'is_system': True
        },
        {
            'key': 'logout_on_window_close',
            'value': 'true',
            'value_type': 'boolean',
            'description': 'Automatically logout when browser window is closed',
            'category': 'security',
            'is_system': True
        },
        {
            'key': 'show_logout_warning',
            'value': 'true',
            'value_type': 'boolean',
            'description': 'Show warning before automatic logout',
            'category': 'security',
            'is_system': True
        },
        {
            'key': 'logout_warning_minutes',
            'value': '5',
            'value_type': 'integer',
            'description': 'Minutes before logout to show warning',
            'category': 'security',
            'is_system': True
        },
        
        # Notification Settings
        {
            'key': 'enable_notifications',
            'value': 'true',
            'value_type': 'boolean',
            'description': 'Enable system notifications',
            'category': 'notifications',
            'is_system': True
        },
        {
            'key': 'enable_chemical_alerts',
            'value': 'true',
            'value_type': 'boolean',
            'description': 'Enable chemical expiry alerts',
            'category': 'chemicals',
            'is_system': True
        },
        {
            'key': 'chemical_expiry_threshold',
            'value': '30',
            'value_type': 'integer',
            'description': 'Days before chemical expiry to show alerts',
            'category': 'chemicals',
            'is_system': True
        },
        {
            'key': 'enable_tool_calibration_alerts',
            'value': 'true',
            'value_type': 'boolean',
            'description': 'Enable tool calibration alerts',
            'category': 'tools',
            'is_system': True
        },
        {
            'key': 'calibration_due_threshold',
            'value': '14',
            'value_type': 'integer',
            'description': 'Days before calibration due to show alerts',
            'category': 'tools',
            'is_system': True
        },
        
        # Logging Settings
        {
            'key': 'enable_audit_logging',
            'value': 'true',
            'value_type': 'boolean',
            'description': 'Enable audit logging',
            'category': 'security',
            'is_system': True
        },
        {
            'key': 'enable_user_activity',
            'value': 'true',
            'value_type': 'boolean',
            'description': 'Track user activity',
            'category': 'security',
            'is_system': True
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    try:
        for setting_data in default_settings:
            existing_setting = SystemSettings.query.filter_by(key=setting_data['key']).first()
            
            if existing_setting:
                # Update description and category if they've changed
                if (existing_setting.description != setting_data['description'] or 
                    existing_setting.category != setting_data['category']):
                    existing_setting.description = setting_data['description']
                    existing_setting.category = setting_data['category']
                    updated_count += 1
            else:
                # Create new setting
                new_setting = SystemSettings(
                    key=setting_data['key'],
                    value=setting_data['value'],
                    value_type=setting_data['value_type'],
                    description=setting_data['description'],
                    category=setting_data['category'],
                    is_system=setting_data['is_system']
                )
                db.session.add(new_setting)
                created_count += 1
        
        db.session.commit()
        
        logger.info(f"System settings initialized: {created_count} created, {updated_count} updated")
        return True, f"System settings initialized: {created_count} created, {updated_count} updated"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to initialize system settings: {str(e)}")
        return False, f"Failed to initialize system settings: {str(e)}"

def get_setting_value(key, default=None):
    """Helper function to get a setting value"""
    return SystemSettings.get_setting(key, default)

def update_setting_value(key, value, user_id=None):
    """Helper function to update a setting value"""
    try:
        setting = SystemSettings.query.filter_by(key=key).first()
        if setting:
            setting.set_typed_value(value)
            setting.updated_by = user_id
            setting.updated_at = get_current_time()
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update setting {key}: {str(e)}")
        return False
