# Utils package for SupplyLine MRO Suite

# Import password validation functions from the main utils module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from utils import validate_password_strength, calculate_password_strength
    __all__ = ['validate_password_strength', 'calculate_password_strength']
except ImportError:
    # Fallback if utils.py is not available
    def validate_password_strength(password):
        return True, []

    def calculate_password_strength(password):
        return {'score': 50, 'strength': 'medium', 'feedback': []}

    __all__ = ['validate_password_strength', 'calculate_password_strength']
