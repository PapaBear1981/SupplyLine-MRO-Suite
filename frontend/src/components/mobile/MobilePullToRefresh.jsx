import { useState, useRef, useEffect } from 'react';
import { Spinner } from 'react-bootstrap';

const MobilePullToRefresh = ({ children, onRefresh, refreshing = false }) => {
  const [pullDistance, setPullDistance] = useState(0);
  const [isPulling, setIsPulling] = useState(false);
  const [startY, setStartY] = useState(0);
  const containerRef = useRef(null);
  const threshold = 80; // Distance needed to trigger refresh

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let touchStartY = 0;
    let touchCurrentY = 0;

    const handleTouchStart = (e) => {
      if (container.scrollTop === 0) {
        touchStartY = e.touches[0].clientY;
        setStartY(touchStartY);
        // Don't set pulling to true immediately, wait for actual pull motion
      }
    };

    const handleTouchMove = (e) => {
      // Only start pulling if we're at the top and moving down
      if (container.scrollTop > 0) {
        setIsPulling(false);
        setPullDistance(0);
        return;
      }

      touchCurrentY = e.touches[0].clientY;
      const distance = touchCurrentY - touchStartY;

      // Only activate pull-to-refresh for significant downward motion
      if (distance > 10) { // 10px threshold before activating
        setIsPulling(true);
        const pullDistance = Math.max(0, distance * 0.5);

        if (pullDistance > 0) {
          e.preventDefault();
          setPullDistance(Math.min(pullDistance, threshold * 1.5));
        }
      } else if (distance < -10) {
        // If scrolling up, disable pull-to-refresh
        setIsPulling(false);
        setPullDistance(0);
      }
    };

    const handleTouchEnd = () => {
      if (isPulling && pullDistance >= threshold && !refreshing) {
        onRefresh();
      }

      setIsPulling(false);
      setPullDistance(0);
    };

    container.addEventListener('touchstart', handleTouchStart, { passive: false });
    container.addEventListener('touchmove', handleTouchMove, { passive: false });
    container.addEventListener('touchend', handleTouchEnd);

    return () => {
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchmove', handleTouchMove);
      container.removeEventListener('touchend', handleTouchEnd);
    };
  }, [isPulling, pullDistance, threshold, onRefresh, refreshing]);

  const getRefreshIndicatorStyle = () => {
    const opacity = Math.min(pullDistance / threshold, 1);
    const scale = Math.min(pullDistance / threshold, 1);

    return {
      transform: `translateY(${Math.min(pullDistance, threshold)}px) scale(${scale})`,
      opacity: opacity
    };
  };

  return (
    <div
      ref={containerRef}
      className="mobile-pull-to-refresh-container"
      style={{
        transform: `translateY(${isPulling ? pullDistance : 0}px)`,
        transition: isPulling ? 'none' : 'transform 0.3s ease-out'
      }}
    >
      {/* Pull to refresh indicator */}
      <div
        className="mobile-pull-to-refresh-indicator"
        style={getRefreshIndicatorStyle()}
      >
        {refreshing ? (
          <div className="d-flex align-items-center">
            <Spinner animation="border" size="sm" className="me-2" />
            <span>Refreshing...</span>
          </div>
        ) : (
          <div className="d-flex align-items-center">
            <i
              className={`bi bi-arrow-down me-2 ${pullDistance >= threshold ? 'text-success' : 'text-muted'}`}
              style={{
                transform: pullDistance >= threshold ? 'rotate(180deg)' : 'rotate(0deg)',
                transition: 'transform 0.2s ease'
              }}
            ></i>
            <span className={pullDistance >= threshold ? 'text-success' : 'text-muted'}>
              {pullDistance >= threshold ? 'Release to refresh' : 'Pull to refresh'}
            </span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="mobile-pull-to-refresh-content">
        {children}
      </div>
    </div>
  );
};

export default MobilePullToRefresh;
