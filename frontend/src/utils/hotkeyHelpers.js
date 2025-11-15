/**
 * Hotkey Helper Utilities
 * Helper functions for keyboard event handling
 */

/**
 * Check if an element is an input field
 * @param {HTMLElement} element - The element to check
 * @returns {boolean}
 */
export const isInputElement = (element) => {
  if (!element) return false;

  const tagName = element.tagName.toLowerCase();
  const editableElements = ['input', 'textarea', 'select'];

  return (
    editableElements.includes(tagName) ||
    element.isContentEditable ||
    element.getAttribute('contenteditable') === 'true'
  );
};

/**
 * Check if the modifier key matches (Ctrl on Windows/Linux, Cmd on Mac)
 * @param {KeyboardEvent} event
 * @returns {boolean}
 */
export const isModKey = (event) => {
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  return isMac ? event.metaKey : event.ctrlKey;
};

/**
 * Parse a hotkey string into its components
 * @param {string} hotkeyString - e.g., "mod+shift+t"
 * @returns {Object} - { key, modifiers: { mod, shift, alt, ctrl } }
 */
export const parseHotkey = (hotkeyString) => {
  const parts = hotkeyString.toLowerCase().split('+');
  const key = parts[parts.length - 1];
  const modifiers = {
    mod: parts.includes('mod'),
    shift: parts.includes('shift'),
    alt: parts.includes('alt'),
    ctrl: parts.includes('ctrl')
  };

  return { key, modifiers };
};

/**
 * Check if a keyboard event matches a hotkey definition
 * @param {KeyboardEvent} event
 * @param {string} hotkeyString - e.g., "mod+d"
 * @returns {boolean}
 */
export const matchesHotkey = (event, hotkeyString) => {
  const { key, modifiers } = parseHotkey(hotkeyString);

  // Check if the base key matches
  const keyMatches = event.key.toLowerCase() === key.toLowerCase();

  // Check if modifiers match
  const modMatches = !modifiers.mod || isModKey(event);
  const shiftMatches = modifiers.shift === event.shiftKey;
  const altMatches = modifiers.alt === event.altKey;
  const ctrlMatches = !modifiers.ctrl || event.ctrlKey;

  // For "mod" key, we need to ensure the opposite modifier is NOT pressed
  // (e.g., on Mac, if we're checking for Cmd, Ctrl should not be pressed)
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  const noConflictingMod = !modifiers.mod || (
    isMac ? !event.ctrlKey : !event.metaKey
  );

  return keyMatches && modMatches && shiftMatches && altMatches && ctrlMatches && noConflictingMod;
};

/**
 * Check if hotkeys should be ignored (e.g., when typing in an input)
 * @param {KeyboardEvent} event
 * @param {string} hotkeyString - The hotkey to check
 * @returns {boolean} - true if the hotkey should be ignored
 */
export const shouldIgnoreHotkey = (event, hotkeyString) => {
  const target = event.target;

  // Always allow Escape and certain mod+ combinations even in input fields
  const alwaysAllow = ['escape', 'mod+/', 'mod+p', 'mod+s'];
  if (alwaysAllow.some(allowed => hotkeyString.toLowerCase().includes(allowed))) {
    return false;
  }

  // Ignore single-key hotkeys when in an input field
  if (isInputElement(target)) {
    const { modifiers } = parseHotkey(hotkeyString);
    // If hotkey doesn't use any modifiers, ignore it in input fields
    if (!modifiers.mod && !modifiers.ctrl && !modifiers.alt && !modifiers.shift) {
      return true;
    }
  }

  return false;
};

/**
 * Get the platform-specific modifier key name
 * @returns {string} - "Cmd" or "Ctrl"
 */
export const getModKeyName = () => {
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  return isMac ? 'Cmd' : 'Ctrl';
};

/**
 * Create a keyboard event listener with hotkey matching
 * @param {string} hotkeyString - The hotkey to listen for
 * @param {Function} callback - Function to call when hotkey is pressed
 * @param {Object} options - { preventDefault, stopPropagation, ignoreInInputs }
 * @returns {Function} - Event handler function
 */
export const createHotkeyHandler = (hotkeyString, callback, options = {}) => {
  const {
    preventDefault = true,
    stopPropagation = false,
    ignoreInInputs = true
  } = options;

  return (event) => {
    if (ignoreInInputs && shouldIgnoreHotkey(event, hotkeyString)) {
      return;
    }

    if (matchesHotkey(event, hotkeyString)) {
      if (preventDefault) {
        event.preventDefault();
      }
      if (stopPropagation) {
        event.stopPropagation();
      }
      callback(event);
    }
  };
};

export default {
  isInputElement,
  isModKey,
  parseHotkey,
  matchesHotkey,
  shouldIgnoreHotkey,
  getModKeyName,
  createHotkeyHandler
};
