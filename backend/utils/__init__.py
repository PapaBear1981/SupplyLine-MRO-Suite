# Utils package for SupplyLine MRO Suite

import logging

logger = logging.getLogger(__name__)

try:
    # Import from the main utils.py file (not the utils package)
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    import utils as root_utils
    validate_password_strength = root_utils.validate_password_strength
    calculate_password_strength = root_utils.calculate_password_strength
    __all__ = ['validate_password_strength', 'calculate_password_strength']
except (ImportError, AttributeError):
    # Fallback with security warning - fail secure by default
    logger.error("Falling back to dummy password validation - strong-password checks DISABLED")

    def validate_password_strength(password):
        logger.error("Password validation unavailable - refusing by default")
        return False, ["Password validation unavailable - refusing by default"]

    def calculate_password_strength(password):
        return {'score': 0, 'strength': 'unavailable', 'feedback': ['Password validation unavailable']}

    __all__ = ['validate_password_strength', 'calculate_password_strength']
