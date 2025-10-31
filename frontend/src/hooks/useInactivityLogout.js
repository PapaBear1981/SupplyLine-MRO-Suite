import { useCallback, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { clearError, forceLogout, logout } from '../store/authSlice';

const ACTIVITY_EVENTS = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll', 'focus'];

const sanitizeMinutes = (value, fallback = 30) => {
  const parsed = parseInt(value, 10);
  if (Number.isNaN(parsed) || parsed <= 0) {
    return fallback;
  }
  return parsed;
};

const useInactivityLogout = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { isAuthenticated } = useSelector((state) => state.auth);
  const { sessionTimeoutMinutes } = useSelector((state) => state.security);

  const timerRef = useRef(null);
  const hasTimedOutRef = useRef(false);

  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const handleTimeout = useCallback(() => {
    if (!isAuthenticated || hasTimedOutRef.current) {
      return;
    }

    hasTimedOutRef.current = true;
    clearTimer();

    const minutes = sanitizeMinutes(sessionTimeoutMinutes);

    dispatch(forceLogout());
    dispatch(logout())
      .unwrap()
      .catch(() => {
        dispatch(clearError());
      });

    navigate('/login', {
      replace: true,
      state: {
        sessionTimeoutMessage: `Your session ended after ${minutes} minute${minutes === 1 ? '' : 's'} of inactivity. Please sign in again.`,
      },
    });
  }, [clearTimer, dispatch, isAuthenticated, navigate, sessionTimeoutMinutes]);

  const resetTimer = useCallback(() => {
    if (!isAuthenticated) {
      clearTimer();
      return;
    }

    clearTimer();
    hasTimedOutRef.current = false;

    const minutes = sanitizeMinutes(sessionTimeoutMinutes);
    timerRef.current = setTimeout(handleTimeout, minutes * 60 * 1000);
  }, [clearTimer, handleTimeout, isAuthenticated, sessionTimeoutMinutes]);

  useEffect(() => {
    if (!isAuthenticated) {
      clearTimer();
      hasTimedOutRef.current = false;
      return undefined;
    }

    resetTimer();

    const handleActivity = () => {
      if (!isAuthenticated) {
        return;
      }
      resetTimer();
    };

    ACTIVITY_EVENTS.forEach((eventName) => {
      window.addEventListener(eventName, handleActivity, true);
    });

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        handleActivity();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      ACTIVITY_EVENTS.forEach((eventName) => {
        window.removeEventListener(eventName, handleActivity, true);
      });
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      clearTimer();
    };
  }, [clearTimer, isAuthenticated, resetTimer]);

  useEffect(() => {
    if (isAuthenticated) {
      resetTimer();
    } else {
      clearTimer();
    }
  }, [clearTimer, isAuthenticated, resetTimer, sessionTimeoutMinutes]);
};

export default useInactivityLogout;
