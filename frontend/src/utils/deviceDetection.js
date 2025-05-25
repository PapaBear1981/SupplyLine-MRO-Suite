import { useState, useEffect } from 'react';

/**
 * Device detection hook for responsive design
 * Detects device type and orientation changes
 */
export const useDeviceDetection = () => {
  const [deviceType, setDeviceType] = useState('desktop');
  const [orientation, setOrientation] = useState('portrait');
  const [isMobile, setIsMobile] = useState(false);
  const [isTablet, setIsTablet] = useState(false);

  useEffect(() => {
    const checkDevice = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      const userAgent = navigator.userAgent;
      
      // Check for mobile devices
      const mobileRegex = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i;
      const isMobileDevice = mobileRegex.test(userAgent);
      
      // Determine device type based on screen width
      if (width <= 768) {
        setDeviceType('mobile');
        setIsMobile(true);
        setIsTablet(false);
      } else if (width <= 1024) {
        setDeviceType('tablet');
        setIsMobile(false);
        setIsTablet(true);
      } else {
        setDeviceType('desktop');
        setIsMobile(false);
        setIsTablet(false);
      }
      
      // Determine orientation
      setOrientation(width > height ? 'landscape' : 'portrait');
    };
    
    // Initial check
    checkDevice();
    
    // Listen for resize events
    window.addEventListener('resize', checkDevice);
    window.addEventListener('orientationchange', checkDevice);
    
    return () => {
      window.removeEventListener('resize', checkDevice);
      window.removeEventListener('orientationchange', checkDevice);
    };
  }, []);

  return { 
    deviceType, 
    orientation, 
    isMobile, 
    isTablet,
    isDesktop: deviceType === 'desktop'
  };
};

/**
 * Get user preference for mobile/desktop view
 */
export const useViewPreference = () => {
  const [viewPreference, setViewPreference] = useState(() => {
    return localStorage.getItem('viewPreference') || 'auto';
  });

  const setPreference = (preference) => {
    setViewPreference(preference);
    localStorage.setItem('viewPreference', preference);
  };

  return { viewPreference, setPreference };
};

/**
 * Determine if mobile layout should be used
 */
export const useMobileLayout = () => {
  const { isMobile, isTablet } = useDeviceDetection();
  const { viewPreference } = useViewPreference();

  const shouldUseMobileLayout = () => {
    if (viewPreference === 'mobile') return true;
    if (viewPreference === 'desktop') return false;
    return isMobile || isTablet;
  };

  return shouldUseMobileLayout();
};
