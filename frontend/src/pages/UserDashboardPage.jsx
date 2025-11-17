import { useCallback, useEffect, useMemo, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Row, Col, Button, Modal, List, Card, Typography, Space, Tooltip, Divider } from 'antd';
import {
  SettingOutlined,
  ReloadOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  EyeInvisibleOutlined,
  EyeOutlined,
  SwapOutlined,
  DashboardOutlined,
  CalendarOutlined,
} from '@ant-design/icons';
import { toast } from 'react-toastify';
import { fetchRegistrationRequests } from '../store/adminSlice';
import EnterprisePageHeader from '../components/common/EnterprisePageHeader';
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
import '../styles/dashboardThemes.css';

const { Text, Title } = Typography;

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
    () => DASHBOARD_WIDGETS.filter((widget) => widget.isAvailable(roleFlags)),
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
        [COLUMN_SIDEBAR]: Array.isArray(base[COLUMN_SIDEBAR]) ? base[COLUMN_SIDEBAR].filter((id) => availableSet.has(id)) : [],
        [COLUMN_HIDDEN]: Array.isArray(base[COLUMN_HIDDEN]) ? base[COLUMN_HIDDEN].filter((id) => availableSet.has(id)) : [],
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

  // Consolidated layout initialization
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

  const moveWidget = (column, index, direction) => {
    setLayout((currentLayout) => {
      const updatedColumn = [...currentLayout[column]];
      const newIndex = index + direction;
      if (newIndex < 0 || newIndex >= updatedColumn.length) {
        return currentLayout;
      }
      [updatedColumn[index], updatedColumn[newIndex]] = [updatedColumn[newIndex], updatedColumn[index]];
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
      return (
        <div key={id} style={{ marginBottom: 24 }}>
          <Component />
        </div>
      );
    });

  // Expose the customize function to the window object so ProfileModal can access it
  useEffect(() => {
    window.openDashboardCustomizer = () => setShowCustomizer(true);
    return () => {
      delete window.openDashboardCustomizer;
    };
  }, []);

  const currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="enterprise-dashboard" data-testid="dashboard-content">
      <EnterprisePageHeader
        title={`Welcome back, ${user?.name || 'User'}`}
        subtitle={`Here's your operational overview for today`}
        icon={<DashboardOutlined />}
        breadcrumbs={[{ title: 'Dashboard' }]}
        actions={[
          {
            label: 'Customize',
            icon: <SettingOutlined />,
            onClick: () => setShowCustomizer(true),
          },
        ]}
        meta={[
          {
            icon: <CalendarOutlined />,
            label: 'Date',
            value: currentDate,
          },
        ]}
      />

      <Row gutter={[24, 24]}>
        {/* Main content area - 2/3 width on large screens */}
        <Col xs={24} lg={16}>
          {renderWidgets(layout[COLUMN_MAIN])}
        </Col>

        {/* Sidebar - 1/3 width on large screens */}
        <Col xs={24} lg={8}>
          {renderWidgets(layout[COLUMN_SIDEBAR])}
        </Col>
      </Row>

      <Modal
        title="Customize Dashboard"
        open={showCustomizer}
        onCancel={() => setShowCustomizer(false)}
        width={900}
        footer={[
          <Button key="reset" onClick={resetLayout}>
            Reset to Default
          </Button>,
          <Button key="done" type="primary" onClick={() => setShowCustomizer(false)}>
            Done
          </Button>,
        ]}
      >
        <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
          Reorder, hide, or move widgets between columns. Changes are saved automatically for your account.
        </Text>

        <Row gutter={16}>
          <Col span={8}>
            <Card
              title={<Text strong>Main Column</Text>}
              size="small"
              style={{ height: '100%' }}
            >
              <List
                dataSource={layout[COLUMN_MAIN]}
                renderItem={(widgetId, index) => {
                  const widget = widgetLookup[widgetId];
                  return (
                    <List.Item
                      style={{ display: 'block', padding: '12px 0' }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                        <Text strong>{widget?.label}</Text>
                        <Space size={4}>
                          <Tooltip title="Move Up">
                            <Button
                              size="small"
                              icon={<ArrowUpOutlined />}
                              onClick={() => moveWidget(COLUMN_MAIN, index, -1)}
                              disabled={index === 0}
                            />
                          </Tooltip>
                          <Tooltip title="Move Down">
                            <Button
                              size="small"
                              icon={<ArrowDownOutlined />}
                              onClick={() => moveWidget(COLUMN_MAIN, index, 1)}
                              disabled={index === layout[COLUMN_MAIN].length - 1}
                            />
                          </Tooltip>
                        </Space>
                      </div>
                      <Space size={8}>
                        <Button
                          size="small"
                          icon={<SwapOutlined />}
                          onClick={() => moveWidgetToColumn(widgetId, COLUMN_MAIN, COLUMN_SIDEBAR)}
                        >
                          To Sidebar
                        </Button>
                        <Button
                          size="small"
                          danger
                          icon={<EyeInvisibleOutlined />}
                          onClick={() => hideWidget(widgetId, COLUMN_MAIN)}
                        >
                          Hide
                        </Button>
                      </Space>
                    </List.Item>
                  );
                }}
                locale={{ emptyText: 'No widgets in this column' }}
              />
            </Card>
          </Col>

          <Col span={8}>
            <Card
              title={<Text strong>Sidebar</Text>}
              size="small"
              style={{ height: '100%' }}
            >
              <List
                dataSource={layout[COLUMN_SIDEBAR]}
                renderItem={(widgetId, index) => {
                  const widget = widgetLookup[widgetId];
                  return (
                    <List.Item
                      style={{ display: 'block', padding: '12px 0' }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                        <Text strong>{widget?.label}</Text>
                        <Space size={4}>
                          <Tooltip title="Move Up">
                            <Button
                              size="small"
                              icon={<ArrowUpOutlined />}
                              onClick={() => moveWidget(COLUMN_SIDEBAR, index, -1)}
                              disabled={index === 0}
                            />
                          </Tooltip>
                          <Tooltip title="Move Down">
                            <Button
                              size="small"
                              icon={<ArrowDownOutlined />}
                              onClick={() => moveWidget(COLUMN_SIDEBAR, index, 1)}
                              disabled={index === layout[COLUMN_SIDEBAR].length - 1}
                            />
                          </Tooltip>
                        </Space>
                      </div>
                      <Space size={8}>
                        <Button
                          size="small"
                          icon={<SwapOutlined />}
                          onClick={() => moveWidgetToColumn(widgetId, COLUMN_SIDEBAR, COLUMN_MAIN)}
                        >
                          To Main
                        </Button>
                        <Button
                          size="small"
                          danger
                          icon={<EyeInvisibleOutlined />}
                          onClick={() => hideWidget(widgetId, COLUMN_SIDEBAR)}
                        >
                          Hide
                        </Button>
                      </Space>
                    </List.Item>
                  );
                }}
                locale={{ emptyText: 'No widgets in this column' }}
              />
            </Card>
          </Col>

          <Col span={8}>
            <Card
              title={<Text strong>Hidden Widgets</Text>}
              size="small"
              style={{ height: '100%' }}
            >
              <List
                dataSource={layout[COLUMN_HIDDEN]}
                renderItem={(widgetId) => {
                  const widget = widgetLookup[widgetId];
                  return (
                    <List.Item
                      style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                    >
                      <Text strong>{widget?.label}</Text>
                      <Button
                        size="small"
                        type="primary"
                        ghost
                        icon={<EyeOutlined />}
                        onClick={() => restoreWidget(widgetId)}
                      >
                        Restore
                      </Button>
                    </List.Item>
                  );
                }}
                locale={{ emptyText: 'No hidden widgets' }}
              />
            </Card>
          </Col>
        </Row>
      </Modal>
    </div>
  );
};

export default UserDashboardPage;
