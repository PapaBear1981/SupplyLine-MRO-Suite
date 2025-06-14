import { Container, Row, Col, Card, Button, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { ExclamationTriangleFill, HouseFill, PersonFill } from 'react-bootstrap-icons';

/**
 * Component to display when user is not authorized to access a resource
 * @param {Object} props
 * @param {string} props.title - Title of the error (default: "Access Denied")
 * @param {string} props.message - Error message to display
 * @param {string} props.redirectPath - Path to redirect to (default: "/dashboard")
 * @param {string} props.redirectText - Text for redirect button (default: "Go to Dashboard")
 */
const UnauthorizedAccess = ({ 
  title = "Access Denied", 
  message = "You do not have permission to access this resource.",
  redirectPath = "/dashboard",
  redirectText = "Go to Dashboard"
}) => {
  return (
    <Container className="mt-5">
      <Row className="justify-content-center">
        <Col md={8} lg={6}>
          <Card className="text-center shadow">
            <Card.Body className="p-5">
              <div className="mb-4">
                <ExclamationTriangleFill 
                  size={64} 
                  className="text-warning mb-3" 
                />
              </div>
              
              <Card.Title as="h2" className="mb-3">
                {title}
              </Card.Title>
              
              <Alert variant="warning" className="mb-4">
                <PersonFill className="me-2" />
                {message}
              </Alert>
              
              <div className="d-flex flex-column flex-sm-row gap-3 justify-content-center">
                <Button 
                  as={Link} 
                  to={redirectPath}
                  variant="primary"
                  size="lg"
                  className="d-flex align-items-center justify-content-center"
                >
                  <HouseFill className="me-2" />
                  {redirectText}
                </Button>
                
                <Button 
                  as={Link} 
                  to="/login"
                  variant="outline-secondary"
                  size="lg"
                  className="d-flex align-items-center justify-content-center"
                >
                  <PersonFill className="me-2" />
                  Login as Different User
                </Button>
              </div>
              
              <div className="mt-4 text-muted">
                <small>
                  If you believe this is an error, please contact your system administrator.
                </small>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default UnauthorizedAccess;
