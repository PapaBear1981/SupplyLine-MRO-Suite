import { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Layout, Menu, Avatar, Dropdown, Badge, Button, Tooltip, Spin, ConfigProvider, theme as antTheme } from 'antd';
import {
  DashboardOutlined,
  ToolOutlined,
  ShoppingCartOutlined,
  FileAddOutlined,
  ExportOutlined,
  ExperimentOutlined,
  SlidersFilled,
  BankOutlined,
  FileTextOutlined,
  HistoryOutlined,
  SettingOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  UserOutlined,
  BellOutlined,
  QuestionCircleOutlined,
  SunOutlined,
  MoonOutlined,
  LogoutOutlined,
  ProfileOutlined,
  AppstoreOutlined,
} from '@ant-design/icons';
import { fetchSecuritySettings } from '../../store/securitySlice';
import { logout } from '../../store/authSlice';
import { toggleTheme } from '../../store/themeSlice';
import { hasPermission } from '../auth/ProtectedRoute';
import useInactivityLogout from '../../hooks/useInactivityLogout';
import { useHelp } from '../../context/HelpContext';
import { APP_VERSION } from '../../utils/version';
import TourGuide from '../common/TourGuide';
import { enterpriseTheme, enterpriseDarkTheme } from '../../theme/enterpriseTheme';
import PropTypes from 'prop-types';

const { Header, Sider, Content, Footer } = Layout;

