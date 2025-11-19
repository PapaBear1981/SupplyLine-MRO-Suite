import { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Container, Nav, Button, OverlayTrigger, Tooltip, Spinner } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';
import { FaTools, FaBars, FaTimes } from 'react-icons/fa';
import ProfileModal from '../profile/ProfileModal';
import { APP_VERSION } from '../../utils/version';
import { useHelp } from '../../context/HelpContext';
import TourGuide from './TourGuide';
import { hasPermission } from '../auth/ProtectedRoute';
import { fetchSecuritySettings } from '../../store/securitySlice';
import useInactivityLogout from '../../hooks/useInactivityLogout';
import './MainLayout.css';

const MainLayout = ({ children }) => {
  const dispatch = useDispatch();
  const location = useLocation();
  const { user, isAuthenticated } = useSelector((state) => state.auth);
  const { hasLoaded: securityLoaded, loading: securityLoading } = useSelector((state) => state.security);
  const { showHelp, setShowHelp } = useHelp();
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showTour, setShowTour] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [transitionStage, setTransitionStage] = useState('idle');
  const [isRouteLoading, setIsRouteLoading] = useState(false);
  const transitionTimers = useRef({ exit: null, enter: null });
  const initialRenderRef = useRef(true);

  useInactivityLogout();

  useEffect(() => {
    if (isAuthenticated && !securityLoaded && !securityLoading) {
      dispatch(fetchSecuritySettings());
    }
  }, [dispatch, isAuthenticated, securityLoaded, securityLoading]);

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

  useEffect(() => () => {
    if (transitionTimers.current.exit) {
      clearTimeout(transitionTimers.current.exit);
    }
    if (transitionTimers.current.enter) {
      clearTimeout(transitionTimers.current.enter);
    }
  }, []);

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const transitionClassName = `page-transition page-transition--${transitionStage}`;

  return (
    <div className="main-layout">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        {/* Sidebar Header with Logo and Toggle */}
        <div className="sidebar-header">
          <Button
            variant="link"
            className="sidebar-toggle-btn"
            onClick={toggleSidebar}
            aria-label="Toggle sidebar"
          >
            {sidebarCollapsed ? <FaBars size={20} /> : <FaTimes size={20} />}
          </Button>
          {!sidebarCollapsed && (
            <Link to="/" className="sidebar-brand">
              <FaTools className="me-2" />
              <span>SupplyLine MRO</span>
            </Link>
          )}
        </div>

        {/* Sidebar Navigation */}
        <Nav className="flex-column sidebar-nav">
          {/* Dashboard is always visible to authenticated users */}
          <Nav.Link
            as={Link}
            to="/dashboard"
            className={location.pathname === '/dashboard' ? 'active' : ''}
          >
            <i className="bi bi-speedometer2"></i>
            {!sidebarCollapsed && <span>Dashboard</span>}
          </Nav.Link>

          {/* Show navigation links based on page permissions */}
          {user && (
            <>
              {hasPermission(user, 'page.tools') && (
                <Nav.Link
                  as={Link}
                  to="/tools"
                  className={location.pathname === '/tools' ? 'active' : ''}
                >
                  <i className="bi bi-tools"></i>
                  {!sidebarCollapsed && <span>Tools</span>}
                </Nav.Link>
              )}

              {hasPermission(user, 'page.orders') && (
                <Nav.Link
                  as={Link}
                  to="/orders"
                  className={location.pathname === '/orders' ? 'active' : ''}
                >
                  <i className="bi bi-cart"></i>
                  {!sidebarCollapsed && <span>Orders</span>}
                </Nav.Link>
              )}

              {hasPermission(user, 'page.requests') && (
                <Nav.Link
                  as={Link}
                  to="/requests"
                  className={location.pathname === '/requests' ? 'active' : ''}
                >
                  <i className="bi bi-journal-plus"></i>
                  {!sidebarCollapsed && <span>Requests</span>}
                </Nav.Link>
              )}

              {hasPermission(user, 'page.checkouts') && (
                <Nav.Link
                  as={Link}
                  to="/checkouts"
                  className={location.pathname === '/checkouts' ? 'active' : ''}
                >
                  <i className="bi bi-box-arrow-right"></i>
                  {!sidebarCollapsed && <span>Checkouts</span>}
                </Nav.Link>
              )}

              {hasPermission(user, 'page.kits') && (
                <Nav.Link
                  as={Link}
                  to="/kits"
                  className={location.pathname === '/kits' ? 'active' : ''}
                >
                  <i className="bi bi-briefcase"></i>
                  {!sidebarCollapsed && <span>Kits</span>}
                </Nav.Link>
              )}

              {hasPermission(user, 'page.chemicals') && (
                <Nav.Link
                  as={Link}
                  to="/chemicals"
                  className={location.pathname === '/chemicals' ? 'active' : ''}
                >
                  <i className="bi bi-droplet"></i>
                  {!sidebarCollapsed && <span>Chemicals</span>}
                </Nav.Link>
              )}

              {hasPermission(user, 'page.calibrations') && (
                <Nav.Link
                  as={Link}
                  to="/calibrations"
                  className={location.pathname === '/calibrations' ? 'active' : ''}
                >
                  <i className="bi bi-sliders"></i>
                  {!sidebarCollapsed && <span>Calibrations</span>}
                </Nav.Link>
              )}

              {hasPermission(user, 'page.warehouses') && (
                <Nav.Link
                  as={Link}
                  to="/warehouses"
                  className={location.pathname === '/warehouses' ? 'active' : ''}
                >
                  <i className="bi bi-building"></i>
                  {!sidebarCollapsed && <span>Warehouses</span>}
                </Nav.Link>
              )}

              {hasPermission(user, 'page.reports') && (
                <Nav.Link
                  as={Link}
                  to="/reports"
                  className={location.pathname === '/reports' ? 'active' : ''}
                >
                  <i className="bi bi-file-earmark-text"></i>
                  {!sidebarCollapsed && <span>Reports</span>}
                </Nav.Link>
              )}

              {/* Item History Lookup - Available to all authenticated users */}
              <Nav.Link
                as={Link}
                to="/history"
                className={location.pathname === '/history' ? 'active' : ''}
              >
                <i className="bi bi-clock-history"></i>
                {!sidebarCollapsed && <span>History</span>}
              </Nav.Link>

              {/* CYCLE COUNT NAVIGATION - TEMPORARILY DISABLED */}
              {/* ============================================== */}
              {/* The "Cycle Counts" navigation menu item has been disabled due to GitHub Issue #366 */}
              {/* */}
              {/* REASON FOR DISABLING: */}
              {/* - Cycle count system is completely non-functional */}
              {/* - Backend API endpoints return "Resource not found" errors */}
              {/* - Clicking this link leads to error pages that confuse users */}
              {/* - Production stability requires hiding broken functionality */}
              {/* */}
              {/* WHAT THIS NAVIGATION ITEM DID: */}
              {/* - Linked to /cycle-counts route (main cycle count dashboard) */}
              {/* - Provided access to inventory cycle counting operations */}
              {/* - Allowed users to schedule, execute, and review cycle counts */}
              {/* */}
              {/* TO RE-ENABLE: */}
              {/* 1. Uncomment the Nav.Link below */}
              {/* 2. Ensure cycle count routes are enabled in App.jsx */}
              {/* 3. Verify backend cycle count routes work (backend/routes.py) */}
              {/* 4. Test that all cycle count functionality works end-to-end */}
              {/* */}
              {/* DISABLED DATE: 2025-06-22 */}
              {/* GITHUB ISSUE: #366 */}
              {/* <Nav.Link as={Link} to="/cycle-counts">Cycle Counts</Nav.Link> */}

              {/* Directory Link - Visible to users with user.view permission */}
              {hasPermission(user, 'user.view') && (
                <Nav.Link
                  as={Link}
                  to="/directory"
                  className={location.pathname === '/directory' ? 'active' : ''}
                >
                  <i className="bi bi-people"></i>
                  {!sidebarCollapsed && <span>Directory</span>}
                </Nav.Link>
              )}

              {/* Only show Admin Dashboard to users with permission */}
              {hasPermission(user, 'page.admin_dashboard') && (
                <Nav.Link
                  as={Link}
                  to="/admin/dashboard"
                  className={location.pathname === '/admin/dashboard' ? 'active' : ''}
                >
                  <i className="bi bi-gear"></i>
                  {!sidebarCollapsed && <span>Admin Dashboard</span>}
                </Nav.Link>
              )}
            </>
          )}
        </Nav>

        {/* Sidebar User Section - Moved to Bottom */}
        {isAuthenticated && (
          <div className="sidebar-user-section">
            <Button
              variant="link"
              className="sidebar-user-btn w-100"
              onClick={() => setShowProfileModal(true)}
              data-testid="user-menu"
            >
              {user?.avatar ? (
                <img
                  src={user.avatar}
                  alt="User Avatar"
                  className="sidebar-avatar"
                  style={{ objectFit: 'cover' }}
                />
              ) : (
                <div className="sidebar-avatar bg-primary text-white">
                  {user?.name?.charAt(0) || 'U'}
                </div>
              )}
              {!sidebarCollapsed && (
                <span className="sidebar-user-name">{user?.name || 'User'}</span>
              )}
            </Button>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className={`main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <Container fluid className="flex-grow-1 px-4 py-0">
          <div key={location.pathname} className={transitionClassName}>
            {children}
          </div>
        </Container>

        <footer className="main-footer py-3 mt-auto">
          <Container fluid>
            <div className="d-flex justify-content-between">
              <span>SupplyLine MRO Suite &copy; {new Date().getFullYear()}</span>
              <span>Version {APP_VERSION}</span>
            </div>
          </Container>
        </footer>
      </div>

      {/* Profile Modal */}
      <ProfileModal
        show={showProfileModal}
        onHide={() => setShowProfileModal(false)}
        onShowTour={() => setShowTour(true)}
        onToggleHelp={() => setShowHelp(!showHelp)}
        showHelp={showHelp}
      />

      {/* Tour Guide */}
      <TourGuide
        show={showTour}
        onClose={() => setShowTour(false)}
        title="SupplyLine MRO Suite Tour"
        steps={[
          {
            title: 'Welcome to SupplyLine MRO Suite',
            content: 'This guided tour will help you understand the key features of the application. Click Next to continue or Skip Tour to exit at any time.'
          },
          {
            title: 'Navigation',
            content: 'The navigation sidebar on the left provides access to all main sections of the application, including Tools, Checkouts, Chemicals, and more. You can collapse it using the menu button.'
          },
          {
            title: 'Tool Management',
            content: 'The Tools section allows you to view, search, and manage all tools in the inventory. You can checkout tools, view their details, and track their status.'
          },
          {
            title: 'Checkout System',
            content: 'The Checkouts section shows tools that are currently checked out to users. You can return tools, view checkout history, and manage your checkouts.'
          },
          {
            title: 'Cycle Count',
            content: 'The Cycle Count section allows you to manage inventory counts, create count schedules, and track discrepancies to maintain accurate inventory records.'
          },
          {
            title: 'Help Features',
            content: 'Throughout the application, you\'ll find help icons (?) that provide contextual information about features. You can also toggle help features on/off using the help button in the top navigation bar.'
          },
          {
            title: 'User Profile',
            content: 'Click on your name in the top-right corner to access your profile, change settings, or log out.'
          },
          {
            title: 'That\'s it!',
            content: 'You\'re now ready to use SupplyLine MRO Suite. If you need help at any time, look for the help icons or start this tour again from the navigation bar.'
          }
        ]}
      />

      {isRouteLoading && (
        <div className="page-loading-overlay" role="status" aria-live="polite">
          <Spinner animation="border" variant="light">
            <span className="visually-hidden">Loading next section</span>
          </Spinner>
          <span className="page-loading-message">Loading next section…</span>
        </div>
      )}
    </div>
  );
};

export default MainLayout;
