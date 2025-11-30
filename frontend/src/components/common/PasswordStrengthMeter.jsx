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
    isValid: false,
    requirements: []
  });

  // Calculate password strength
  useEffect(() => {
    const safePassword = password || '';

    // Check minimum length
    const lengthValid = safePassword.length >= 8;

    // Check for uppercase letters
    const uppercaseValid = /[A-Z]/.test(safePassword);

    // Check for lowercase letters
    const lowercaseValid = /[a-z]/.test(safePassword);

    // Check for digits
    const digitsValid = /\d/.test(safePassword);

    // Check for special characters
    const specialCharsValid = /[!@#$%^&*(),.?":{}|<>]/.test(safePassword);
    
    // Calculate score (0-100)
    let score = 0;

    // Length contribution (up to 25 points)
    const lengthScore = Math.min(25, safePassword.length * 2);
    score += lengthScore;

    // Character variety contribution (up to 50 points)
    if (uppercaseValid) score += 10;
    if (lowercaseValid) score += 10;
    if (digitsValid) score += 10;
    if (specialCharsValid) score += 20;

    // Complexity contribution (up to 25 points)
    if (new Set(safePassword).size > 6) score += 15; // Unique characters
    if (safePassword.length > 12) score += 10;
    
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
    if (!safePassword) feedback.push('Enter a password');
    if (!lengthValid) feedback.push('Add more characters (minimum 8)');
    if (!uppercaseValid) feedback.push('Add uppercase letters');
    if (!lowercaseValid) feedback.push('Add lowercase letters');
    if (!digitsValid) feedback.push('Add numbers');
    if (!specialCharsValid) feedback.push('Add special characters (!@#$%^&*(),.?":{}|<>)');

    const requirements = [
      { label: 'At least 8 characters', met: lengthValid },
      { label: 'Contains uppercase letters', met: uppercaseValid },
      { label: 'Contains lowercase letters', met: lowercaseValid },
      { label: 'Contains at least one number', met: digitsValid },
      { label: 'Contains at least one special character', met: specialCharsValid }
    ];
    
    // Check if password is valid (meets all requirements)
    const isValid = lengthValid && uppercaseValid && lowercaseValid && digitsValid && specialCharsValid;
    
    setStrength({
      score,
      strength: strengthCategory,
      feedback,
      isValid,
      requirements
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
      <div className="small mb-2">
        {strength.requirements?.map((requirement, index) => (
          <div
            key={index}
            className={`d-flex align-items-center ${requirement.met ? 'text-success' : 'text-muted'}`}
          >
            <i className={`bi ${requirement.met ? 'bi-check-circle-fill' : 'bi-circle'} me-2`}></i>
            <span>{requirement.label}</span>
          </div>
        ))}
      </div>
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
