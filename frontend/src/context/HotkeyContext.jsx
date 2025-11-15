import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';

const HotkeyContext = createContext();

const STORAGE_KEY = 'hotkeyPreferences';

const DEFAULT_PREFERENCES = {
  enabled: true,
  disabled: [], // Array of hotkey names to disable
  customizations: {} // Future: user-defined hotkey mappings
};

export const HotkeyProvider = ({ children }) => {
  const [preferences, setPreferences] = useState(() => {
    // Load preferences from localStorage on init
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      const prefs = stored ? { ...DEFAULT_PREFERENCES, ...JSON.parse(stored) } : DEFAULT_PREFERENCES;
      if (import.meta.env.DEV) {
        console.log('[Hotkey] Initializing with preferences:', prefs);
      }
      return prefs;
    } catch (error) {
      console.error('Failed to load hotkey preferences:', error);
      return DEFAULT_PREFERENCES;
    }
  });

  const [showHelpModal, setShowHelpModal] = useState(false);

  // Save preferences to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
    } catch (error) {
      console.error('Failed to save hotkey preferences:', error);
    }
  }, [preferences]);

  /**
   * Check if hotkeys are globally enabled
   */
  const isEnabled = useCallback(() => {
    return preferences.enabled;
  }, [preferences.enabled]);

  /**
   * Check if a specific hotkey is enabled
   */
  const isHotkeyEnabled = useCallback((hotkeyName) => {
    return preferences.enabled && !preferences.disabled.includes(hotkeyName);
  }, [preferences.enabled, preferences.disabled]);

  /**
   * Enable or disable all hotkeys
   */
  const setHotkeysEnabled = useCallback((enabled) => {
    setPreferences(prev => ({
      ...prev,
      enabled
    }));
  }, []);

  /**
   * Enable or disable a specific hotkey
   */
  const setHotkeyEnabled = useCallback((hotkeyName, enabled) => {
    setPreferences(prev => {
      const disabled = enabled
        ? prev.disabled.filter(name => name !== hotkeyName)
        : [...prev.disabled, hotkeyName];

      return {
        ...prev,
        disabled
      };
    });
  }, []);

  /**
   * Reset preferences to defaults
   */
  const resetPreferences = useCallback(() => {
    setPreferences(DEFAULT_PREFERENCES);
  }, []);

  /**
   * Toggle the hotkey help modal
   */
  const toggleHelpModal = useCallback(() => {
    setShowHelpModal(prev => !prev);
  }, []);

  const value = {
    preferences,
    isEnabled,
    isHotkeyEnabled,
    setHotkeysEnabled,
    setHotkeyEnabled,
    resetPreferences,
    showHelpModal,
    setShowHelpModal,
    toggleHelpModal
  };

  return (
    <HotkeyContext.Provider value={value}>
      {children}
    </HotkeyContext.Provider>
  );
};

HotkeyProvider.propTypes = {
  children: PropTypes.node.isRequired
};

/**
 * Hook to access hotkey context
 */
export const useHotkeyContext = () => {
  const context = useContext(HotkeyContext);
  if (!context) {
    throw new Error('useHotkeyContext must be used within a HotkeyProvider');
  }
  return context;
};

export default HotkeyContext;
