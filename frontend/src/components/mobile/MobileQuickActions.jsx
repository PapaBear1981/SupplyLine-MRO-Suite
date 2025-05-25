import { Button, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';

const MobileQuickActions = () => {
  const { user } = useSelector((state) => state.auth);

  const quickActions = [
    {
      icon: 'upc-scan',
      label: 'Scan',
      path: '/scanner',
      variant: 'primary',
      available: true
    },
    {
      icon: 'search',
      label: 'Find Tool',
      path: '/tools',
      variant: 'outline-primary',
      available: true
    },
    {
      icon: 'clipboard-check',
      label: 'Checkout',
      path: '/checkouts',
      variant: 'outline-success',
      available: true
    },
    {
      icon: 'arrow-return-left',
      label: 'Return',
      path: '/checkouts',
      variant: 'outline-warning',
      available: true
    }
  ];

  // Add admin/materials specific actions
  if (user && (user.is_admin || user.department === 'Materials')) {
    quickActions.push(
      {
        icon: 'plus-circle',
        label: 'Add Tool',
        path: '/tools/new',
        variant: 'outline-info',
        available: true
      },
      {
        icon: 'flask',
        label: 'Chemicals',
        path: '/chemicals',
        variant: 'outline-secondary',
        available: true
      }
    );
  }

  return (
    <div className="mobile-quick-actions mb-4">
      <h6 className="mb-3">Quick Actions</h6>
      <Row className="g-2">
        {quickActions.map((action, index) => (
          <Col xs={6} sm={4} key={index}>
            <Button
              as={Link}
              to={action.path}
              variant={action.variant}
              className="mobile-quick-action-btn w-100"
              disabled={!action.available}
            >
              <div className="mobile-quick-action-content">
                <i className={`bi bi-${action.icon} mb-1`}></i>
                <div className="mobile-quick-action-label">{action.label}</div>
              </div>
            </Button>
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default MobileQuickActions;
