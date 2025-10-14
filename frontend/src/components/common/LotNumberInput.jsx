import React, { useState } from 'react';
import { Form, Button, InputGroup, Spinner } from 'react-bootstrap';
import { FaSync, FaCheck } from 'react-icons/fa';
import api from '../../services/api';
import './LotNumberInput.css';

/**
 * LotNumberInput - Form input component for lot number entry with auto-generation
 * 
 * Features:
 * - Manual lot number entry
 * - Auto-generate button that calls API to generate unique lot number
 * - Visual feedback for generated vs manual entry
 * - Validation support
 * 
 * Props:
 * - value: string - current lot number value
 * - onChange: function - callback when value changes (receives new value)
 * - disabled: boolean - whether input is disabled
 * - required: boolean - whether field is required
 * - label: string - label text (default: "Lot Number")
 * - placeholder: string - placeholder text
 * - helpText: string - help text to display below input
 * - showAutoGenerate: boolean - whether to show auto-generate button (default: true)
 */
const LotNumberInput = ({
  value,
  onChange,
  disabled = false,
  required = false,
  label = 'Lot Number',
  placeholder = 'Enter lot number or click Auto-Generate',
  helpText = '',
  showAutoGenerate = true
}) => {
  const [generating, setGenerating] = useState(false);
  const [isGenerated, setIsGenerated] = useState(false);
  const [error, setError] = useState(null);

  // Handle auto-generate button click
  const handleAutoGenerate = async () => {
    setGenerating(true);
    setError(null);

    try {
      const response = await api.post('/lot-numbers/generate');
      const generatedLotNumber = response.data.lot_number;
      
      // Update parent component
      onChange(generatedLotNumber);
      setIsGenerated(true);
      
      // Show success feedback briefly
      setTimeout(() => {
        setIsGenerated(false);
      }, 3000);
    } catch (err) {
      console.error('Error generating lot number:', err);
      setError(err.response?.data?.error || 'Failed to generate lot number');
    } finally {
      setGenerating(false);
    }
  };

  // Handle manual input change
  const handleInputChange = (e) => {
    onChange(e.target.value);
    setIsGenerated(false);
    setError(null);
  };

  return (
    <Form.Group className="lot-number-input-group">
      <Form.Label>
        {label}
        {required && <span className="text-danger ms-1">*</span>}
      </Form.Label>
      
      <InputGroup>
        <Form.Control
          type="text"
          value={value || ''}
          onChange={handleInputChange}
          disabled={disabled || generating}
          required={required}
          placeholder={placeholder}
          className={isGenerated ? 'generated-value' : ''}
          isInvalid={!!error}
        />
        
        {showAutoGenerate && (
          <Button
            variant={isGenerated ? 'success' : 'outline-primary'}
            onClick={handleAutoGenerate}
            disabled={disabled || generating}
            className="auto-generate-btn"
          >
            {generating ? (
              <>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                  className="me-1"
                />
                Generating...
              </>
            ) : isGenerated ? (
              <>
                <FaCheck className="me-1" />
                Generated
              </>
            ) : (
              <>
                <FaSync className="me-1" />
                Auto-Generate
              </>
            )}
          </Button>
        )}
      </InputGroup>
      
      {error && (
        <Form.Control.Feedback type="invalid" className="d-block">
          {error}
        </Form.Control.Feedback>
      )}
      
      {helpText && !error && (
        <Form.Text className="text-muted">
          {helpText}
        </Form.Text>
      )}
      
      {isGenerated && !error && (
        <Form.Text className="text-success d-block mt-1">
          <FaCheck className="me-1" />
          Lot number generated successfully
        </Form.Text>
      )}
    </Form.Group>
  );
};

export default LotNumberInput;

