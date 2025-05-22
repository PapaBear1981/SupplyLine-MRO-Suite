import React, { useState, useEffect } from 'react';
import { Badge, Button, Card, ListGroup, Spinner, Alert, Dropdown } from 'react-bootstrap';
import { BellFill, CheckCircleFill } from 'react-bootstrap-icons';
import axios from 'axios';
import { formatDistanceToNow } from 'date-fns';

const CycleCountNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);

  // Fetch notifications
  const fetchNotifications = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('/api/cycle-counts/notifications');
      setNotifications(response.data.notifications);
      setUnreadCount(response.data.unread_count);
    } catch (err) {
      setError('Failed to load notifications');
      console.error('Error fetching notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  // Mark a notification as read
  const markAsRead = async (id) => {
    try {
      await axios.post(`/api/cycle-counts/notifications/${id}/read`);
      
      // Update local state
      setNotifications(notifications.map(notification => 
        notification.id === id ? { ...notification, is_read: true } : notification
      ));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Error marking notification as read:', err);
    }
  };

  // Mark all notifications as read
  const markAllAsRead = async () => {
    try {
      await axios.post('/api/cycle-counts/notifications/read-all');
      
      // Update local state
      setNotifications(notifications.map(notification => ({ ...notification, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Error marking all notifications as read:', err);
    }
  };

  // Get notification badge color based on type
  const getNotificationBadgeVariant = (type) => {
    switch (type) {
      case 'batch_assigned':
        return 'primary';
      case 'discrepancy_found':
        return 'danger';
      case 'batch_completed':
        return 'success';
      case 'adjustment_approved':
        return 'info';
      default:
        return 'secondary';
    }
  };

  // Get notification icon based on type
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'batch_assigned':
        return <i className="bi bi-clipboard-check"></i>;
      case 'discrepancy_found':
        return <i className="bi bi-exclamation-triangle"></i>;
      case 'batch_completed':
        return <i className="bi bi-check-circle"></i>;
      case 'adjustment_approved':
        return <i className="bi bi-pencil-square"></i>;
      default:
        return <i className="bi bi-bell"></i>;
    }
  };

  // Format notification time
  const formatNotificationTime = (dateString) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch (err) {
      return 'Unknown time';
    }
  };

  // Load notifications on component mount
  useEffect(() => {
    fetchNotifications();
    
    // Poll for new notifications every minute
    const interval = setInterval(fetchNotifications, 60000);
    
    // Clean up interval on unmount
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="notification-dropdown">
      <Dropdown show={showDropdown} onToggle={(isOpen) => setShowDropdown(isOpen)}>
        <Dropdown.Toggle variant="link" id="notification-dropdown" className="position-relative p-0 text-decoration-none">
          <BellFill size={20} className="text-secondary" />
          {unreadCount > 0 && (
            <Badge 
              pill 
              bg="danger" 
              className="position-absolute top-0 start-100 translate-middle"
              style={{ fontSize: '0.6rem' }}
            >
              {unreadCount}
            </Badge>
          )}
        </Dropdown.Toggle>

        <Dropdown.Menu align="end" className="notification-menu shadow-lg" style={{ width: '350px', maxHeight: '500px', overflow: 'auto' }}>
          <div className="d-flex justify-content-between align-items-center px-3 py-2 border-bottom">
            <h6 className="mb-0">Notifications</h6>
            {unreadCount > 0 && (
              <Button 
                variant="link" 
                size="sm" 
                className="text-decoration-none p-0"
                onClick={markAllAsRead}
              >
                Mark all as read
              </Button>
            )}
          </div>

          {loading && (
            <div className="text-center p-3">
              <Spinner animation="border" size="sm" />
            </div>
          )}

          {error && (
            <Alert variant="danger" className="m-2 p-2">
              {error}
            </Alert>
          )}

          {!loading && notifications.length === 0 && (
            <div className="text-center p-3 text-muted">
              No notifications
            </div>
          )}

          <ListGroup variant="flush">
            {notifications.map(notification => (
              <ListGroup.Item 
                key={notification.id}
                className={`border-bottom ${!notification.is_read ? 'bg-light' : ''}`}
                style={{ cursor: 'pointer' }}
                onClick={() => !notification.is_read && markAsRead(notification.id)}
              >
                <div className="d-flex">
                  <div className="me-2">
                    <Badge bg={getNotificationBadgeVariant(notification.notification_type)} className="p-2">
                      {getNotificationIcon(notification.notification_type)}
                    </Badge>
                  </div>
                  <div className="flex-grow-1">
                    <div className="d-flex justify-content-between">
                      <small className="text-muted">
                        {formatNotificationTime(notification.created_at)}
                      </small>
                      {!notification.is_read && (
                        <Badge pill bg="primary" className="ms-2">New</Badge>
                      )}
                    </div>
                    <p className="mb-0">{notification.message}</p>
                  </div>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        </Dropdown.Menu>
      </Dropdown>
    </div>
  );
};

export default CycleCountNotifications;
