import React, { useState, useEffect } from 'react';
import { ProgressBar, Form } from 'react-bootstrap';

/**
 * Password strength meter component
 * @param {Object} props
 * @param {string} props.password - The password to evaluate
 * @param {function} props.onValidationChange - Callback when validation status changes
 */
const PasswordStrengthMeter = ({ password, onValidationChange }) => {
  const [strength, setStrength] = useState({
    score: 0,
    strength: 'weak',
    feedback: [],
    isValid: false
  });

  // Calculate password strength
  useEffect(() => {
    if (!password) {
      setStrength({
        score: 0,
        strength: 'weak',
        feedback: ['Enter a password'],
        isValid: false
      });
      if (onValidationChange) onValidationChange(false);
      return;
    }

    // Check minimum length
    const lengthValid = password.length >= 8;
    
    // Check for uppercase letters
    const uppercaseValid = /[A-Z]/.test(password);
    
    // Check for lowercase letters
    const lowercaseValid = /[a-z]/.test(password);
    
    // Check for digits
    const digitsValid = /\d/.test(password);
    
    // Check for special characters
    const specialCharsValid = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    
    // Calculate score (0-100)
    let score = 0;
    
    // Length contribution (up to 25 points)
    const lengthScore = Math.min(25, password.length * 2);
    score += lengthScore;
    
    // Character variety contribution (up to 50 points)
    if (uppercaseValid) score += 10;
    if (lowercaseValid) score += 10;
    if (digitsValid) score += 10;
    if (specialCharsValid) score += 20;
    
    // Complexity contribution (up to 25 points)
    if (new Set(password).size > 6) score += 15; // Unique characters
    if (password.length > 12) score += 10;
    
    // Determine strength category
    let strengthCategory = 'weak';
    if (score >= 80) {
      strengthCategory = 'very-strong';
    } else if (score >= 60) {
      strengthCategory = 'strong';
    } else if (score >= 40) {
      strengthCategory = 'medium';
    }
    
    // Generate feedback
    const feedback = [];
    if (!lengthValid) feedback.push('Add more characters (minimum 8)');
    if (!uppercaseValid) feedback.push('Add uppercase letters');
    if (!lowercaseValid) feedback.push('Add lowercase letters');
    if (!digitsValid) feedback.push('Add numbers');
    if (!specialCharsValid) feedback.push('Add special characters (!@#$%^&*(),.?":{}|<>)');
    
    // Check if password is valid (meets all requirements)
    const isValid = lengthValid && uppercaseValid && lowercaseValid && digitsValid && specialCharsValid;
    
    setStrength({
      score,
      strength: strengthCategory,
      feedback,
      isValid
    });
    
    if (onValidationChange) onValidationChange(isValid);
  }, [password, onValidationChange]);

  // Get progress bar variant based on strength
  const getVariant = () => {
    switch (strength.strength) {
      case 'very-strong':
        return 'success';
      case 'strong':
        return 'info';
      case 'medium':
        return 'warning';
      default:
        return 'danger';
    }
  };

  // Get label text based on strength
  const getLabel = () => {
    switch (strength.strength) {
      case 'very-strong':
        return 'Very Strong';
      case 'strong':
        return 'Strong';
      case 'medium':
        return 'Medium';
      default:
        return 'Weak';
    }
  };

  return (
    <div className="password-strength-meter mb-3">
      <div className="d-flex justify-content-between align-items-center mb-1">
        <small>Password Strength:</small>
        <small className={`text-${getVariant()}`}>{getLabel()}</small>
      </div>
      <ProgressBar 
        now={strength.score} 
        variant={getVariant()} 
        className="mb-2" 
        style={{ height: '8px' }}
      />
      {strength.feedback.length > 0 && (
        <Form.Text className="text-muted">
          <ul className="ps-3 mb-0 mt-1">
            {strength.feedback.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </Form.Text>
      )}
    </div>
  );
};

export default PasswordStrengthMeter;