const EnterpriseLayout = ({ children }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated } = useSelector((state) => state.auth);
  const { theme: currentTheme } = useSelector((state) => state.theme);
  const { hasLoaded: securityLoaded, loading: securityLoading } = useSelector((state) => state.security);
  const { showHelp, setShowHelp } = useHelp();

  const [collapsed, setCollapsed] = useState(false);
  const [showTour, setShowTour] = useState(false);
  const [isRouteLoading, setIsRouteLoading] = useState(false);
  const [transitionStage, setTransitionStage] = useState('idle');
  const transitionTimers = useRef({ exit: null, enter: null });
  const initialRenderRef = useRef(true);

  useInactivityLogout();

  // Fetch security settings on mount
  useEffect(() => {
    if (isAuthenticated && !securityLoaded && !securityLoading) {
      dispatch(fetchSecuritySettings());
    }
  }, [dispatch, isAuthenticated, securityLoaded, securityLoading]);

  // Handle route transitions
  useEffect(() => {
    if (initialRenderRef.current) {
      initialRenderRef.current = false;
      setTransitionStage('idle');
      return;
    }

    if (transitionTimers.current.exit) {
      clearTimeout(transitionTimers.current.exit);
    }
    if (transitionTimers.current.enter) {
      clearTimeout(transitionTimers.current.enter);
    }

    setIsRouteLoading(true);
    setTransitionStage('exiting');

    transitionTimers.current.exit = setTimeout(() => {
      setTransitionStage('entering');
      transitionTimers.current.enter = setTimeout(() => {
        setTransitionStage('idle');
        setIsRouteLoading(false);
        transitionTimers.current.enter = null;
      }, 320);
      transitionTimers.current.exit = null;
    }, 120);

    return () => {
      if (transitionTimers.current.exit) {
        clearTimeout(transitionTimers.current.exit);
        transitionTimers.current.exit = null;
      }
      if (transitionTimers.current.enter) {
        clearTimeout(transitionTimers.current.enter);
        transitionTimers.current.enter = null;
      }
    };
  }, [location.pathname]);

  // Cleanup on unmount
  useEffect(() => () => {
    if (transitionTimers.current.exit) {
      clearTimeout(transitionTimers.current.exit);
    }
    if (transitionTimers.current.enter) {
      clearTimeout(transitionTimers.current.enter);
    }
  }, []);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const handleThemeToggle = () => {
    dispatch(toggleTheme());
  };

  // Build navigation items based on permissions
  const getMenuItems = () => {
    const items = [
      {
        key: '/dashboard',
        icon: <DashboardOutlined />,
        label: 'Dashboard',
      },
    ];

    if (user) {
      if (hasPermission(user, 'page.tools')) {
        items.push({
          key: '/tools',
          icon: <ToolOutlined />,
          label: 'Tools',
        });
      }

      if (hasPermission(user, 'page.orders')) {
        items.push({
          key: '/orders',
          icon: <ShoppingCartOutlined />,
          label: 'Orders',
        });
      }

      if (hasPermission(user, 'page.requests')) {
        items.push({
          key: '/requests',
          icon: <FileAddOutlined />,
          label: 'Requests',
        });
      }

      if (hasPermission(user, 'page.checkouts')) {
        items.push({
          key: '/checkouts',
          icon: <ExportOutlined />,
          label: 'Checkouts',
        });
      }

      if (hasPermission(user, 'page.kits')) {
        items.push({
          key: '/kits',
          icon: <AppstoreOutlined />,
          label: 'Kits',
        });
      }

      if (hasPermission(user, 'page.chemicals')) {
        items.push({
          key: '/chemicals',
          icon: <ExperimentOutlined />,
          label: 'Chemicals',
        });
      }

      if (hasPermission(user, 'page.calibrations')) {
        items.push({
          key: '/calibrations',
          icon: <SlidersFilled />,
          label: 'Calibrations',
        });
      }

      if (hasPermission(user, 'page.warehouses')) {
        items.push({
          key: '/warehouses',
          icon: <BankOutlined />,
          label: 'Warehouses',
        });
      }

      if (hasPermission(user, 'page.reports')) {
        items.push({
          key: '/reports',
          icon: <FileTextOutlined />,
          label: 'Reports',
        });
      }

      // History is available to all authenticated users
      items.push({
        key: '/history',
        icon: <HistoryOutlined />,
        label: 'History',
      });

      if (hasPermission(user, 'page.admin_dashboard')) {
        items.push({
          key: '/admin/dashboard',
          icon: <SettingOutlined />,
          label: 'Admin Dashboard',
        });
      }
    }

    return items;
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <ProfileOutlined />,
      label: 'Profile',
      onClick: () => navigate('/profile'),
    },
    {
      key: 'tour',
      icon: <QuestionCircleOutlined />,
      label: 'Start Tour',
      onClick: () => setShowTour(true),
    },
    {
      key: 'help',
      icon: <QuestionCircleOutlined />,
      label: showHelp ? 'Hide Help' : 'Show Help',
      onClick: () => setShowHelp(!showHelp),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      danger: true,
      onClick: handleLogout,
    },
  ];

  const selectedKeys = [location.pathname];
  const openKeys = [];

  // Determine if any parent menu should be open based on current path
  if (location.pathname.startsWith('/admin')) {
    openKeys.push('/admin/dashboard');
  }

  const transitionClassName = `page-transition page-transition--${transitionStage}`;

  const isDarkMode = currentTheme === 'dark';
  const selectedTheme = isDarkMode ? enterpriseDarkTheme : enterpriseTheme;

  return (
    <ConfigProvider
      theme={{
        ...selectedTheme,
        algorithm: isDarkMode ? antTheme.darkAlgorithm : antTheme.defaultAlgorithm,
      }}
    >
      <Layout className="enterprise-layout" style={{ minHeight: '100vh' }}>
        {/* Fixed Header */}
        <Header className="enterprise-header">
          <div className="enterprise-header-logo">
            <ToolOutlined style={{ fontSize: 24 }} />
            {!collapsed && <span>SupplyLine MRO Suite</span>}
          </div>

          <div className="enterprise-header-actions">
            <Tooltip title="Toggle Help">
              <Button
                type="text"
                icon={<QuestionCircleOutlined />}
                onClick={() => setShowHelp(!showHelp)}
                className="enterprise-header-action"
                style={{ color: 'rgba(255, 255, 255, 0.85)' }}
              />
            </Tooltip>

            <Tooltip title={isDarkMode ? 'Light Mode' : 'Dark Mode'}>
              <Button
                type="text"
                icon={isDarkMode ? <SunOutlined /> : <MoonOutlined />}
                onClick={handleThemeToggle}
                className="enterprise-header-action"
                style={{ color: 'rgba(255, 255, 255, 0.85)' }}
              />
            </Tooltip>

            <Badge count={0} size="small">
              <Tooltip title="Notifications">
                <Button
                  type="text"
                  icon={<BellOutlined />}
                  className="enterprise-header-action"
                  style={{ color: 'rgba(255, 255, 255, 0.85)' }}
                />
              </Tooltip>
            </Badge>

            {isAuthenticated && user && (
              <Dropdown
                menu={{ items: userMenuItems }}
                placement="bottomRight"
                trigger={['click']}
              >
                <div className="enterprise-user-menu">
                  <Avatar
                    size={32}
                    src={user.avatar}
                    icon={!user.avatar && <UserOutlined />}
                    className="enterprise-user-avatar"
                  >
                    {!user.avatar && user.name?.charAt(0)}
                  </Avatar>
                  {!collapsed && (
                    <span className="enterprise-user-name">{user.name || 'User'}</span>
                  )}
                </div>
              </Dropdown>
            )}
          </div>
        </Header>

        <Layout>
          {/* Sidebar Navigation */}
          <Sider
            trigger={null}
            collapsible
            collapsed={collapsed}
            width={240}
            collapsedWidth={64}
            className="enterprise-sider"
            style={{
              overflow: 'auto',
              height: 'calc(100vh - 48px)',
              position: 'fixed',
              left: 0,
              top: 48,
              bottom: 0,
              zIndex: 1000,
            }}
          >
            <div style={{ padding: '12px 8px', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <Button
                type="text"
                icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                onClick={() => setCollapsed(!collapsed)}
                style={{
                  fontSize: '16px',
                  width: collapsed ? 48 : '100%',
                  color: 'rgba(255, 255, 255, 0.85)',
                }}
              />
            </div>
            <Menu
              theme="dark"
              mode="inline"
              selectedKeys={selectedKeys}
              defaultOpenKeys={openKeys}
              items={getMenuItems()}
              onClick={({ key }) => navigate(key)}
              style={{
                background: 'transparent',
                borderRight: 'none',
              }}
            />
          </Sider>

          {/* Main Content Area */}
          <Layout
            style={{
              marginLeft: collapsed ? 64 : 240,
              marginTop: 48,
              transition: 'margin-left 0.2s ease',
              minHeight: 'calc(100vh - 48px)',
            }}
          >
            <Content
              style={{
                padding: 24,
                background: isDarkMode ? '#0d1b2a' : '#f4f6f9',
                minHeight: 'calc(100vh - 48px - 60px)',
              }}
            >
              <div key={location.pathname} className={transitionClassName}>
                <div className="enterprise-page enterprise-fade-in">
                  {children}
                </div>
              </div>
            </Content>

            <Footer className="enterprise-footer">
              <div style={{ display: 'flex', justifyContent: 'space-between', maxWidth: 1600, margin: '0 auto' }}>
                <span>SupplyLine MRO Suite &copy; {new Date().getFullYear()}</span>
                <span>Version {APP_VERSION}</span>
              </div>
            </Footer>
          </Layout>
        </Layout>

        {/* Tour Guide */}
        <TourGuide
          show={showTour}
          onClose={() => setShowTour(false)}
          title="SupplyLine MRO Suite Tour"
          steps={[
            {
              title: 'Welcome to SupplyLine MRO Suite',
              content: 'This guided tour will help you understand the key features of the application. Click Next to continue or Skip Tour to exit at any time.',
            },
            {
              title: 'Navigation',
              content: 'The navigation sidebar on the left provides access to all main sections of the application. You can collapse it using the menu button for more workspace.',
            },
            {
              title: 'Tool Management',
              content: 'The Tools section allows you to view, search, and manage all tools in the inventory. You can checkout tools, view their details, and track their status.',
            },
            {
              title: 'Checkout System',
              content: 'The Checkouts section shows tools that are currently checked out to users. You can return tools, view checkout history, and manage your checkouts.',
            },
            {
              title: 'Dashboard & Analytics',
              content: 'Your dashboard provides real-time insights into inventory status, pending actions, and key performance indicators.',
            },
            {
              title: 'Help & Support',
              content: 'Throughout the application, you\'ll find help icons that provide contextual information. Toggle help features using the help button in the header.',
            },
            {
              title: 'User Profile',
              content: 'Click on your avatar in the top-right corner to access your profile, change settings, start this tour again, or log out.',
            },
            {
              title: 'You\'re All Set!',
              content: 'You\'re now ready to use SupplyLine MRO Suite. If you need help at any time, look for the help icons or start this tour again from your profile menu.',
            },
          ]}
        />

        {/* Loading Overlay */}
        {isRouteLoading && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0, 0, 0, 0.4)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 2000,
            }}
          >
            <Spin size="large" />
            <div style={{ marginTop: 12, color: '#fff', fontSize: 13 }}>
              Loading next section...
            </div>
          </div>
        )}
      </Layout>
    </ConfigProvider>
  );
};

EnterpriseLayout.propTypes = {
  children: PropTypes.node.isRequired,
};

export default EnterpriseLayout;
