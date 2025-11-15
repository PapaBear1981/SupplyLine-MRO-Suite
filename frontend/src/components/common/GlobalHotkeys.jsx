import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { toggleTheme } from '../../store/themeSlice';
import { useHotkeyContext } from '../../context/HotkeyContext';
import useHotkeys from '../../hooks/useHotkeys';
import HotkeyHelp from './HotkeyHelp';

/**
 * Global Hotkeys Component
 * Manages application-wide keyboard shortcuts
 */
const GlobalHotkeys = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const { showHelpModal, setShowHelpModal, toggleHelpModal } = useHotkeyContext();
  const { user } = useSelector((state) => state.auth);

  // Check if user has permission for a page
  const hasPermission = (permission) => {
    if (!user || !user.permissions) return false;
    return user.permissions.includes(permission) || user.role === 'admin' || user.isAdmin;
  };

  // Global navigation hotkeys
  useHotkeys({
    // Navigation shortcuts
    'mod+d': () => {
      navigate('/dashboard');
    },
    'mod+t': () => {
      if (hasPermission('page.tools')) {
        navigate('/tools');
      }
    },
    'mod+k': () => {
      if (hasPermission('page.kits')) {
        navigate('/kits');
      }
    },
    'mod+c': () => {
      if (hasPermission('page.chemicals')) {
        navigate('/chemicals');
      }
    },
    'mod+o': () => {
      if (hasPermission('page.orders')) {
        navigate('/orders');
      }
    },
    'mod+h': () => {
      navigate('/history');
    },
    'mod+s': () => {
      if (hasPermission('page.scanner')) {
        navigate('/scanner');
      }
    },
    'mod+r': () => {
      navigate('/reports');
    },
    'mod+shift+c': () => {
      if (hasPermission('page.checkouts')) {
        navigate('/checkouts/all');
      } else if (hasPermission('page.my_checkouts')) {
        navigate('/checkouts');
      }
    },
    'mod+w': () => {
      if (hasPermission('page.warehouses')) {
        navigate('/warehouses');
      }
    },

    // Action shortcuts
    'mod+shift+t': () => {
      dispatch(toggleTheme());
    },
    'mod+p': (e) => {
      // Prevent browser print dialog
      e.preventDefault();
      navigate('/profile');
    },
    'mod+/': (e) => {
      // Prevent browser default
      e.preventDefault();
      toggleHelpModal();
    },

    // Admin shortcuts
    'mod+shift+a': () => {
      if (hasPermission('page.admin_dashboard') || user?.role === 'admin' || user?.isAdmin) {
        navigate('/admin/dashboard');
      }
    }
  }, {
    enableOnFormTags: false,
    deps: [navigate, dispatch, user]
  });

  return (
    <HotkeyHelp
      show={showHelpModal}
      onHide={() => setShowHelpModal(false)}
    />
  );
};

export default GlobalHotkeys;
