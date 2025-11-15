/**
 * Hotkey Configuration
 * Defines all available hotkeys in the application
 */

export const HOTKEY_CATEGORIES = {
  NAVIGATION: 'Navigation',
  ACTIONS: 'Actions',
  LIST_VIEWS: 'List Views',
  MODALS: 'Modals',
  ADMIN: 'Admin'
};

export const HOTKEYS = {
  // Navigation hotkeys
  DASHBOARD: {
    key: 'mod+d',
    description: 'Go to Dashboard',
    category: HOTKEY_CATEGORIES.NAVIGATION,
    global: true
  },
  TOOLS: {
    key: 'mod+t',
    description: 'Go to Tools',
    category: HOTKEY_CATEGORIES.NAVIGATION,
    global: true
  },
  KITS: {
    key: 'mod+k',
    description: 'Go to Kits',
    category: HOTKEY_CATEGORIES.NAVIGATION,
    global: true
  },
  CHEMICALS: {
    key: 'mod+c',
    description: 'Go to Chemicals',
    category: HOTKEY_CATEGORIES.NAVIGATION,
    global: true
  },
  ORDERS: {
    key: 'mod+o',
    description: 'Go to Orders',
    category: HOTKEY_CATEGORIES.NAVIGATION,
    global: true
  },
  HISTORY: {
    key: 'mod+h',
    description: 'Go to History',
    category: HOTKEY_CATEGORIES.NAVIGATION,
    global: true
  },
  SCANNER: {
    key: 'mod+s',
    description: 'Go to Scanner',
    category: HOTKEY_CATEGORIES.NAVIGATION,
    global: true
  },
  REPORTS: {
    key: 'mod+r',
    description: 'Go to Reports',
    category: HOTKEY_CATEGORIES.NAVIGATION,
    global: true
  },
  CHECKOUTS: {
    key: 'mod+shift+c',
    description: 'Go to Checkouts',
    category: HOTKEY_CATEGORIES.NAVIGATION,
    global: true
  },
  WAREHOUSES: {
    key: 'mod+w',
    description: 'Go to Warehouses',
    category: HOTKEY_CATEGORIES.NAVIGATION,
    global: true
  },

  // Action hotkeys
  TOGGLE_SIDEBAR: {
    key: 'mod+b',
    description: 'Toggle Sidebar',
    category: HOTKEY_CATEGORIES.ACTIONS,
    global: true
  },
  OPEN_PROFILE: {
    key: 'mod+p',
    description: 'Open Profile',
    category: HOTKEY_CATEGORIES.ACTIONS,
    global: true
  },
  TOGGLE_THEME: {
    key: 'mod+shift+t',
    description: 'Toggle Theme',
    category: HOTKEY_CATEGORIES.ACTIONS,
    global: true
  },
  SHOW_HELP: {
    key: '?',
    description: 'Show Help',
    category: HOTKEY_CATEGORIES.ACTIONS,
    global: true
  },
  SHOW_HOTKEYS: {
    key: 'mod+/',
    description: 'Show Hotkey Cheat Sheet',
    category: HOTKEY_CATEGORIES.ACTIONS,
    global: true
  },
  FOCUS_SEARCH: {
    key: '/',
    description: 'Focus Search',
    category: HOTKEY_CATEGORIES.ACTIONS,
    global: false
  },

  // List view hotkeys (context-specific)
  NEW_ITEM: {
    key: 'n',
    description: 'Create New Item',
    category: HOTKEY_CATEGORIES.LIST_VIEWS,
    global: false
  },
  TOGGLE_FILTERS: {
    key: 'f',
    description: 'Toggle Filters',
    category: HOTKEY_CATEGORIES.LIST_VIEWS,
    global: false
  },
  CLEAR_SEARCH: {
    key: 'mod+shift+x',
    description: 'Clear Search',
    category: HOTKEY_CATEGORIES.LIST_VIEWS,
    global: false
  },
  NEXT_ITEM: {
    key: 'j',
    description: 'Next Item',
    category: HOTKEY_CATEGORIES.LIST_VIEWS,
    global: false
  },
  PREV_ITEM: {
    key: 'k',
    description: 'Previous Item',
    category: HOTKEY_CATEGORIES.LIST_VIEWS,
    global: false
  },

  // Modal hotkeys
  CLOSE_MODAL: {
    key: 'escape',
    description: 'Close Modal',
    category: HOTKEY_CATEGORIES.MODALS,
    global: false
  },

  // Admin hotkeys
  ADMIN_DASHBOARD: {
    key: 'mod+shift+a',
    description: 'Admin Dashboard',
    category: HOTKEY_CATEGORIES.ADMIN,
    global: true,
    requiresAdmin: true
  }
};

// Group hotkeys by category for display
export const getHotkeysByCategory = () => {
  const grouped = {};

  Object.keys(HOTKEY_CATEGORIES).forEach(category => {
    grouped[HOTKEY_CATEGORIES[category]] = [];
  });

  Object.entries(HOTKEYS).forEach(([name, config]) => {
    grouped[config.category].push({
      name,
      ...config
    });
  });

  return grouped;
};

// Format hotkey for display (e.g., "mod+d" -> "Ctrl+D" or "⌘D")
export const formatHotkeyForDisplay = (hotkey) => {
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  const modKey = isMac ? '⌘' : 'Ctrl';

  return hotkey
    .replace(/mod\+/g, `${modKey}+`)
    .replace(/shift\+/g, 'Shift+')
    .replace(/alt\+/g, 'Alt+')
    .replace(/ctrl\+/g, 'Ctrl+')
    .split('+')
    .map(part => part.charAt(0).toUpperCase() + part.slice(1))
    .join('+');
};

export default HOTKEYS;
