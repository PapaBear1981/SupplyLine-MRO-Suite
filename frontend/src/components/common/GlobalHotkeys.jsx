import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
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
  const dispatch = useDispatch();
  const { showHelpModal, setShowHelpModal, toggleHelpModal } = useHotkeyContext();

  // Global navigation hotkeys (using Alt to avoid browser conflicts)
  // Note: Routes themselves handle permission checks, so hotkeys just navigate
  useHotkeys({
    // Navigation shortcuts
    'alt+d': () => {
      navigate('/dashboard');
    },
    'alt+t': () => {
      navigate('/tools');
    },
    'alt+k': () => {
      navigate('/kits');
    },
    'alt+c': () => {
      navigate('/chemicals');
    },
    'alt+o': () => {
      navigate('/orders');
    },
    'alt+h': () => {
      navigate('/history');
    },
    'alt+s': () => {
      navigate('/scanner');
    },
    'alt+r': () => {
      navigate('/reports');
    },
    'alt+shift+c': () => {
      navigate('/checkouts');
    },
    'alt+w': () => {
      navigate('/warehouses');
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

    // Admin shortcuts (route will handle permission check)
    'mod+shift+a': () => {
      navigate('/admin/dashboard');
    }
  }, {
    enableOnFormTags: false,
    deps: [navigate, dispatch, toggleHelpModal]
  });

  return (
    <HotkeyHelp
      show={showHelpModal}
      onHide={() => setShowHelpModal(false)}
    />
  );
};

export default GlobalHotkeys;
