import { useCallback, useEffect, useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import { Container, Row, Col, Button, Modal, ListGroup, ButtonGroup } from 'react-bootstrap';
import OverdueChemicals from '../components/dashboard/OverdueChemicals';
import CalibrationNotifications from '../components/calibration/CalibrationNotifications';
import UserCheckoutStatus from '../components/dashboard/UserCheckoutStatus';
import RecentActivity from '../components/dashboard/RecentActivity';
import Announcements from '../components/dashboard/Announcements';
import QuickActions from '../components/dashboard/QuickActions';
import PastDueTools from '../components/dashboard/PastDueTools';
import MyKits from '../components/dashboard/MyKits';
import KitAlertsSummary from '../components/dashboard/KitAlertsSummary';
import RecentKitActivity from '../components/dashboard/RecentKitActivity';
import '../styles/dashboardThemes.css';

const DASHBOARD_WIDGETS = [
  {
    id: 'calibrationNotifications',
    label: 'Calibration Notifications',
    defaultColumn: 'main',
    component: CalibrationNotifications,
    isAvailable: () => true,
  },
  {
    id: 'overdueChemicals',
    label: 'Overdue Chemicals',
    defaultColumn: 'main',
    component: OverdueChemicals,
    isAvailable: ({ canViewAdminWidgets }) => canViewAdminWidgets,
  },
  {
    id: 'pastDueTools',
    label: 'Past Due Tools',
    defaultColumn: 'main',
    component: PastDueTools,
    isAvailable: ({ canViewAdminWidgets }) => canViewAdminWidgets,
  },
  {
    id: 'kitAlerts',
    label: 'Kit Alerts Summary',
    defaultColumn: 'main',
    component: KitAlertsSummary,
    isAvailable: () => true,
  },
  {
    id: 'checkoutStatus',
    label: 'My Checked Out Tools',
    defaultColumn: 'main',
    component: UserCheckoutStatus,
    isAvailable: () => true,
  },
  {
    id: 'myKits',
    label: 'My Kits',
    defaultColumn: 'main',
    component: MyKits,
    isAvailable: () => true,
  },
  {
    id: 'recentKitActivity',
    label: 'Recent Kit Activity',
    defaultColumn: 'main',
    component: RecentKitActivity,
    isAvailable: () => true,
  },
  {
    id: 'recentActivity',
    label: 'Recent Activity',
    defaultColumn: 'main',
    component: RecentActivity,
    isAvailable: () => true,
  },
  {
    id: 'announcements',
    label: 'Announcements',
    defaultColumn: 'sidebar',
    component: Announcements,
    isAvailable: () => true,
  },
  {
    id: 'quickActions',
    label: 'Quick Actions',
    defaultColumn: 'sidebar',
    component: QuickActions,
    isAvailable: () => true,
  },
];

const UserDashboardPage = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin;
  const isMaterials = user?.department === 'Materials';
  const canViewAdminWidgets = isAdmin || isMaterials;

  const widgetLookup = useMemo(() => {
    const lookup = {};
    DASHBOARD_WIDGETS.forEach((widget) => {
      lookup[widget.id] = widget;
    });
    return lookup;
  }, []);

  const roleFlags = useMemo(
    () => ({ isAdmin, isMaterials, canViewAdminWidgets }),
    [isAdmin, isMaterials, canViewAdminWidgets]
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
        main: Array.isArray(base.main) ? base.main.filter((id) => availableSet.has(id)) : [],
        sidebar: Array.isArray(base.sidebar)
          ? base.sidebar.filter((id) => availableSet.has(id))
          : [],
        hidden: Array.isArray(base.hidden)
          ? base.hidden.filter((id) => availableSet.has(id))
          : [],
      };

      const used = new Set([...normalized.main, ...normalized.sidebar, ...normalized.hidden]);

      availableWidgetIds.forEach((id) => {
        if (!used.has(id)) {
          const widget = widgetLookup[id];
          const column = widget?.defaultColumn || 'main';
          normalized[column] = [...normalized[column], id];
          used.add(id);
        }
      });

      return normalized;
    },
    [availableWidgetIds, widgetLookup]
  );

  const defaultLayout = useMemo(() => {
    const layout = { main: [], sidebar: [], hidden: [] };
    availableWidgetIds.forEach((id) => {
      const widget = widgetLookup[id];
      const column = widget?.defaultColumn || 'main';
      layout[column].push(id);
    });
    return layout;
  }, [availableWidgetIds, widgetLookup]);

  const cloneLayout = useCallback(
    (layout) => ({
      main: [...layout.main],
      sidebar: [...layout.sidebar],
      hidden: [...layout.hidden],
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
    }

    return cloneLayout(defaultLayout);
  });

  const [showCustomizer, setShowCustomizer] = useState(false);

  useEffect(() => {
    setLayout((currentLayout) => normalizeLayout(currentLayout));
  }, [normalizeLayout]);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    try {
      const saved = localStorage.getItem(layoutStorageKey);
      if (saved) {
        setLayout(normalizeLayout(JSON.parse(saved)));
      } else {
        setLayout(cloneLayout(defaultLayout));
      }
    } catch (error) {
      console.warn('Failed to reload dashboard layout:', error);
      setLayout(cloneLayout(defaultLayout));
    }
  }, [layoutStorageKey, defaultLayout, normalizeLayout, cloneLayout]);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    try {
      localStorage.setItem(layoutStorageKey, JSON.stringify(layout));
    } catch (error) {
      console.warn('Failed to persist dashboard layout:', error);
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
      hidden: currentLayout.hidden.includes(widgetId)
        ? currentLayout.hidden
        : [...currentLayout.hidden, widgetId],
    }));
  };

  const restoreWidget = (widgetId) => {
    const defaultColumn = widgetLookup[widgetId]?.defaultColumn || 'main';
    setLayout((currentLayout) => ({
      ...currentLayout,
      [defaultColumn]: currentLayout[defaultColumn].includes(widgetId)
        ? currentLayout[defaultColumn]
        : [...currentLayout[defaultColumn], widgetId],
      hidden: currentLayout.hidden.filter((id) => id !== widgetId),
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

  return (
    <div
      className={`dashboard-root w-100 ${roleThemeClass}`}
      data-testid="dashboard-content"
    >
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <h1 className="mb-0">Dashboard</h1>
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={() => setShowCustomizer(true)}
        >
          <i className="bi bi-sliders me-2"></i>
          Customize
        </Button>
      </div>

      <Container fluid className="p-0">
        <Row>
          {/* Main content area - 2/3 width on large screens */}
          <Col lg={8}>{renderWidgets(layout.main)}</Col>

          {/* Sidebar - 1/3 width on large screens */}
          <Col lg={4}>{renderWidgets(layout.sidebar)}</Col>
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
              <ListGroup>
                {layout.main.map((widgetId, index) => {
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
                            onClick={() => moveWidget('main', index, -1)}
                            disabled={index === 0}
                            aria-label="Move up"
                          >
                            <i className="bi bi-arrow-up"></i>
                          </Button>
                          <Button
                            variant="outline-secondary"
                            onClick={() => moveWidget('main', index, 1)}
                            disabled={index === layout.main.length - 1}
                            aria-label="Move down"
                          >
                            <i className="bi bi-arrow-down"></i>
                          </Button>
                        </ButtonGroup>
                      </div>
                      <div className="d-flex gap-2 flex-wrap">
                        <Button
                          variant="outline-primary"
                          size="sm"
                          onClick={() => moveWidgetToColumn(widgetId, 'main', 'sidebar')}
                        >
                          Move to Sidebar
                        </Button>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => hideWidget(widgetId, 'main')}
                        >
                          Hide
                        </Button>
                      </div>
                    </ListGroup.Item>
                  );
                })}
                {layout.main.length === 0 && (
                  <ListGroup.Item className="text-muted">
                    No widgets in the main column.
                  </ListGroup.Item>
                )}
              </ListGroup>
            </Col>
            <Col md={4}>
              <h6 className="text-uppercase text-muted mb-2">Sidebar</h6>
              <ListGroup>
                {layout.sidebar.map((widgetId, index) => {
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
                            onClick={() => moveWidget('sidebar', index, -1)}
                            disabled={index === 0}
                            aria-label="Move up"
                          >
                            <i className="bi bi-arrow-up"></i>
                          </Button>
                          <Button
                            variant="outline-secondary"
                            onClick={() => moveWidget('sidebar', index, 1)}
                            disabled={index === layout.sidebar.length - 1}
                            aria-label="Move down"
                          >
                            <i className="bi bi-arrow-down"></i>
                          </Button>
                        </ButtonGroup>
                      </div>
                      <div className="d-flex gap-2 flex-wrap">
                        <Button
                          variant="outline-primary"
                          size="sm"
                          onClick={() => moveWidgetToColumn(widgetId, 'sidebar', 'main')}
                        >
                          Move to Main
                        </Button>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => hideWidget(widgetId, 'sidebar')}
                        >
                          Hide
                        </Button>
                      </div>
                    </ListGroup.Item>
                  );
                })}
                {layout.sidebar.length === 0 && (
                  <ListGroup.Item className="text-muted">
                    No widgets in the sidebar.
                  </ListGroup.Item>
                )}
              </ListGroup>
            </Col>
            <Col md={4}>
              <h6 className="text-uppercase text-muted mb-2">Hidden Widgets</h6>
              <ListGroup>
                {layout.hidden.map((widgetId) => {
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
                {layout.hidden.length === 0 && (
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
