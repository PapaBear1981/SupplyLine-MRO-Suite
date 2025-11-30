import { useMemo } from 'react';
import { useSelector } from 'react-redux';
import { useLocation, useNavigate } from 'react-router-dom';
import { FaHome, FaBarcode, FaTools, FaClipboardList, FaUser } from 'react-icons/fa';
import './MobileLayout.css';

const MobileLayout = ({ children }) => {
  const { user } = useSelector((state) => state.auth);
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = useMemo(
    () => [
      { label: 'Home', icon: <FaHome />, path: '/mobile' },
      { label: 'Scan', icon: <FaBarcode />, path: '/scanner' },
      { label: 'Tools', icon: <FaTools />, path: '/tools' },
      { label: 'Requests', icon: <FaClipboardList />, path: '/requests' },
      { label: 'Profile', icon: <FaUser />, path: '/profile' }
    ],
    []
  );

  const isActive = (path) => {
    if (path === '/mobile') {
      return location.pathname === '/mobile';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="mobile-shell">
      <header className="mobile-shell__header">
        <div>
          <p className="mobile-shell__eyebrow">Signed in as</p>
          <h1 className="mobile-shell__title">{user?.full_name || user?.username || 'Team Member'}</h1>
          <p className="mobile-shell__subtitle">Tap a shortcut below to jump into your next task.</p>
        </div>
      </header>

      <main className="mobile-shell__content">{children}</main>

      <nav className="mobile-shell__nav" aria-label="Mobile primary navigation">
        {navItems.map((item) => (
          <button
            key={item.path}
            type="button"
            className={`mobile-shell__nav-item ${isActive(item.path) ? 'active' : ''}`}
            onClick={() => navigate(item.path)}
          >
            <span className="mobile-shell__nav-icon" aria-hidden>{item.icon}</span>
            <span className="mobile-shell__nav-label">{item.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
};

export default MobileLayout;
