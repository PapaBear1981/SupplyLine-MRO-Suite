import { useSelector } from 'react-redux';
import { Card, Button, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import Tooltip from '../common/Tooltip';
import { useHelp } from '../../context/HelpContext';

const QuickActions = () => {
  const { user } = useSelector((state) => state.auth);
  const { showTooltips } = useHelp();
  const isAdmin = user?.is_admin;
  const isMaterials = user?.department === 'Materials';

  // Define quick actions based on user role
  const getQuickActions = () => {
    const commonActions = [
      {
        title: 'Checkout Tool',
        icon: 'box-arrow-right',
        link: '/tools',
        variant: 'primary',
        tooltip: 'Browse and checkout tools from inventory'
      },
      {
        title: 'My Checkouts',
        icon: 'list-check',
        link: '/my-checkouts',
        variant: 'info',
        tooltip: 'View tools currently checked out to you'
      },
      {
        title: 'View Profile',
        icon: 'person',
        link: '/profile',
        variant: 'secondary',
        tooltip: 'View and edit your user profile settings'
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
          variant: 'danger',
          tooltip: 'Access administrative functions and system overview'
        },
        {
          title: 'Add New Tool',
          icon: 'plus-circle',
          link: '/tools/new',
          variant: 'success',
          tooltip: 'Add a new tool to the inventory system'
        },
        {
          title: 'Manage Users',
          icon: 'people',
          link: '/admin/dashboard',
          variant: 'warning',
          state: { activeTab: 'users' },
          tooltip: 'Manage user accounts and permissions'
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
          variant: 'success',
          tooltip: 'Add a new tool to the inventory system'
        },
        {
          title: 'Manage Chemicals',
          icon: 'flask',
          link: '/chemicals',
          variant: 'warning',
          tooltip: 'View and manage chemical inventory'
        },
        {
          title: 'Calibrations',
          icon: 'rulers',
          link: '/calibrations',
          variant: 'danger',
          tooltip: 'Manage tool calibrations and schedules'
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
        variant: 'success',
        tooltip: 'Browse available tools in inventory'
      },
      {
        title: 'View Chemicals',
        icon: 'flask',
        link: '/chemicals',
        variant: 'warning',
        tooltip: 'View chemical inventory and information'
      },
      {
        title: 'Help',
        icon: 'question-circle',
        link: '/help',
        variant: 'dark',
        tooltip: 'Access help documentation and support'
      }
    ];
  };

  const actions = getQuickActions();

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header className="bg-light">
        <h4 className="mb-0">Quick Actions</h4>
      </Card.Header>
      <Card.Body>
        <Row className="g-2">
          {actions.map((action, index) => (
            <Col xs={6} key={index}>
              <Tooltip text={showTooltips ? action.tooltip : null} placement="top">
                <Button
                  as={Link}
                  to={action.link}
                  state={action.state}
                  variant={action.variant}
                  className="w-100 d-flex flex-column align-items-center justify-content-center p-3 h-100"
                  aria-label={action.tooltip}
                >
                  <i className={`bi bi-${action.icon} fs-4 mb-2`}></i>
                  <span>{action.title}</span>
                </Button>
              </Tooltip>
            </Col>
          ))}
        </Row>
      </Card.Body>
    </Card>
  );
};

export default QuickActions;
