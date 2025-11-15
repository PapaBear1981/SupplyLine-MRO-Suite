import { useEffect, useRef, useCallback } from 'react';
import { useHotkeyContext } from '../context/HotkeyContext';
import { matchesHotkey, shouldIgnoreHotkey } from '../utils/hotkeyHelpers';

/**
 * Custom hook for registering hotkeys in components
 *
 * @param {Object} hotkeyMap - Map of hotkey strings to callback functions
 *   Example: { 'mod+d': () => navigate('/dashboard'), 'n': () => createNew() }
 * @param {Object} options - Configuration options
 *   - enabled: Whether hotkeys are active (default: true)
 *   - enableOnFormTags: Allow hotkeys even in form elements (default: false)
 *   - preventDefault: Prevent default browser behavior (default: true)
 *   - deps: Dependency array for callbacks (default: [])
 *
 * @example
 * useHotkeys({
 *   'mod+s': handleSave,
 *   'escape': handleClose,
 *   '/': () => searchRef.current.focus()
 * }, { enabled: isModalOpen });
 */
export const useHotkeys = (hotkeyMap, options = {}) => {
  const {
    enabled = true,
    enableOnFormTags = false,
    preventDefault = true,
    deps = []
  } = options;

  const { isEnabled } = useHotkeyContext();
  const hotkeyMapRef = useRef(hotkeyMap);

  // Update ref when hotkeyMap changes
  useEffect(() => {
    hotkeyMapRef.current = hotkeyMap;
  }, [hotkeyMap]);

  const handleKeyDown = useCallback((event) => {
    // Check if hotkeys are globally enabled
    if (!isEnabled()) {
      return;
    }

    // Check if component-level enabled
    if (!enabled) {
      return;
    }

    // Check each hotkey in the map
    let matched = false;
    Object.entries(hotkeyMapRef.current).forEach(([hotkey, callback]) => {
      // Skip if hotkey should be ignored (e.g., typing in input)
      if (!enableOnFormTags && shouldIgnoreHotkey(event, hotkey)) {
        return;
      }

      // Check if the event matches this hotkey
      if (matchesHotkey(event, hotkey)) {
        matched = true;

        // Log in development mode
        if (import.meta.env.DEV) {
          console.log(`[Hotkey] Matched: ${hotkey}`);
        }

        // Prevent default browser behavior and stop propagation
        if (preventDefault) {
          event.preventDefault();
          event.stopPropagation();
        }

        // Call the callback
        if (typeof callback === 'function') {
          callback(event);
        }
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, enableOnFormTags, preventDefault, isEnabled, ...deps]);

  useEffect(() => {
    // Only attach listener if hotkeys are enabled
    if (!enabled || !isEnabled()) {
      return;
    }

    // Use capture phase to catch events before browser defaults
    window.addEventListener('keydown', handleKeyDown, true);

    return () => {
      window.removeEventListener('keydown', handleKeyDown, true);
    };
  }, [enabled, handleKeyDown, isEnabled]);
};

/**
 * Hook for a single hotkey
 *
 * @param {string} hotkey - The hotkey string (e.g., 'mod+s')
 * @param {Function} callback - Function to call when hotkey is pressed
 * @param {Object} options - Same options as useHotkeys
 *
 * @example
 * useHotkey('mod+s', handleSave, { enabled: isDirty });
 */
export const useHotkey = (hotkey, callback, options = {}) => {
  const hotkeyMap = { [hotkey]: callback };
  useHotkeys(hotkeyMap, options);
};

export default useHotkeys;
