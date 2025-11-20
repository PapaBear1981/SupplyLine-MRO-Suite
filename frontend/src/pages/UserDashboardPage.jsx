import { useCallback, useEffect, useMemo, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Container, Row, Col, Button, Modal, ListGroup, ButtonGroup } from 'react-bootstrap';
import { toast } from 'react-toastify';
import { fetchRegistrationRequests } from '../store/adminSlice';
import CalibrationNotifications from '../components/calibration/CalibrationNotifications';
import UserCheckoutStatus from '../components/dashboard/UserCheckoutStatus';
import RecentActivity from '../components/dashboard/RecentActivity';
import Announcements from '../components/dashboard/Announcements';
import QuickActions from '../components/dashboard/QuickActions';
import PastDueTools from '../components/dashboard/PastDueTools';
import MyKits from '../components/dashboard/MyKits';
import KitAlertsSummary from '../components/dashboard/KitAlertsSummary';
import RecentKitActivity from '../components/dashboard/RecentKitActivity';
import LateOrdersWidget from '../components/dashboard/LateOrdersWidget';
import MyRequestsWidget from '../components/dashboard/MyRequestsWidget';
import PendingUserRequests from '../components/admin/PendingUserRequests';
import PendingUpdateRequestsWidget from '../components/dashboard/PendingUpdateRequestsWidget';
import GlobalSearch from '../components/common/GlobalSearch';
import '../styles/dashboardThemes.css';

// Constants for column names
const COLUMN_MAIN = 'main';
const COLUMN_SIDEBAR = 'sidebar';
const COLUMN_HIDDEN = 'hidden';

const DASHBOARD_WIDGETS = [
  {
    id: 'calibrationNotifications',
    label: 'Calibration Notifications',
    defaultColumn: COLUMN_MAIN,
    component: CalibrationNotifications,
    isAvailable: () => true,
  },
  {
    id: 'pastDueTools',
    label: 'Past Due Tools',
    defaultColumn: COLUMN_MAIN,
    component: PastDueTools,
    isAvailable: ({ canViewAdminWidgets }) => canViewAdminWidgets,
  },
  {
    id: 'kitAlerts',
    label: 'Kit Alerts Summary',
    defaultColumn: COLUMN_MAIN,
    component: KitAlertsSummary,
    isAvailable: () => true,
  },
  {
    id: 'checkoutStatus',
    label: 'My Checked Out Tools',
    defaultColumn: COLUMN_MAIN,
    component: UserCheckoutStatus,
    isAvailable: () => true,
  },
  {
    id: 'myKits',
    label: 'My Kits',
    defaultColumn: COLUMN_MAIN,
    component: MyKits,
    isAvailable: () => true,
  },
  {
    id: 'recentKitActivity',
    label: 'Recent Kit Activity',
    defaultColumn: COLUMN_MAIN,
    component: RecentKitActivity,
    isAvailable: () => true,
  },
  {
    id: 'recentActivity',
    label: 'Recent Activity',
    defaultColumn: COLUMN_MAIN,
    component: RecentActivity,
    isAvailable: () => true,
  },
  {
    id: 'announcements',
    label: 'Announcements',
    defaultColumn: COLUMN_SIDEBAR,
    component: Announcements,
    isAvailable: () => true,
  },
  {
    id: 'quickActions',
    label: 'Quick Actions',
    defaultColumn: COLUMN_SIDEBAR,
    component: QuickActions,
    isAvailable: () => true,
  },
  {
    id: 'lateOrders',
    label: 'Late Orders',
    defaultColumn: COLUMN_SIDEBAR,
    component: LateOrdersWidget,
    isAvailable: ({ hasOrderPermission }) => hasOrderPermission,
  },
  {
    id: 'myRequests',
    label: 'My Open Requests',
    defaultColumn: COLUMN_SIDEBAR,
    component: MyRequestsWidget,
    isAvailable: ({ hasRequestPermission }) => hasRequestPermission,
  },
  {
    id: 'pendingUpdateRequests',
    label: 'Pending Update Requests',
    defaultColumn: COLUMN_SIDEBAR,
    component: PendingUpdateRequestsWidget,
    isAvailable: ({ hasOrderPermission }) => hasOrderPermission,
  },
  {
    id: 'pendingUserRequests',
    label: 'Pending User Requests',
    defaultColumn: COLUMN_SIDEBAR,
    component: PendingUserRequests,
    isAvailable: ({ isAdmin }) => isAdmin,
  },
];

