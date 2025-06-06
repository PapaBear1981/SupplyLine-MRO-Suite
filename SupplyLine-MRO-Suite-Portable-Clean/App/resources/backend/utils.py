import re

def validate_password_strength(password):
    """
    Validates password strength based on the following criteria:
    - Minimum length of 8 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    
    Returns:
        tuple: (is_valid, error_message)
    """
    errors = []
    
    # Check minimum length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    # Check for uppercase letters
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    # Check for lowercase letters
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    # Check for digits
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    # Check for special characters
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    # Check for common passwords (simplified version)
    common_passwords = [
        "password", "123456", "qwerty", "admin", "welcome", 
        "password123", "admin123", "letmein", "welcome1"
    ]
    
    if password.lower() in common_passwords:
        errors.append("Password is too common and easily guessable")
    
    if errors:
        return False, errors
    
    return True, []

def calculate_password_strength(password):
    """
    Calculates password strength on a scale of 0-100
    
    Returns:
        dict: {
            'score': int (0-100),
            'strength': str ('weak', 'medium', 'strong', 'very-strong'),
            'feedback': list of str (improvement suggestions)
        }
    """
    score = 0
    feedback = []
    
    # Length contribution (up to 25 points)
    length_score = min(25, len(password) * 2)
    score += length_score
    
    if len(password) < 8:
        feedback.append("Add more characters")
    
    # Character variety contribution (up to 50 points)
    if re.search(r'[A-Z]', password):
        score += 10
    else:
        feedback.append("Add uppercase letters")
        
    if re.search(r'[a-z]', password):
        score += 10
    else:
        feedback.append("Add lowercase letters")
        
    if re.search(r'\d', password):
        score += 10
    else:
        feedback.append("Add numbers")
        
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 20
    else:
        feedback.append("Add special characters")
    
    # Complexity contribution (up to 25 points)
    if len(set(password)) > 6:  # Unique characters
        score += 15
    
    if len(password) > 12:
        score += 10
    
    # Determine strength category
    strength = 'weak'
    if score >= 80:
        strength = 'very-strong'
    elif score >= 60:
        strength = 'strong'
    elif score >= 40:
        strength = 'medium'
    
    return {
        'score': score,
        'strength': strength,
        'feedback': feedback
    }
