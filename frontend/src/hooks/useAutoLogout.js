import { useEffect, useRef, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../store/authSlice';
import AuthService from '../services/authService';

/**
 * Custom hook for handling automatic logout functionality
 * Features:
 * - Configurable inactivity timeout
 * - Activity detection (mouse, keyboard, touch)
 * - Warning before logout
 * - Window/browser close detection
 */
const useAutoLogout = () => {
  const dispatch = useDispatch();
  const { isAuthenticated } = useSelector(state => state.auth);
  
  const timeoutRef = useRef(null);
  const warningTimeoutRef = useRef(null);
  const sessionCheckRef = useRef(null);
  const timeoutMinutesRef = useRef(30); // Default 30 minutes
  const lastActivityRef = useRef(Date.now());
  
  // Warning callback (can be overridden)
  const warningCallbackRef = useRef(null);
  
  // Get session info and timeout settings
  const getSessionInfo = useCallback(async () => {
    try {
      const response = await AuthService.getSessionInfo();
      if (response.authenticated && response.session) {
        timeoutMinutesRef.current = response.session.timeout_minutes;
        return response.session;
      }
      return null;
    } catch (error) {
      console.error('Failed to get session info:', error);
      return null;
    }
  }, []);

  // Reset the timeout
  const resetTimeout = useCallback(() => {
    if (!isAuthenticated) return;

    // Clear existing timeouts
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    if (warningTimeoutRef.current) {
      clearTimeout(warningTimeoutRef.current);
    }

    const timeoutMs = timeoutMinutesRef.current * 60 * 1000;
    const warningMs = Math.max(timeoutMs - (5 * 60 * 1000), timeoutMs * 0.8); // 5 minutes before or 80% of timeout

    // Set warning timeout
    warningTimeoutRef.current = setTimeout(() => {
      if (warningCallbackRef.current) {
        warningCallbackRef.current(5); // 5 minutes warning
      }
    }, warningMs);

    // Set logout timeout
    timeoutRef.current = setTimeout(() => {
      console.log('Auto logout due to inactivity');
      dispatch(logout());
    }, timeoutMs);

    lastActivityRef.current = Date.now();
  }, [isAuthenticated, dispatch]);

  // Handle user activity
  const handleActivity = useCallback(() => {
    if (!isAuthenticated) return;
    
    const now = Date.now();
    const timeSinceLastActivity = now - lastActivityRef.current;
    
    // Only reset if it's been more than 1 minute since last activity
    // This prevents excessive API calls
    if (timeSinceLastActivity > 60000) {
      resetTimeout();
    }
  }, [isAuthenticated, resetTimeout]);

  // Check session status periodically
  const checkSessionStatus = useCallback(async () => {
    if (!isAuthenticated) return;

    try {
      const sessionInfo = await getSessionInfo();
      if (!sessionInfo || !sessionInfo.is_active) {
        console.log('Session expired on server');
        dispatch(logout());
        return;
      }

      // Update timeout if it changed
      if (sessionInfo.timeout_minutes !== timeoutMinutesRef.current) {
        timeoutMinutesRef.current = sessionInfo.timeout_minutes;
        resetTimeout();
      }
    } catch (error) {
      console.error('Session check failed:', error);
      // Don't logout on network errors, just log
    }
  }, [isAuthenticated, getSessionInfo, dispatch, resetTimeout]);

  // Handle window/browser close
  const handleBeforeUnload = useCallback((event) => {
    if (isAuthenticated) {
      // Attempt to logout (may not complete due to browser limitations)
      navigator.sendBeacon('/api/auth/logout', JSON.stringify({}));
      
      // Some browsers show a confirmation dialog
      event.preventDefault();
      event.returnValue = '';
      return '';
    }
  }, [isAuthenticated]);

  // Handle page visibility change (tab switching, minimizing)
  const handleVisibilityChange = useCallback(() => {
    if (document.hidden) {
      // Page is hidden, continue timeout
      return;
    } else {
      // Page is visible again, treat as activity
      handleActivity();
    }
  }, [handleActivity]);

  // Set up event listeners and timers
  useEffect(() => {
    if (!isAuthenticated) {
      // Clear all timeouts when not authenticated
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (warningTimeoutRef.current) clearTimeout(warningTimeoutRef.current);
      if (sessionCheckRef.current) clearInterval(sessionCheckRef.current);
      return;
    }

    // Activity events to monitor
    const events = [
      'mousedown',
      'mousemove',
      'keypress',
      'scroll',
      'touchstart',
      'click'
    ];

    // Add event listeners
    events.forEach(event => {
      document.addEventListener(event, handleActivity, true);
    });

    // Add visibility change listener
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Add beforeunload listener
    window.addEventListener('beforeunload', handleBeforeUnload);

    // Set up periodic session check (every 5 minutes)
    sessionCheckRef.current = setInterval(checkSessionStatus, 5 * 60 * 1000);

    // Initialize timeout
    getSessionInfo().then(() => {
      resetTimeout();
    });

    // Cleanup function
    return () => {
      events.forEach(event => {
        document.removeEventListener(event, handleActivity, true);
      });
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('beforeunload', handleBeforeUnload);
      
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (warningTimeoutRef.current) clearTimeout(warningTimeoutRef.current);
      if (sessionCheckRef.current) clearInterval(sessionCheckRef.current);
    };
  }, [
    isAuthenticated,
    handleActivity,
    handleVisibilityChange,
    handleBeforeUnload,
    checkSessionStatus,
    getSessionInfo,
    resetTimeout
  ]);

  // Public API
  const setWarningCallback = useCallback((callback) => {
    warningCallbackRef.current = callback;
  }, []);

  const getRemainingTime = useCallback(async () => {
    const sessionInfo = await getSessionInfo();
    return sessionInfo ? sessionInfo.remaining_seconds : 0;
  }, [getSessionInfo]);

  const extendSession = useCallback(() => {
    resetTimeout();
  }, [resetTimeout]);

  return {
    setWarningCallback,
    getRemainingTime,
    extendSession,
    timeoutMinutes: timeoutMinutesRef.current
  };
};

export default useAutoLogout;
