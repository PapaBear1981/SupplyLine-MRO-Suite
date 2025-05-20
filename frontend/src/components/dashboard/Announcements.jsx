import { useState, useEffect } from 'react';
import { Card, ListGroup, Badge, Alert, Button, Spinner } from 'react-bootstrap';
import api from '../../services/api';

// Mock data for announcements - in a real app, this would come from the API
const mockAnnouncements = [
  {
    id: 1,
    title: 'System Maintenance',
    content: 'The system will be down for maintenance on Saturday from 2-4 AM.',
    priority: 'high',
    date: '2025-05-18T14:00:00Z',
    read: false
  },
  {
    id: 2,
    title: 'New Chemical Safety Procedures',
    content: 'Updated chemical handling procedures are now in effect. Please review the new safety guidelines.',
    priority: 'medium',
    date: '2025-05-15T09:30:00Z',
    read: false
  },
  {
    id: 3,
    title: 'Holiday Schedule',
    content: 'The facility will be closed on May 27th for Memorial Day.',
    priority: 'low',
    date: '2025-05-10T11:15:00Z',
    read: true
  }
];

const Announcements = () => {
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnnouncements = async () => {
      try {
        setLoading(true);
        // In a real app, this would be an API call
        // const response = await api.get('/announcements');
        // setAnnouncements(response.data);
        
        // Using mock data for now
        setTimeout(() => {
          setAnnouncements(mockAnnouncements);
          setLoading(false);
        }, 500);
      } catch (err) {
        console.error('Error fetching announcements:', err);
        setError('Failed to load announcements');
        setLoading(false);
      }
    };

    fetchAnnouncements();
  }, []);

  // Function to format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  // Function to mark announcement as read
  const markAsRead = (id) => {
    setAnnouncements(announcements.map(announcement => 
      announcement.id === id ? { ...announcement, read: true } : announcement
    ));
    
    // In a real app, this would be an API call
    // api.post(`/announcements/${id}/read`);
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
      <Card className="shadow-sm mb-4">
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
      <Card className="shadow-sm mb-4">
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
  const sortedAnnouncements = [...announcements].sort((a, b) => {
    // First sort by read status (unread first)
    if (a.read !== b.read) return a.read ? 1 : -1;
    
    // Then sort by priority
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    }
    
    // Finally sort by date (newest first)
    return new Date(b.date) - new Date(a.date);
  });

  return (
    <Card className="shadow-sm mb-4">
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
                    <small className="text-muted">{formatDate(announcement.date)}</small>
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
