import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Container, Card, Form, Button, Row, Col, ProgressBar, Alert, ListGroup, Badge } from 'react-bootstrap';
import { FaPlane, FaBox, FaCheck, FaArrowLeft, FaArrowRight } from 'react-icons/fa';
import { fetchAircraftTypes, kitWizardStep, createKit, setWizardData, clearWizardData } from '../../store/kitsSlice';

const KitWizard = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { aircraftTypes, wizardData, loading, error } = useSelector((state) => state.kits);
  
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    aircraft_type_id: '',
    name: '',
    description: '',
    boxes: []
  });
  const [validationErrors, setValidationErrors] = useState({});

  useEffect(() => {
    dispatch(fetchAircraftTypes());
    return () => {
      dispatch(clearWizardData());
    };
  }, [dispatch]);

  const totalSteps = 4;
  const progress = (currentStep / totalSteps) * 100;

  const validateStep = (step) => {
    const errors = {};
    
    if (step === 1) {
      if (!formData.aircraft_type_id) {
        errors.aircraft_type_id = 'Please select an aircraft type';
      }
    } else if (step === 2) {
      if (!formData.name || formData.name.trim() === '') {
        errors.name = 'Kit name is required';
      }
    } else if (step === 3) {
      if (formData.boxes.length === 0) {
        errors.boxes = 'At least one box is required';
      }
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleNext = async () => {
    if (!validateStep(currentStep)) {
      return;
    }
    
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
      
      // Load suggested boxes for step 3
      if (currentStep === 2) {
        const result = await dispatch(kitWizardStep({ step: 3 }));
        if (result.payload?.suggested_boxes) {
          setFormData(prev => ({
            ...prev,
            boxes: result.payload.suggested_boxes
          }));
        }
      }
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) {
      return;
    }
    
    try {
      const result = await dispatch(createKit(formData));
      if (result.payload) {
        navigate(`/kits/${result.payload.id}`);
      }
    } catch (err) {
      console.error('Failed to create kit:', err);
    }
  };

  const handleBoxChange = (index, field, value) => {
    const newBoxes = [...formData.boxes];
    newBoxes[index] = { ...newBoxes[index], [field]: value };
    setFormData({ ...formData, boxes: newBoxes });
  };

  const addBox = () => {
    setFormData({
      ...formData,
      boxes: [...formData.boxes, { box_number: `Box${formData.boxes.length + 1}`, box_type: 'expendable', description: '' }]
    });
  };

  const removeBox = (index) => {
    const newBoxes = formData.boxes.filter((_, i) => i !== index);
    setFormData({ ...formData, boxes: newBoxes });
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div>
            <h4 className="mb-4">
              <FaPlane className="me-2" />
              Select Aircraft Type
            </h4>
            <p className="text-muted mb-4">
              Choose the aircraft type this kit will be associated with
            </p>
            
            <Row>
              {aircraftTypes.map(type => (
                <Col key={type.id} md={4} className="mb-3">
                  <Card 
                    className={`h-100 cursor-pointer ${formData.aircraft_type_id === type.id ? 'border-primary' : ''}`}
                    onClick={() => setFormData({ ...formData, aircraft_type_id: type.id })}
                    style={{ cursor: 'pointer' }}
                  >
                    <Card.Body className="text-center">
                      <FaPlane size={48} className={formData.aircraft_type_id === type.id ? 'text-primary' : 'text-muted'} />
                      <h5 className="mt-3">{type.name}</h5>
                      {type.description && (
                        <p className="text-muted small">{type.description}</p>
                      )}
                      {formData.aircraft_type_id === type.id && (
                        <Badge bg="primary" className="mt-2">
                          <FaCheck className="me-1" />
                          Selected
                        </Badge>
                      )}
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
            
            {validationErrors.aircraft_type_id && (
              <Alert variant="danger" className="mt-3">{validationErrors.aircraft_type_id}</Alert>
            )}
          </div>
        );
      
      case 2:
        return (
          <div>
            <h4 className="mb-4">Kit Details</h4>
            <p className="text-muted mb-4">
              Provide basic information about the kit
            </p>
            
            <Form>
              <Form.Group className="mb-3">
                <Form.Label>Kit Name *</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="e.g., Q400 Kit #1"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  isInvalid={!!validationErrors.name}
                />
                <Form.Control.Feedback type="invalid">
                  {validationErrors.name}
                </Form.Control.Feedback>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Description (Optional)</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  placeholder="Add any additional details about this kit..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </Form.Group>
            </Form>
          </div>
        );
      
      case 3:
        return (
          <div>
            <h4 className="mb-4">
              <FaBox className="me-2" />
              Configure Boxes
            </h4>
            <p className="text-muted mb-4">
              Set up the boxes that will be in this kit
            </p>
            
            <ListGroup className="mb-3">
              {formData.boxes.map((box, index) => (
                <ListGroup.Item key={index}>
                  <Row className="align-items-center">
                    <Col md={3}>
                      <Form.Control
                        size="sm"
                        type="text"
                        placeholder="Box number"
                        value={box.box_number}
                        onChange={(e) => handleBoxChange(index, 'box_number', e.target.value)}
                      />
                    </Col>
                    <Col md={3}>
                      <Form.Select
                        size="sm"
                        value={box.box_type}
                        onChange={(e) => handleBoxChange(index, 'box_type', e.target.value)}
                      >
                        <option value="expendable">Expendable</option>
                        <option value="tooling">Tooling</option>
                        <option value="consumable">Consumable</option>
                        <option value="loose">Loose</option>
                        <option value="floor">Floor</option>
                      </Form.Select>
                    </Col>
                    <Col md={5}>
                      <Form.Control
                        size="sm"
                        type="text"
                        placeholder="Description"
                        value={box.description}
                        onChange={(e) => handleBoxChange(index, 'description', e.target.value)}
                      />
                    </Col>
                    <Col md={1}>
                      <Button
                        size="sm"
                        variant="outline-danger"
                        onClick={() => removeBox(index)}
                      >
                        ×
                      </Button>
                    </Col>
                  </Row>
                </ListGroup.Item>
              ))}
            </ListGroup>
            
            <Button variant="outline-primary" size="sm" onClick={addBox}>
              + Add Box
            </Button>
            
            {validationErrors.boxes && (
              <Alert variant="danger" className="mt-3">{validationErrors.boxes}</Alert>
            )}
          </div>
        );
      
      case 4:
        const selectedAircraftType = aircraftTypes.find(at => at.id === formData.aircraft_type_id);
        return (
          <div>
            <h4 className="mb-4">Review & Create</h4>
            <p className="text-muted mb-4">
              Review your kit configuration before creating
            </p>
            
            <Card className="mb-3">
              <Card.Body>
                <h6>Aircraft Type</h6>
                <p className="mb-0">{selectedAircraftType?.name}</p>
              </Card.Body>
            </Card>
            
            <Card className="mb-3">
              <Card.Body>
                <h6>Kit Name</h6>
                <p className="mb-2">{formData.name}</p>
                {formData.description && (
                  <>
                    <h6 className="mt-3">Description</h6>
                    <p className="mb-0">{formData.description}</p>
                  </>
                )}
              </Card.Body>
            </Card>
            
            <Card>
              <Card.Body>
                <h6>Boxes ({formData.boxes.length})</h6>
                <ListGroup variant="flush">
                  {formData.boxes.map((box, index) => (
                    <ListGroup.Item key={index}>
                      <strong>{box.box_number}</strong> - {box.box_type}
                      {box.description && ` - ${box.description}`}
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              </Card.Body>
            </Card>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <Container className="py-4">
      <Card>
        <Card.Header>
          <h3 className="mb-0">Create New Kit</h3>
        </Card.Header>
        <Card.Body>
          <ProgressBar now={progress} className="mb-4" />
          
          {error && (
            <Alert variant="danger" dismissible>
              {error.message || 'An error occurred'}
            </Alert>
          )}
          
          {renderStep()}
          
          <div className="d-flex justify-content-between mt-4">
            <Button
              variant="outline-secondary"
              onClick={currentStep === 1 ? () => navigate('/kits') : handleBack}
            >
              <FaArrowLeft className="me-2" />
              {currentStep === 1 ? 'Cancel' : 'Back'}
            </Button>
            
            {currentStep < totalSteps ? (
              <Button variant="primary" onClick={handleNext} disabled={loading}>
                Next
                <FaArrowRight className="ms-2" />
              </Button>
            ) : (
              <Button variant="success" onClick={handleSubmit} disabled={loading}>
                <FaCheck className="me-2" />
                Create Kit
              </Button>
            )}
          </div>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default KitWizard;