const UserDashboardPage = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin;
  const isMaterials = user?.department === 'Materials';
  const canViewAdminWidgets = isAdmin || isMaterials;
  const hasOrderPermission = Boolean(isAdmin || (user?.permissions || []).includes('page.orders'));
  const hasRequestPermission = Boolean(isAdmin || (user?.permissions || []).includes('page.requests') || (user?.permissions || []).includes('page.orders'));

  // Fetch registration requests for admins
  useEffect(() => {
    if (isAdmin) {
      dispatch(fetchRegistrationRequests('pending'));
    }
  }, [dispatch, isAdmin]);

  const widgetLookup = useMemo(() => {
    const lookup = {};
    DASHBOARD_WIDGETS.forEach((widget) => {
      lookup[widget.id] = widget;
    });
    return lookup;
  }, []);

  const roleFlags = useMemo(
    () => ({ isAdmin, isMaterials, canViewAdminWidgets, hasOrderPermission, hasRequestPermission }),
    [isAdmin, isMaterials, canViewAdminWidgets, hasOrderPermission, hasRequestPermission]
  );

  const availableWidgets = useMemo(
    () =>
      DASHBOARD_WIDGETS.filter((widget) => widget.isAvailable(roleFlags)),
    [roleFlags]
  );

  const availableWidgetIds = useMemo(
    () => availableWidgets.map((widget) => widget.id),
    [availableWidgets]
  );

  const layoutStorageKey = useMemo(
    () => `dashboardLayout_${user?.id || 'guest'}`,
    [user?.id]
  );

  const normalizeLayout = useCallback(
    (savedLayout) => {
      const availableSet = new Set(availableWidgetIds);
      const base = savedLayout || {};

      const normalized = {
        [COLUMN_MAIN]: Array.isArray(base[COLUMN_MAIN]) ? base[COLUMN_MAIN].filter((id) => availableSet.has(id)) : [],
        [COLUMN_SIDEBAR]: Array.isArray(base[COLUMN_SIDEBAR])
          ? base[COLUMN_SIDEBAR].filter((id) => availableSet.has(id))
          : [],
        [COLUMN_HIDDEN]: Array.isArray(base[COLUMN_HIDDEN])
          ? base[COLUMN_HIDDEN].filter((id) => availableSet.has(id))
          : [],
      };

      const used = new Set([...normalized[COLUMN_MAIN], ...normalized[COLUMN_SIDEBAR], ...normalized[COLUMN_HIDDEN]]);

      availableWidgetIds.forEach((id) => {
        if (!used.has(id)) {
          const widget = widgetLookup[id];
          const column = widget?.defaultColumn || COLUMN_MAIN;
          normalized[column] = [...normalized[column], id];
          used.add(id);
        }
      });

      return normalized;
    },
    [availableWidgetIds, widgetLookup]
  );

  const defaultLayout = useMemo(() => {
    const layout = { [COLUMN_MAIN]: [], [COLUMN_SIDEBAR]: [], [COLUMN_HIDDEN]: [] };
    availableWidgetIds.forEach((id) => {
      const widget = widgetLookup[id];
      const column = widget?.defaultColumn || COLUMN_MAIN;
      layout[column].push(id);
    });
    return layout;
  }, [availableWidgetIds, widgetLookup]);

  const cloneLayout = useCallback(
    (layout) => ({
      [COLUMN_MAIN]: [...layout[COLUMN_MAIN]],
      [COLUMN_SIDEBAR]: [...layout[COLUMN_SIDEBAR]],
      [COLUMN_HIDDEN]: [...layout[COLUMN_HIDDEN]],
    }),
    []
  );

  const [layout, setLayout] = useState(() => {
    if (typeof window === 'undefined') {
      return cloneLayout(defaultLayout);
    }

    try {
      const saved = localStorage.getItem(layoutStorageKey);
      if (saved) {
        return normalizeLayout(JSON.parse(saved));
      }
    } catch (error) {
      console.warn('Failed to load dashboard layout:', error);
      toast.error('Failed to load your dashboard layout. Using default layout.');
    }

    return cloneLayout(defaultLayout);
  });

  const [showCustomizer, setShowCustomizer] = useState(false);

  // Consolidated layout initialization - handles both initial load and storage key changes
  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    try {
      const saved = localStorage.getItem(layoutStorageKey);
      if (saved) {
        const parsedLayout = JSON.parse(saved);
        setLayout(normalizeLayout(parsedLayout));
      } else {
        setLayout(cloneLayout(defaultLayout));
      }
    } catch (error) {
      console.warn('Failed to reload dashboard layout:', error);
      toast.error('Failed to load your dashboard layout. Using default layout.');
      setLayout(cloneLayout(defaultLayout));
    }
  }, [layoutStorageKey, defaultLayout, normalizeLayout, cloneLayout]);

  // Persist layout changes to localStorage
  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    try {
      localStorage.setItem(layoutStorageKey, JSON.stringify(layout));
    } catch (error) {
      console.error('Failed to persist dashboard layout:', error);
      toast.error('Failed to save your dashboard layout. Changes may not persist.');
    }
  }, [layout, layoutStorageKey]);

  const roleThemeClass = useMemo(() => {
    if (isAdmin) {
      return 'dashboard-theme-admin';
    }
    if (isMaterials) {
      return 'dashboard-theme-materials';
    }
    return 'dashboard-theme-standard';
  }, [isAdmin, isMaterials]);

  const moveWidget = (column, index, direction) => {
    setLayout((currentLayout) => {
      const updatedColumn = [...currentLayout[column]];
      const newIndex = index + direction;
      if (newIndex < 0 || newIndex >= updatedColumn.length) {
        return currentLayout;
      }
      [updatedColumn[index], updatedColumn[newIndex]] = [
        updatedColumn[newIndex],
        updatedColumn[index],
      ];
      return {
        ...currentLayout,
        [column]: updatedColumn,
      };
    });
  };

  const moveWidgetToColumn = (widgetId, fromColumn, toColumn) => {
    setLayout((currentLayout) => {
      const source = currentLayout[fromColumn].filter((id) => id !== widgetId);
      const destination = [...currentLayout[toColumn], widgetId];
      return {
        ...currentLayout,
        [fromColumn]: source,
        [toColumn]: destination,
      };
    });
  };

  const hideWidget = (widgetId, fromColumn) => {
    setLayout((currentLayout) => ({
      ...currentLayout,
      [fromColumn]: currentLayout[fromColumn].filter((id) => id !== widgetId),
      [COLUMN_HIDDEN]: currentLayout[COLUMN_HIDDEN].includes(widgetId)
        ? currentLayout[COLUMN_HIDDEN]
        : [...currentLayout[COLUMN_HIDDEN], widgetId],
    }));
  };

  const restoreWidget = (widgetId) => {
    const defaultColumn = widgetLookup[widgetId]?.defaultColumn || COLUMN_MAIN;
    setLayout((currentLayout) => ({
      ...currentLayout,
      [defaultColumn]: currentLayout[defaultColumn].includes(widgetId)
        ? currentLayout[defaultColumn]
        : [...currentLayout[defaultColumn], widgetId],
      [COLUMN_HIDDEN]: currentLayout[COLUMN_HIDDEN].filter((id) => id !== widgetId),
    }));
  };

  const resetLayout = () => {
    setLayout(cloneLayout(defaultLayout));
  };

  const renderWidgets = (widgetIds) =>
    widgetIds.map((id) => {
      const widget = widgetLookup[id];
      if (!widget) {
        return null;
      }
      const Component = widget.component;
      return <Component key={id} />;
    });

  // Reusable component for rendering widget list in customization modal
  const renderWidgetList = (columnName, widgetIds, canMoveToColumn) => (
    <ListGroup>
      {widgetIds.map((widgetId, index) => {
        const widget = widgetLookup[widgetId];
        return (
          <ListGroup.Item
            key={widgetId}
            className="d-flex flex-column gap-2"
          >
            <div className="d-flex justify-content-between align-items-center">
              <span className="fw-semibold">{widget?.label}</span>
              <ButtonGroup size="sm">
                <Button
                  variant="outline-secondary"
                  onClick={() => moveWidget(columnName, index, -1)}
                  disabled={index === 0}
                  aria-label="Move up"
                >
                  <i className="bi bi-arrow-up"></i>
                </Button>
                <Button
                  variant="outline-secondary"
                  onClick={() => moveWidget(columnName, index, 1)}
                  disabled={index === widgetIds.length - 1}
                  aria-label="Move down"
                >
                  <i className="bi bi-arrow-down"></i>
                </Button>
              </ButtonGroup>
            </div>
            <div className="d-flex gap-2 flex-wrap">
              {canMoveToColumn && (
                <Button
                  variant="outline-primary"
                  size="sm"
                  onClick={() => moveWidgetToColumn(widgetId, columnName, canMoveToColumn)}
                >
                  Move to {canMoveToColumn === COLUMN_MAIN ? 'Main' : 'Sidebar'}
                </Button>
              )}
              <Button
                variant="outline-danger"
                size="sm"
                onClick={() => hideWidget(widgetId, columnName)}
              >
                Hide
              </Button>
            </div>
          </ListGroup.Item>
        );
      })}
      {widgetIds.length === 0 && (
        <ListGroup.Item className="text-muted">
          No widgets in this column.
        </ListGroup.Item>
      )}
    </ListGroup>
  );

  // Expose the customize function to the window object so ProfileModal can access it
  useEffect(() => {
    window.openDashboardCustomizer = () => setShowCustomizer(true);
    return () => {
      delete window.openDashboardCustomizer;
    };
  }, []);

  return (
    <div
      className={`dashboard-root w-100 ${roleThemeClass}`}
      data-testid="dashboard-content"
    >
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div className="w-100 mb-3">
          <GlobalSearch />
        </div>
        <h1 className="mb-0">Dashboard</h1>
      </div>

      <Container fluid className="p-0">
        <Row>
          {/* Main content area - 2/3 width on large screens */}
          <Col lg={8}>{renderWidgets(layout[COLUMN_MAIN])}</Col>

          {/* Sidebar - 1/3 width on large screens */}
          <Col lg={4}>{renderWidgets(layout[COLUMN_SIDEBAR])}</Col>
        </Row>
      </Container>

      <Modal
        show={showCustomizer}
        onHide={() => setShowCustomizer(false)}
        size="lg"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Customize Dashboard</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p className="text-muted">
            Reorder, hide, or move widgets between columns. Changes are saved
            automatically for your account.
          </p>
          <Row className="gy-3">
            <Col md={4}>
              <h6 className="text-uppercase text-muted mb-2">Main Column</h6>
              {renderWidgetList(COLUMN_MAIN, layout[COLUMN_MAIN], COLUMN_SIDEBAR)}
            </Col>
            <Col md={4}>
              <h6 className="text-uppercase text-muted mb-2">Sidebar</h6>
              {renderWidgetList(COLUMN_SIDEBAR, layout[COLUMN_SIDEBAR], COLUMN_MAIN)}
            </Col>
            <Col md={4}>
              <h6 className="text-uppercase text-muted mb-2">Hidden Widgets</h6>
              <ListGroup>
                {layout[COLUMN_HIDDEN].map((widgetId) => {
                  const widget = widgetLookup[widgetId];
                  return (
                    <ListGroup.Item
                      key={widgetId}
                      className="d-flex justify-content-between align-items-center"
                    >
                      <span className="fw-semibold">{widget?.label}</span>
                      <Button
                        variant="outline-success"
                        size="sm"
                        onClick={() => restoreWidget(widgetId)}
                      >
                        Restore
                      </Button>
                    </ListGroup.Item>
                  );
                })}
                {layout[COLUMN_HIDDEN].length === 0 && (
                  <ListGroup.Item className="text-muted">
                    No hidden widgets.
                  </ListGroup.Item>
                )}
              </ListGroup>
            </Col>
          </Row>
        </Modal.Body>
        <Modal.Footer className="d-flex justify-content-between">
          <Button variant="link" onClick={resetLayout}>
            Reset to Default
          </Button>
          <Button variant="primary" onClick={() => setShowCustomizer(false)}>
            Done
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default UserDashboardPage;
