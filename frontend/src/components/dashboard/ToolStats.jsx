import { Card, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const ToolStats = ({ tools }) => {
  // Log tool statuses for debugging
  console.log('Tool statuses:', tools.map(tool => tool.status));

  // Count tools by status
  const availableTools = tools.filter(tool => tool.status === 'available').length;
  const checkedOutTools = tools.filter(tool => tool.status === 'checked_out').length;
  const maintenanceTools = tools.filter(tool => tool.status === 'maintenance').length;
  const totalTools = tools.length;

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header className="bg-light">
        <h4 className="mb-0">Tool Inventory Overview</h4>
      </Card.Header>
      <Card.Body>
        <Row>
          <Col md={3} sm={6} className="mb-3 mb-md-0">
            <div className="text-center">
              <h2 className="text-primary display-4">{totalTools}</h2>
              <h5>Total Tools</h5>
            </div>
          </Col>
          <Col md={3} sm={6} className="mb-3 mb-md-0">
            <div className="text-center">
              <h2 className="text-success display-4">{availableTools}</h2>
              <h5>Available</h5>
            </div>
          </Col>
          <Col md={3} sm={6} className="mb-3 mb-md-0">
            <div className="text-center">
              <h2 className="text-warning display-4">{checkedOutTools}</h2>
              <h5>Checked Out</h5>
            </div>
          </Col>
          <Col md={3} sm={6}>
            <div className="text-center">
              <h2 className="text-danger display-4">{maintenanceTools}</h2>
              <h5>In Maintenance</h5>
            </div>
          </Col>
        </Row>
        <div className="text-center mt-3">
          <Link to="/tools" className="btn btn-outline-primary">View All Tools</Link>
        </div>
      </Card.Body>
    </Card>
  );
};

export default ToolStats;
