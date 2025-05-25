import { useState, useRef, useEffect } from 'react';
import { Button } from 'react-bootstrap';

const MobileSwipeActions = ({ children, actions = [] }) => {
  const [swipeDistance, setSwipeDistance] = useState(0);
  const [isSwipeActive, setIsSwipeActive] = useState(false);
  const [startX, setStartX] = useState(0);
  const containerRef = useRef(null);
  const maxSwipeDistance = 120; // Maximum swipe distance

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let touchStartX = 0;
    let touchCurrentX = 0;
    let isSwiping = false;

    const handleTouchStart = (e) => {
      touchStartX = e.touches[0].clientX;
      setStartX(touchStartX);
      isSwiping = true;
    };

    const handleTouchMove = (e) => {
      if (!isSwiping) return;

      touchCurrentX = e.touches[0].clientX;
      const distance = touchStartX - touchCurrentX;
      
      // Only allow left swipe (positive distance)
      if (distance > 0) {
        e.preventDefault();
        const clampedDistance = Math.min(distance, maxSwipeDistance);
        setSwipeDistance(clampedDistance);
        setIsSwipeActive(true);
      } else {
        setSwipeDistance(0);
        setIsSwipeActive(false);
      }
    };

    const handleTouchEnd = () => {
      isSwiping = false;
      
      // If swipe distance is less than threshold, snap back
      if (swipeDistance < maxSwipeDistance * 0.3) {
        setSwipeDistance(0);
        setIsSwipeActive(false);
      } else {
        // Snap to full open position
        setSwipeDistance(maxSwipeDistance);
        setIsSwipeActive(true);
      }
    };

    // Close swipe actions when clicking outside
    const handleClickOutside = (e) => {
      if (!container.contains(e.target)) {
        setSwipeDistance(0);
        setIsSwipeActive(false);
      }
    };

    container.addEventListener('touchstart', handleTouchStart, { passive: false });
    container.addEventListener('touchmove', handleTouchMove, { passive: false });
    container.addEventListener('touchend', handleTouchEnd);
    document.addEventListener('click', handleClickOutside);

    return () => {
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchmove', handleTouchMove);
      container.removeEventListener('touchend', handleTouchEnd);
      document.removeEventListener('click', handleClickOutside);
    };
  }, [swipeDistance, maxSwipeDistance]);

  const handleActionClick = (action) => {
    action.action();
    // Close swipe actions after action
    setSwipeDistance(0);
    setIsSwipeActive(false);
  };

  return (
    <div 
      ref={containerRef}
      className="mobile-swipe-container"
      style={{ position: 'relative', overflow: 'hidden' }}
    >
      {/* Main content */}
      <div
        className="mobile-swipe-content"
        style={{
          transform: `translateX(-${swipeDistance}px)`,
          transition: isSwipeActive ? 'none' : 'transform 0.3s ease-out'
        }}
      >
        {children}
      </div>

      {/* Swipe actions */}
      <div
        className="mobile-swipe-actions"
        style={{
          position: 'absolute',
          top: 0,
          right: `-${maxSwipeDistance}px`,
          bottom: 0,
          width: `${maxSwipeDistance}px`,
          display: 'flex',
          transform: `translateX(-${swipeDistance}px)`,
          transition: isSwipeActive ? 'none' : 'transform 0.3s ease-out'
        }}
      >
        {actions.map((action, index) => (
          <Button
            key={index}
            variant={action.variant || 'secondary'}
            className="mobile-swipe-action"
            style={{
              flex: 1,
              borderRadius: 0,
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.75rem',
              padding: '0.5rem'
            }}
            onClick={() => handleActionClick(action)}
          >
            <i className={`bi bi-${action.icon} mb-1`}></i>
            <span>{action.label}</span>
          </Button>
        ))}
      </div>
    </div>
  );
};

export default MobileSwipeActions;
