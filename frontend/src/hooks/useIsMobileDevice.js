import { useEffect, useState } from 'react';

const isTouchUserAgent = () => {
  if (typeof navigator === 'undefined') return false;
  const ua = navigator.userAgent || navigator.vendor || window.opera || '';
  return /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(ua);
};

const useIsMobileDevice = (breakpoint = 900) => {
  const getIsMobile = () => {
    if (typeof window === 'undefined') return false;
    const widthMatch = window.matchMedia(`(max-width: ${breakpoint}px)`).matches;
    return isTouchUserAgent() || widthMatch;
  };

  const [isMobile, setIsMobile] = useState(getIsMobile);

  useEffect(() => {
    const handleResize = () => {
      const nextIsMobile = getIsMobile();
      setIsMobile((current) => (current === nextIsMobile ? current : nextIsMobile));
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [breakpoint]);

  return isMobile;
};

export default useIsMobileDevice;
