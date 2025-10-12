import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, ListGroup, Badge, Button, Form, Modal, Alert, Row, Col } from 'react-bootstrap';
import { FaEnvelope, FaEnvelopeOpen, FaReply, FaPaperPlane, FaInbox, FaPaperclip } from 'react-icons/fa';
import { 
  fetchKitMessages, 
  sendMessage, 
  markMessageAsRead, 
  replyToMessage 
} from '../../store/kitMessagesSlice';

const KitMessaging = ({ kitId }) => {
  const dispatch = useDispatch();
  const { messages, loading, error } = useSelector((state) => state.kitMessages);
  const { user } = useSelector((state) => state.auth);
  
  const [showComposeModal, setShowComposeModal] = useState(false);
  const [showReplyModal, setShowReplyModal] = useState(false);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [view, setView] = useState('inbox'); // inbox or sent
  
  const [composeData, setComposeData] = useState({
    subject: '',
    message: '',
    recipient_id: ''
  });

  const [replyData, setReplyData] = useState({
    message: ''
  });

  useEffect(() => {
    if (kitId) {
      dispatch(fetchKitMessages({ kitId }));
    }
  }, [kitId, dispatch]);

  const kitMessages = messages[kitId] || [];

  const handleComposeChange = (e) => {
    const { name, value } = e.target;
    setComposeData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleReplyChange = (e) => {
    setReplyData({ message: e.target.value });
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    
    dispatch(sendMessage({
      kitId,
      data: {
        subject: composeData.subject,
        message: composeData.message,
        recipient_id: composeData.recipient_id || null
      }
    }))
      .unwrap()
      .then(() => {
        setShowComposeModal(false);
        setComposeData({ subject: '', message: '', recipient_id: '' });
        dispatch(fetchKitMessages({ kitId }));
      })
      .catch((err) => {
        console.error('Failed to send message:', err);
      });
  };

  const handleSendReply = (e) => {
    e.preventDefault();
    
    dispatch(replyToMessage({
      messageId: selectedMessage.id,
      data: { message: replyData.message }
    }))
      .unwrap()
      .then(() => {
        setShowReplyModal(false);
        setReplyData({ message: '' });
        setSelectedMessage(null);
        dispatch(fetchKitMessages({ kitId }));
      })
      .catch((err) => {
        console.error('Failed to send reply:', err);
      });
  };

  const handleMessageClick = (message) => {
    setSelectedMessage(message);
    if (!message.is_read && message.recipient_id === user?.id) {
      dispatch(markMessageAsRead({ messageId: message.id }));
    }
  };

  const handleReply = (message) => {
    setSelectedMessage(message);
    setShowReplyModal(true);
  };

  const getFilteredMessages = () => {
    if (view === 'inbox') {
      return kitMessages.filter(m => m.recipient_id === user?.id || !m.recipient_id);
    } else {
      return kitMessages.filter(m => m.sender_id === user?.id);
    }
  };

  const filteredMessages = getFilteredMessages();

  return (
    <Card>
      <Card.Header>
        <Row className="align-items-center">
          <Col>
            <h5 className="mb-0">
              <FaEnvelope className="me-2" />
              Messages
            </h5>
          </Col>
          <Col xs="auto">
            <Button 
              variant="primary" 
              size="sm"
              onClick={() => setShowComposeModal(true)}
            >
              <FaPaperPlane className="me-1" />
              New Message
            </Button>
          </Col>
        </Row>
      </Card.Header>

      <Card.Body>
        {/* View Toggle */}
        <div className="mb-3">
          <Button
            variant={view === 'inbox' ? 'primary' : 'outline-primary'}
            size="sm"
            className="me-2"
            onClick={() => setView('inbox')}
          >
            <FaInbox className="me-1" />
            Inbox
          </Button>
          <Button
            variant={view === 'sent' ? 'primary' : 'outline-primary'}
            size="sm"
            onClick={() => setView('sent')}
          >
            <FaPaperPlane className="me-1" />
            Sent
          </Button>
        </div>

        {error && (
          <Alert variant="danger">
            {error.message || 'Failed to load messages'}
          </Alert>
        )}

        {/* Messages List */}
        {filteredMessages.length === 0 ? (
          <div className="text-center py-5 text-muted">
            <FaEnvelope size={48} className="mb-3" />
            <p>No messages</p>
          </div>
        ) : (
          <ListGroup>
            {filteredMessages.map((message) => (
              <ListGroup.Item
                key={message.id}
                action
                onClick={() => handleMessageClick(message)}
                className={!message.is_read && view === 'inbox' ? 'fw-bold' : ''}
              >
                <div className="d-flex justify-content-between align-items-start">
                  <div className="flex-grow-1">
                    <div className="d-flex align-items-center mb-1">
                      {!message.is_read && view === 'inbox' && (
                        <FaEnvelope className="me-2 text-primary" />
                      )}
                      {message.is_read && view === 'inbox' && (
                        <FaEnvelopeOpen className="me-2 text-muted" />
                      )}
                      <strong>{message.subject}</strong>
                      {message.parent_message_id && (
                        <Badge bg="secondary" className="ms-2">Reply</Badge>
                      )}
                    </div>
                    <div className="small text-muted">
                      {view === 'inbox' ? (
                        <>From: {message.sender_name || 'Unknown'}</>
                      ) : (
                        <>To: {message.recipient_name || 'Broadcast'}</>
                      )}
                      {' • '}
                      {new Date(message.sent_date).toLocaleString()}
                    </div>
                    <div className="mt-1 text-truncate">
                      {message.message}
                    </div>
                  </div>
                  {view === 'inbox' && (
                    <Button
                      variant="outline-primary"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleReply(message);
                      }}
                    >
                      <FaReply className="me-1" />
                      Reply
                    </Button>
                  )}
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}
      </Card.Body>

      {/* Compose Modal */}
      <Modal show={showComposeModal} onHide={() => setShowComposeModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>New Message</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSendMessage}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Subject *</Form.Label>
              <Form.Control
                type="text"
                name="subject"
                value={composeData.subject}
                onChange={handleComposeChange}
                required
                placeholder="Enter subject"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Recipient (Optional - leave blank for broadcast)</Form.Label>
              <Form.Control
                type="number"
                name="recipient_id"
                value={composeData.recipient_id}
                onChange={handleComposeChange}
                placeholder="User ID (optional)"
              />
              <Form.Text className="text-muted">
                Leave blank to send to all kit users
              </Form.Text>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Message *</Form.Label>
              <Form.Control
                as="textarea"
                rows={5}
                name="message"
                value={composeData.message}
                onChange={handleComposeChange}
                required
                placeholder="Type your message..."
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowComposeModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={loading}>
              <FaPaperPlane className="me-1" />
              {loading ? 'Sending...' : 'Send Message'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Reply Modal */}
      <Modal show={showReplyModal} onHide={() => setShowReplyModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Reply to: {selectedMessage?.subject}</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSendReply}>
          <Modal.Body>
            {selectedMessage && (
              <Alert variant="light" className="mb-3">
                <strong>Original Message:</strong>
                <div className="mt-2">{selectedMessage.message}</div>
                <div className="small text-muted mt-2">
                  From: {selectedMessage.sender_name} • {new Date(selectedMessage.sent_date).toLocaleString()}
                </div>
              </Alert>
            )}

            <Form.Group className="mb-3">
              <Form.Label>Your Reply *</Form.Label>
              <Form.Control
                as="textarea"
                rows={5}
                value={replyData.message}
                onChange={handleReplyChange}
                required
                placeholder="Type your reply..."
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowReplyModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={loading}>
              <FaReply className="me-1" />
              {loading ? 'Sending...' : 'Send Reply'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Card>
  );
};

export default KitMessaging;

