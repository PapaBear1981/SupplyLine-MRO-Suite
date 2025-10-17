import { useSelector } from 'react-redux';
import { Card, Button, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const QuickActions = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin;
  const isMaterials = user?.department === 'Materials';
  
  // Define quick actions based on user role
  const getQuickActions = () => {
    const commonActions = [
      {
        title: 'Checkout Tool',
        icon: 'box-arrow-right',
        link: '/tools',
        variant: 'primary'
      },
      {
        title: 'My Checkouts',
        icon: 'list-check',
        link: '/my-checkouts',
        variant: 'info'
      },
      {
        title: 'View Kits',
        icon: 'box',
        link: '/kits',
        variant: 'success'
      },
      {
        title: 'View Profile',
        icon: 'person',
        link: '/profile',
        variant: 'secondary'
      }
    ];
    
    // Admin-specific actions
    if (isAdmin) {
      return [
        ...commonActions,
        { 
          title: 'Admin Dashboard', 
          icon: 'speedometer2', 
          link: '/admin/dashboard', 
          variant: 'danger' 
        },
        { 
          title: 'Add New Tool', 
          icon: 'plus-circle', 
          link: '/tools/new', 
          variant: 'success' 
        },
        { 
          title: 'Manage Users', 
          icon: 'people', 
          link: '/admin/dashboard', 
          variant: 'warning',
          state: { activeTab: 'users' }
        }
      ];
    }
    
    // Materials department actions
    if (isMaterials) {
      return [
        ...commonActions,
        { 
          title: 'Add New Tool', 
          icon: 'plus-circle', 
          link: '/tools/new', 
          variant: 'success' 
        },
        { 
          title: 'Manage Chemicals', 
          icon: 'flask', 
          link: '/chemicals', 
          variant: 'warning' 
        },
        { 
          title: 'Calibrations', 
          icon: 'rulers', 
          link: '/calibrations', 
          variant: 'danger' 
        }
      ];
    }
    
    // Regular user actions
    return [
      ...commonActions,
      { 
        title: 'View Tools', 
        icon: 'tools', 
        link: '/tools', 
        variant: 'success' 
      },
      { 
        title: 'View Chemicals', 
        icon: 'flask', 
        link: '/chemicals', 
        variant: 'warning' 
      },
      { 
        title: 'Help', 
        icon: 'question-circle', 
        link: '/help', 
        variant: 'dark' 
      }
    ];
  };
  
  const actions = getQuickActions();
  
  return (
    <Card className="shadow-sm mb-4" data-testid="quick-actions">
      <Card.Header className="bg-light">
        <h4 className="mb-0">Quick Actions</h4>
      </Card.Header>
      <Card.Body>
        <Row className="g-2">
          {actions.map((action, index) => (
            <Col xs={6} key={index}>
              <Button
                as={Link}
                to={action.link}
                state={action.state}
                variant={action.variant}
                className="w-100 d-flex flex-column align-items-center justify-content-center p-3 h-100"
              >
                <i className={`bi bi-${action.icon} fs-4 mb-2`}></i>
                <span>{action.title}</span>
              </Button>
            </Col>
          ))}
        </Row>
      </Card.Body>
    </Card>
  );
};

export default QuickActions;
