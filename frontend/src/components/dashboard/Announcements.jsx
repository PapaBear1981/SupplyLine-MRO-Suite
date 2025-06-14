import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, ListGroup, Badge, Alert, Button, Spinner } from 'react-bootstrap';
import { fetchAnnouncements, markAnnouncementAsRead } from '../../store/announcementSlice';
import { formatDate } from '../../utils/dateUtils';

const Announcements = () => {
  const dispatch = useDispatch();
  const { announcements, loading, error } = useSelector((state) => ({
    announcements: state.announcements.announcements,
    loading: state.announcements.loading.fetchAnnouncements,
    error: state.announcements.error.fetchAnnouncements
  }));

  useEffect(() => {
    // Fetch announcements with active_only=true to only show active announcements
    dispatch(fetchAnnouncements({
      page: 1,
      limit: 10,
      filters: {
        active_only: true,
        sort_by: 'created_at',
        sort_direction: 'desc'
      }
    }));
  }, [dispatch]);

  // Function to mark announcement as read
  const markAsRead = (id) => {
    dispatch(markAnnouncementAsRead(id));
  };

  // Function to get badge color based on priority
  const getPriorityBadgeVariant = (priority) => {
    switch (priority) {
      case 'high':
        return 'danger';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'secondary';
    }
  };

  if (loading) {
    return (
      <Card className="shadow-sm mb-4" data-testid="announcements">
        <Card.Header className="bg-light">
          <h4 className="mb-0">Announcements</h4>
        </Card.Header>
        <Card.Body className="text-center p-4">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="shadow-sm mb-4" data-testid="announcements">
        <Card.Header className="bg-light">
          <h4 className="mb-0">Announcements</h4>
        </Card.Header>
        <Card.Body>
          <Alert variant="danger">
            <Alert.Heading>Error</Alert.Heading>
            <p>{error}</p>
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  // Filter unread announcements to the top
  const sortedAnnouncements = [...(announcements || [])].sort((a, b) => {
    // First sort by read status (unread first)
    if (a.read !== b.read) return a.read ? 1 : -1;

    // Then sort by priority
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    }

    // Finally sort by date (newest first)
    return new Date(b.created_at) - new Date(a.created_at);
  });

  return (
    <Card className="shadow-sm mb-4" data-testid="announcements">
      <Card.Header className="bg-light d-flex justify-content-between align-items-center">
        <h4 className="mb-0">Announcements</h4>
        <Badge bg="primary" pill>
          {announcements.filter(a => !a.read).length}
        </Badge>
      </Card.Header>
      <Card.Body className="p-0">
        {sortedAnnouncements.length === 0 ? (
          <Alert variant="info" className="m-3">
            No announcements at this time.
          </Alert>
        ) : (
          <ListGroup variant="flush">
            {sortedAnnouncements.map((announcement) => (
              <ListGroup.Item
                key={announcement.id}
                className={`d-flex flex-column ${!announcement.read ? 'bg-light' : ''}`}
              >
                <div className="d-flex justify-content-between align-items-center mb-1">
                  <div className="fw-bold">{announcement.title}</div>
                  <div className="d-flex align-items-center">
                    <Badge
                      bg={getPriorityBadgeVariant(announcement.priority)}
                      className="me-2"
                    >
                      {announcement.priority}
                    </Badge>
                    <small className="text-muted">{formatDate(announcement.created_at)}</small>
                  </div>
                </div>
                <p className="mb-2">{announcement.content}</p>
                {!announcement.read && (
                  <Button
                    variant="outline-secondary"
                    size="sm"
                    className="align-self-end"
                    onClick={() => markAsRead(announcement.id)}
                  >
                    Mark as Read
                  </Button>
                )}
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}
      </Card.Body>
    </Card>
  );
};

export default Announcements;
