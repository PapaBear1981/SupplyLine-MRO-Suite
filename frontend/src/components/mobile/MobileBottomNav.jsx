import { Link, useLocation } from 'react-router-dom';
import { Badge } from 'react-bootstrap';

const MobileBottomNav = ({ user }) => {
  const location = useLocation();

  const navItems = [
    { 
      path: '/dashboard', 
      icon: 'house', 
      label: 'Home',
      exact: true
    },
    { 
      path: '/tools', 
      icon: 'tools', 
      label: 'Tools' 
    },
    { 
      path: '/checkouts', 
      icon: 'clipboard-check', 
      label: 'Checkouts' 
    },
    { 
      path: '/scanner', 
      icon: 'upc-scan', 
      label: 'Scanner' 
    },
    { 
      path: '/profile', 
      icon: 'person', 
      label: 'Profile' 
    }
  ];

  const isActive = (item) => {
    if (item.exact) {
      return location.pathname === item.path || location.pathname === '/';
    }
    return location.pathname.startsWith(item.path);
  };

  return (
    <nav className="mobile-bottom-nav">
      {navItems.map(item => (
        <Link 
          key={item.path}
          to={item.path}
          className={`mobile-nav-item ${isActive(item) ? 'active' : ''}`}
        >
          <div className="mobile-nav-icon">
            <i className={`bi bi-${item.icon}`}></i>
            {/* Add notification badges for specific items */}
            {item.path === '/checkouts' && (
              <Badge bg="danger" className="mobile-nav-badge">
                {/* This would be populated with actual checkout count */}
              </Badge>
            )}
          </div>
          <span className="mobile-nav-label">{item.label}</span>
        </Link>
      ))}
    </nav>
  );
};

export default MobileBottomNav;
