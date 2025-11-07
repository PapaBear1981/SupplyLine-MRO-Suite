/**
 * Chat Message Bubble Component
 * Displays a single message with sender info, reactions, and attachments
 */
import React from 'react';
import { Card, Badge, Button } from 'react-bootstrap';
import { useSelector } from 'react-redux';
import { selectUserPresence, selectMessageReactions } from '../../store/messagingSlice';
import './ChatMessage.css';

const ChatMessage = ({ message, isOwnMessage, onReact, onReply }) => {
  const userPresence = useSelector(state => selectUserPresence(state, message.sender_id));
  const reactions = useSelector(state => selectMessageReactions(state, message.id));

  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const reactionCounts = reactions.reduce((acc, reaction) => {
    acc[reaction.reaction_type] = (acc[reaction.reaction_type] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className={`chat-message ${isOwnMessage ? 'own-message' : 'other-message'}`}>
      <div className="message-container">
        {!isOwnMessage && (
          <div className="message-sender">
            <span className="sender-name">{message.sender_name}</span>
            {userPresence?.isOnline && (
              <span className="online-indicator" title="Online">●</span>
            )}
          </div>
        )}

        <Card className={`message-bubble ${isOwnMessage ? 'bg-primary text-white' : ''}`}>
          <Card.Body>
            {message.subject && (
              <div className="message-subject fw-bold mb-2">{message.subject}</div>
            )}
            <div className="message-text">{message.message}</div>

            {message.attachments && message.attachments.length > 0 && (
              <div className="message-attachments mt-2">
                {message.attachments.map((attachment, idx) => (
                  <Badge key={idx} bg="secondary" className="me-1">
                    📎 {attachment.original_filename}
                  </Badge>
                ))}
              </div>
            )}

            <div className="message-time text-muted small mt-1">
              {formatTime(message.sent_date)}
              {message.is_read && isOwnMessage && (
                <span className="ms-1">✓✓</span>
              )}
            </div>
          </Card.Body>
        </Card>

        {reactions.length > 0 && (
          <div className="message-reactions">
            {Object.entries(reactionCounts).map(([emoji, count]) => (
              <Badge key={emoji} bg="light" text="dark" className="reaction-badge">
                {emoji} {count}
              </Badge>
            ))}
          </div>
        )}

        <div className="message-actions">
          <Button
            size="sm"
            variant="link"
            onClick={() => onReact?.(message.id)}
            className="text-muted"
          >
            😊
          </Button>
          <Button
            size="sm"
            variant="link"
            onClick={() => onReply?.(message)}
            className="text-muted"
          >
            Reply
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
