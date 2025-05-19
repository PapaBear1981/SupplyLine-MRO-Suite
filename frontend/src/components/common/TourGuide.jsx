import { useState, useEffect } from 'react';
import { Button, Modal } from 'react-bootstrap';
import './Help.css';

/**
 * A simple tour guide component that displays a series of steps to guide users through a feature.
 * 
 * @param {Object} props - Component props
 * @param {Array} props.steps - An array of steps for the tour
 * @param {boolean} props.show - Whether to show the tour
 * @param {Function} props.onClose - Function to call when the tour is closed
 * @param {string} props.title - The title of the tour
 * @returns {React.ReactElement} - The tour guide component
 */
const TourGuide = ({
  steps = [],
  show = false,
  onClose,
  title = 'Feature Tour'
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [showTour, setShowTour] = useState(show);

  useEffect(() => {
    setShowTour(show);
    if (show) {
      setCurrentStep(0);
    }
  }, [show]);

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleClose();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleClose = () => {
    setShowTour(false);
    if (onClose) {
      onClose();
    }
  };

  if (!steps.length) return null;

  return (
    <Modal
      show={showTour}
      onHide={handleClose}
      centered
      backdrop="static"
      keyboard={false}
      size="lg"
    >
      <Modal.Header closeButton>
        <Modal.Title>{title}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <div className="d-flex align-items-center mb-3">
          <span className="badge bg-primary me-2">Step {currentStep + 1} of {steps.length}</span>
          <h5 className="mb-0">{steps[currentStep]?.title}</h5>
        </div>
        <div className="mb-4">
          {steps[currentStep]?.content}
        </div>
        {steps[currentStep]?.image && (
          <div className="text-center mb-3">
            <img 
              src={steps[currentStep].image} 
              alt={`Step ${currentStep + 1}`} 
              className="img-fluid border rounded" 
              style={{ maxHeight: '300px' }}
            />
          </div>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Skip Tour
        </Button>
        <div className="ms-auto">
          <Button 
            variant="outline-primary" 
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className="me-2"
          >
            Previous
          </Button>
          <Button variant="primary" onClick={handleNext}>
            {currentStep < steps.length - 1 ? 'Next' : 'Finish'}
          </Button>
        </div>
      </Modal.Footer>
    </Modal>
  );
};

export default TourGuide;
