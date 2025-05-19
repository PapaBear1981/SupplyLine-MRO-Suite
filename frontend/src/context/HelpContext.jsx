import { createContext, useContext, useState, useEffect } from 'react';

// Create the context
const HelpContext = createContext();

/**
 * Help content for different features in the application
 */
const helpContent = {
  // Tool Management
  toolList: {
    title: 'Tool Inventory',
    content: 'This page displays all tools in the inventory. You can search, filter, and sort tools by various criteria. Click on a tool to view its details or use the action buttons to perform operations like checkout or maintenance.'
  },
  toolDetail: {
    title: 'Tool Details',
    content: 'This page shows detailed information about a specific tool, including its status, location, and history. You can checkout the tool, view its service history, or perform administrative actions if you have the appropriate permissions.'
  },
  toolCheckout: {
    title: 'Tool Checkout',
    content: 'Use this feature to check out a tool for yourself or assign it to another user. Checked out tools will be marked as unavailable in the inventory until they are returned.'
  },
  toolReturn: {
    title: 'Tool Return',
    content: 'Return a tool to the inventory when you\'re done using it. The tool will be marked as available for other users to check out.'
  },
  toolMaintenance: {
    title: 'Tool Maintenance',
    content: 'Mark a tool as under maintenance when it needs repair or calibration. This will make the tool unavailable for checkout until it is returned to service.'
  },
  
  // Chemical Management
  chemicalList: {
    title: 'Chemical Inventory',
    content: 'This page displays all chemicals in the inventory. You can search, filter, and sort chemicals by various criteria. Click on a chemical to view its details or use the action buttons to perform operations.'
  },
  chemicalDetail: {
    title: 'Chemical Details',
    content: 'This page shows detailed information about a specific chemical, including its properties, location, and expiration date. You can view its usage history or perform administrative actions if you have the appropriate permissions.'
  },
  
  // Calibration
  calibrationList: {
    title: 'Calibration Management',
    content: 'This page displays all calibration records for tools that require regular calibration. You can view upcoming calibrations, overdue calibrations, and calibration history.'
  },
  calibrationDetail: {
    title: 'Calibration Details',
    content: 'This page shows detailed information about a specific calibration record, including the standards used, results, and next calibration date.'
  },
  
  // Reports
  reports: {
    title: 'Reports',
    content: 'Generate various reports about tool usage, chemical inventory, calibrations, and more. You can export reports in different formats or schedule them to be sent automatically.'
  },
  
  // Admin Dashboard
  adminDashboard: {
    title: 'Admin Dashboard',
    content: 'The admin dashboard provides access to system-wide settings, user management, and other administrative functions. Only users with admin privileges can access this page.'
  },
  userManagement: {
    title: 'User Management',
    content: 'Manage users in the system, including creating new users, editing user information, and assigning roles and permissions.'
  }
};

/**
 * Provider component for the help context
 */
export const HelpProvider = ({ children }) => {
  const [showHelp, setShowHelp] = useState(true);
  const [showTooltips, setShowTooltips] = useState(true);
  
  // Load user preferences from localStorage
  useEffect(() => {
    const helpPreferences = localStorage.getItem('helpPreferences');
    if (helpPreferences) {
      const { showHelp: savedShowHelp, showTooltips: savedShowTooltips } = JSON.parse(helpPreferences);
      setShowHelp(savedShowHelp);
      setShowTooltips(savedShowTooltips);
    }
  }, []);
  
  // Save user preferences to localStorage
  const savePreferences = (showHelp, showTooltips) => {
    localStorage.setItem('helpPreferences', JSON.stringify({ showHelp, showTooltips }));
    setShowHelp(showHelp);
    setShowTooltips(showTooltips);
  };
  
  // Get help content for a specific feature
  const getHelpContent = (feature) => {
    return helpContent[feature] || { title: 'Help', content: 'No help content available for this feature.' };
  };
  
  return (
    <HelpContext.Provider value={{ 
      showHelp, 
      showTooltips, 
      setShowHelp, 
      setShowTooltips,
      savePreferences,
      getHelpContent,
      helpContent
    }}>
      {children}
    </HelpContext.Provider>
  );
};

/**
 * Custom hook to use the help context
 */
export const useHelp = () => {
  const context = useContext(HelpContext);
  if (!context) {
    throw new Error('useHelp must be used within a HelpProvider');
  }
  return context;
};

export default HelpContext;
