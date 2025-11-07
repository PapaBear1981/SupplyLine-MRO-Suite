import { useEffect, useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import { Card, Button, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';

const QuickActions = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin;
  const isMaterials = user?.department === 'Materials';

  const storageKey = useMemo(
    () => `dashboardFavoriteActions_${user?.id || 'guest'}`,
    [user?.id]
  );

  const [favoriteActions, setFavoriteActions] = useState([]);

  const commonActions = useMemo(
    () => [
      {
        id: 'checkoutTool',
        title: 'Checkout Tool',
        icon: 'box-arrow-right',
        link: '/tools',
        variant: 'primary'
      },
      {
        id: 'myCheckouts',
        title: 'My Checkouts',
        icon: 'list-check',
        link: '/my-checkouts',
        variant: 'info'
      },
      {
        id: 'viewKits',
        title: 'View Kits',
        icon: 'box',
        link: '/kits',
        variant: 'success'
      },
      {
        id: 'viewProfile',
        title: 'View Profile',
        icon: 'person',
        link: '/profile',
        variant: 'secondary'
      }
    ],
    []
  );

  const actions = useMemo(() => {
    if (isAdmin) {
      return [
        ...commonActions,
        {
          id: 'adminDashboard',
          title: 'Admin Dashboard',
          icon: 'speedometer2',
          link: '/admin/dashboard',
          variant: 'danger'
        },
        {
          id: 'addTool',
          title: 'Add New Tool',
          icon: 'plus-circle',
          link: '/tools/new',
          variant: 'success'
        },
        {
          id: 'manageUsers',
          title: 'Manage Users',
          icon: 'people',
          link: '/admin/dashboard',
          variant: 'warning',
          state: { activeTab: 'users' }
        }
      ];
    }

    if (isMaterials) {
      return [
        ...commonActions,
        {
          id: 'addTool',
          title: 'Add New Tool',
          icon: 'plus-circle',
          link: '/tools/new',
          variant: 'success'
        },
        {
          id: 'manageChemicals',
          title: 'Manage Chemicals',
          icon: 'flask',
          link: '/chemicals',
          variant: 'warning'
        },
        {
          id: 'calibrations',
          title: 'Calibrations',
          icon: 'rulers',
          link: '/calibrations',
          variant: 'danger'
        }
      ];
    }

    return [
      ...commonActions,
      {
        id: 'viewTools',
        title: 'View Tools',
        icon: 'tools',
        link: '/tools',
        variant: 'success'
      },
      {
        id: 'viewChemicals',
        title: 'View Chemicals',
        icon: 'flask',
        link: '/chemicals',
        variant: 'warning'
      },
      {
        id: 'help',
        title: 'Help',
        icon: 'question-circle',
        link: '/help',
        variant: 'dark'
      }
    ];
  }, [commonActions, isAdmin, isMaterials]);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) {
          const allowed = parsed.filter((id) => actions.some((action) => action.id === id));
          setFavoriteActions(allowed);
        }
      } else {
        setFavoriteActions([]);
      }
    } catch (error) {
      console.error('Unable to load dashboard favorites:', error);
      toast.error('Failed to load your favorite actions. Using defaults.');
      setFavoriteActions([]);
    }
  }, [actions, storageKey]);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    try {
      const allowedFavorites = favoriteActions.filter((id) =>
        actions.some((action) => action.id === id)
      );
      if (allowedFavorites.length !== favoriteActions.length) {
        setFavoriteActions(allowedFavorites);
        return;
      }
      localStorage.setItem(storageKey, JSON.stringify(favoriteActions));
    } catch (error) {
      console.error('Unable to store dashboard favorites:', error);
      toast.error('Failed to save your favorite actions. Changes may not persist.');
    }
  }, [actions, favoriteActions, storageKey]);

  const toggleFavorite = (event, actionId) => {
    event.preventDefault();
    event.stopPropagation();
    setFavoriteActions((prev) =>
      prev.includes(actionId)
        ? prev.filter((id) => id !== actionId)
        : [...prev, actionId]
    );
  };

  const favoriteActionList = actions.filter((action) => favoriteActions.includes(action.id));
  const remainingActions = actions.filter((action) => !favoriteActions.includes(action.id));

  const renderActionButton = (action) => (
    <Col xs={6} key={action.id}>
      <Button
        as={Link}
        to={action.link}
        state={action.state}
        variant={action.variant}
        className="w-100 d-flex flex-column align-items-center justify-content-center p-3 h-100 position-relative"
      >
        <button
          type="button"
          className="btn btn-link text-decoration-none position-absolute top-0 end-0 p-1"
          onClick={(event) => toggleFavorite(event, action.id)}
          aria-label={favoriteActions.includes(action.id) ? 'Unpin action' : 'Pin action'}
          title={favoriteActions.includes(action.id) ? 'Unpin from favorites' : 'Pin to favorites'}
          aria-pressed={favoriteActions.includes(action.id)}
        >
          <i
            className={`bi ${
              favoriteActions.includes(action.id)
                ? 'bi-star-fill text-warning'
                : 'bi-star text-light opacity-75'
            }`}
          ></i>
        </button>
        <i className={`bi bi-${action.icon} fs-4 mb-2`}></i>
        <span className="text-center">{action.title}</span>
      </Button>
    </Col>
  );

  return (
    <Card className="shadow-sm mb-4 fade-in" data-testid="quick-actions">
      <Card.Header className="bg-light">
        <h4 className="mb-0">Quick Actions</h4>
      </Card.Header>
      <Card.Body>
        {favoriteActionList.length > 0 && (
          <>
            <div className="d-flex justify-content-between align-items-center mb-2">
              <span className="text-uppercase text-muted small">Pinned Favorites</span>
              <span className="badge bg-warning text-dark">{favoriteActionList.length}</span>
            </div>
            <Row className="g-2 mb-3">{favoriteActionList.map(renderActionButton)}</Row>
            {remainingActions.length > 0 && <hr className="my-3" />}
          </>
        )}
        <Row className="g-2">
          {remainingActions.map(renderActionButton)}
        </Row>
      </Card.Body>
    </Card>
  );
};

export default QuickActions;
