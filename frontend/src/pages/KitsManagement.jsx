import React, { useEffect, useState, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Container, Row, Col, Card, Button, Tabs, Tab, Badge, Form, InputGroup } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { FaPlus, FaSearch, FaExclamationTriangle, FaBox, FaPlane } from 'react-icons/fa';
import { AppstoreOutlined, PlusCircleOutlined } from '@ant-design/icons';
import { fetchKits, fetchAircraftTypes } from '../store/kitsSlice';
import { fetchUnreadCount } from '../store/kitMessagesSlice';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EnterprisePageHeader from '../components/common/EnterprisePageHeader';
import useHotkeys from '../hooks/useHotkeys';

const KitsManagement = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { kits, aircraftTypes, loading } = useSelector((state) => state.kits);
  const { unreadCount } = useSelector((state) => state.kitMessages);

  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAircraftType, setSelectedAircraftType] = useState('');
  const searchInputRef = useRef(null);

  // Page-specific hotkeys
  useHotkeys({
    'n': () => navigate('/kits/new'),
    '/': () => searchInputRef.current?.focus()
  }, {
    deps: [navigate]
  });

  useEffect(() => {
    dispatch(fetchKits());
    dispatch(fetchAircraftTypes());
    dispatch(fetchUnreadCount());
  }, [dispatch]);

  const filteredKits = kits.filter(kit => {
    // Filter by tab
    if (activeTab === 'active' && kit.status !== 'active') return false;
    if (activeTab === 'inactive' && kit.status !== 'inactive') return false;
    
    // Filter by search term
    if (searchTerm && !kit.name.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    
    // Filter by aircraft type
    if (selectedAircraftType && kit.aircraft_type_id !== parseInt(selectedAircraftType)) {
      return false;
    }
    
    return true;
  });

  const getStatusBadge = (status) => {
    const variants = {
      active: 'success',
      inactive: 'secondary',
      maintenance: 'warning'
    };
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>;
  };

  const KitCard = ({ kit }) => {
    const aircraftType = aircraftTypes.find(at => at.id === kit.aircraft_type_id);

    return (
      <Card className="mb-3 shadow-sm hover-shadow" style={{ cursor: 'pointer' }} data-testid="kit-card">
        <Card.Body onClick={() => navigate(`/kits/${kit.id}`)}>
          <div className="d-flex justify-content-between align-items-start mb-2">
            <div>
              <h5 className="mb-1">{kit.name}</h5>
              <div className="text-muted small">
                <FaPlane className="me-1" />
                {aircraftType?.name || 'Unknown'}
              </div>
            </div>
            <div className="text-end">
              {getStatusBadge(kit.status)}
            </div>
          </div>

          {kit.description && (
            <p className="text-muted small mb-2">{kit.description}</p>
          )}

          <Row className="mt-3">
            <Col xs={4} className="text-center">
              <div className="text-muted small">Boxes</div>
              <div className="fw-bold">{kit.box_count || 0}</div>
            </Col>
            <Col xs={4} className="text-center">
              <div className="text-muted small">Items</div>
              <div className="fw-bold">{kit.item_count || 0}</div>
            </Col>
            <Col xs={4} className="text-center">
              <div className="text-muted small">Alerts</div>
              <div className="fw-bold text-danger">
                {kit.alert_count || 0}
                {kit.alert_count > 0 && <FaExclamationTriangle className="ms-1" />}
              </div>
            </Col>
          </Row>
        </Card.Body>
      </Card>
    );
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="enterprise-kits-management">
      <EnterprisePageHeader
        title="Mobile Warehouses (Kits)"
        subtitle="Manage mobile warehouses that follow aircraft to operating bases"
        icon={<AppstoreOutlined />}
        breadcrumbs={[{ title: 'Kits' }]}
        actions={[
          {
            label: 'Create Kit',
            icon: <PlusCircleOutlined />,
            type: 'primary',
            onClick: () => navigate('/kits/new'),
          },
        ]}
        meta={
          unreadCount > 0
            ? [
                {
                  label: 'Unread Messages',
                  value: <Badge bg="danger">{unreadCount}</Badge>,
                },
              ]
            : []
        }
      />

      <Row className="mb-3">
        <Col md={6}>
          <InputGroup>
            <InputGroup.Text>
              <FaSearch />
            </InputGroup.Text>
            <Form.Control
              ref={searchInputRef}
              type="text"
              placeholder="Search kits..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              data-testid="search-kits-input"
            />
          </InputGroup>
        </Col>
        <Col md={6}>
          <Form.Select
            value={selectedAircraftType}
            onChange={(e) => setSelectedAircraftType(e.target.value)}
            data-testid="aircraft-type-filter"
          >
            <option value="">All Aircraft Types</option>
            {aircraftTypes.map(at => (
              <option key={at.id} value={at.id}>{at.name}</option>
            ))}
          </Form.Select>
        </Col>
      </Row>

      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k)}
        className="mb-3"
      >
        <Tab eventKey="all" title={`All Kits (${kits.length})`}>
          <Row>
            {filteredKits.length === 0 ? (
              <Col>
                <Card className="text-center py-5">
                  <Card.Body>
                    <FaBox size={48} className="text-muted mb-3" />
                    <h5>No kits found</h5>
                    <p className="text-muted">
                      {searchTerm || selectedAircraftType 
                        ? 'Try adjusting your filters' 
                        : 'Create your first kit to get started'}
                    </p>
                    {!searchTerm && !selectedAircraftType && (
                      <Button variant="primary" onClick={() => navigate('/kits/new')}>
                        <FaPlus className="me-2" />
                        Create Kit
                      </Button>
                    )}
                  </Card.Body>
                </Card>
              </Col>
            ) : (
              filteredKits.map(kit => (
                <Col key={kit.id} md={6} lg={4}>
                  <KitCard kit={kit} />
                </Col>
              ))
            )}
          </Row>
        </Tab>
        
        <Tab eventKey="active" title={`Active (${kits.filter(k => k.status === 'active').length})`}>
          <Row>
            {filteredKits.map(kit => (
              <Col key={kit.id} md={6} lg={4}>
                <KitCard kit={kit} />
              </Col>
            ))}
          </Row>
        </Tab>
        
        <Tab eventKey="inactive" title={`Inactive (${kits.filter(k => k.status === 'inactive').length})`}>
          <Row>
            {filteredKits.map(kit => (
              <Col key={kit.id} md={6} lg={4}>
                <KitCard kit={kit} />
              </Col>
            ))}
          </Row>
        </Tab>
        
        <Tab 
          eventKey="alerts" 
          title={
            <span>
              Alerts
              {kits.filter(k => k.alert_count > 0).length > 0 && (
                <Badge bg="danger" className="ms-2">
                  {kits.filter(k => k.alert_count > 0).length}
                </Badge>
              )}
            </span>
          }
        >
          <Row>
            {kits.filter(k => k.alert_count > 0).map(kit => (
              <Col key={kit.id} md={6} lg={4}>
                <KitCard kit={kit} />
              </Col>
            ))}
          </Row>
        </Tab>
      </Tabs>

      <style jsx>{`
        .hover-shadow {
          transition: box-shadow 0.3s ease-in-out;
        }
        .hover-shadow:hover {
          box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
        }
      `}</style>
    </div>
  );
};

export default KitsManagement;

