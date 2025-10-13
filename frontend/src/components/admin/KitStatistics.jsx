import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Row, Col, Badge, Alert } from 'react-bootstrap';
import { FaBox, FaPlane, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';
import { fetchKits, fetchAircraftTypes } from '../../store/kitsSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const KitStatistics = () => {
  const dispatch = useDispatch();
  const { kits, aircraftTypes, loading, error } = useSelector((state) => state.kits);

  useEffect(() => {
    dispatch(fetchKits());
    dispatch(fetchAircraftTypes());
  }, [dispatch]);

  // Calculate statistics
  const totalKits = kits.length;
  const activeKits = kits.filter(kit => kit.status === 'active').length;
  const inactiveKits = kits.filter(kit => kit.status === 'inactive').length;
  const maintenanceKits = kits.filter(kit => kit.status === 'maintenance').length;
  const kitsWithAlerts = kits.filter(kit => kit.alert_count > 0).length;
  const totalAlerts = kits.reduce((sum, kit) => sum + (kit.alert_count || 0), 0);

  // Group kits by aircraft type
  const kitsByAircraftType = aircraftTypes.map(type => ({
    name: type.name,
    count: kits.filter(kit => kit.aircraft_type_id === type.id).length,
    active: kits.filter(kit => kit.aircraft_type_id === type.id && kit.status === 'active').length
  }));

  if (loading && kits.length === 0) {
    return (
      <Card className="mb-4">
        <Card.Header as="h5">
          <FaBox className="me-2" />
          Kit Statistics
        </Card.Header>
        <Card.Body>
          <LoadingSpinner />
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="mb-4">
        <Card.Header as="h5">
          <FaBox className="me-2" />
          Kit Statistics
        </Card.Header>
        <Card.Body>
          <Alert variant="danger">
            Failed to load kit statistics: {error.message || 'Unknown error'}
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="mb-4">
      <Card.Header as="h5">
        <FaBox className="me-2" />
        Kit Statistics
      </Card.Header>
      <Card.Body>
        {/* Overall Statistics */}
        <Row className="mb-4">
          <Col md={3} sm={6} className="mb-3">
            <div className="stat-card text-center p-3 border rounded">
              <h3 className="mb-1">{totalKits}</h3>
              <p className="text-muted mb-2">Total Kits</p>
              <Badge bg="primary">All Kits</Badge>
            </div>
          </Col>
          <Col md={3} sm={6} className="mb-3">
            <div className="stat-card text-center p-3 border rounded">
              <h3 className="mb-1 text-success">{activeKits}</h3>
              <p className="text-muted mb-2">Active Kits</p>
              <Badge bg="success">
                <FaCheckCircle className="me-1" />
                Operational
              </Badge>
            </div>
          </Col>
          <Col md={3} sm={6} className="mb-3">
            <div className="stat-card text-center p-3 border rounded">
              <h3 className="mb-1 text-warning">{kitsWithAlerts}</h3>
              <p className="text-muted mb-2">Kits with Alerts</p>
              <Badge bg="warning">
                <FaExclamationTriangle className="me-1" />
                {totalAlerts} Total Alerts
              </Badge>
            </div>
          </Col>
          <Col md={3} sm={6} className="mb-3">
            <div className="stat-card text-center p-3 border rounded">
              <h3 className="mb-1 text-secondary">{inactiveKits}</h3>
              <p className="text-muted mb-2">Inactive Kits</p>
              <Badge bg="secondary">Not in Use</Badge>
            </div>
          </Col>
        </Row>

        {/* Kits by Aircraft Type */}
        <h6 className="mb-3">
          <FaPlane className="me-2" />
          Kits by Aircraft Type
        </h6>
        <Row>
          {kitsByAircraftType.length === 0 ? (
            <Col>
              <Alert variant="info">No aircraft types configured</Alert>
            </Col>
          ) : (
            kitsByAircraftType.map((type, index) => (
              <Col md={4} sm={6} key={index} className="mb-3">
                <div className="p-3 border rounded">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <h5 className="mb-1">{type.name}</h5>
                      <p className="text-muted mb-0 small">
                        {type.count} {type.count === 1 ? 'kit' : 'kits'}
                      </p>
                    </div>
                    <div className="text-end">
                      <Badge bg="success" className="mb-1">
                        {type.active} Active
                      </Badge>
                      <div className="text-muted small">
                        {type.count - type.active} Inactive
                      </div>
                    </div>
                  </div>
                </div>
              </Col>
            ))
          )}
        </Row>

        {/* Additional Stats */}
        {maintenanceKits > 0 && (
          <Row className="mt-3">
            <Col>
              <Alert variant="warning" className="mb-0">
                <FaExclamationTriangle className="me-2" />
                <strong>{maintenanceKits}</strong> {maintenanceKits === 1 ? 'kit is' : 'kits are'} currently under maintenance
              </Alert>
            </Col>
          </Row>
        )}
      </Card.Body>
    </Card>
  );
};

export default KitStatistics;

