# Utils package for SupplyLine MRO Suite

import logging

logger = logging.getLogger(__name__)

try:
    # Import from the main utils.py file (not the utils package)
    import sys
    import os
    import importlib.util

    # Get the backend directory path
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    utils_file_path = os.path.join(backend_dir, 'utils.py')

    if os.path.exists(utils_file_path):
        # Load the utils module directly from file path
        spec = importlib.util.spec_from_file_location("root_utils", utils_file_path)
        root_utils = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(root_utils)

        validate_password_strength = root_utils.validate_password_strength
        calculate_password_strength = root_utils.calculate_password_strength
        logger.info("Successfully imported password validation functions from utils.py")
        __all__ = ['validate_password_strength', 'calculate_password_strength']
    else:
        raise ImportError(f"utils.py not found at {utils_file_path}")

except (ImportError, AttributeError) as e:
    # Fallback with security warning - fail secure by default
    logger.error(f"Falling back to dummy password validation - strong-password checks DISABLED. Error: {e}")

    def validate_password_strength(password):
        logger.error("Password validation unavailable - refusing by default")
        return False, ["Password validation unavailable - refusing by default"]

    def calculate_password_strength(password):
        return {'score': 0, 'strength': 'unavailable', 'feedback': ['Password validation unavailable']}

    __all__ = ['validate_password_strength', 'calculate_password_strength']
