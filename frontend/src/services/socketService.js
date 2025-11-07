/**
 * WebSocket Service for Real-Time Messaging
 * Manages Socket.io connection and event handlers
 */
import { io } from 'socket.io-client';
import store from '../store/store';
import {
  setConnected,
  setDisconnected,
  addMessage,
  updateMessageReadStatus,
  updateUserPresence,
  addReaction,
  removeReaction as removeReactionFromState,
  setTypingIndicator
} from '../store/messagingSlice';

class SocketService {
  constructor() {
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  /**
   * Connect to WebSocket server
   * @param {string} token - JWT authentication token
   */
  connect(token) {
    if (this.socket?.connected) {
      console.log('Socket already connected');
      return;
    }

    const SOCKET_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

    this.socket = io(SOCKET_URL, {
      auth: { token },
      query: { token },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: this.maxReconnectAttempts,
      timeout: 20000
    });

    this.setupEventHandlers();
    console.log('Socket.io connecting...');
  }

  /**
   * Set up all event handlers
   */
  setupEventHandlers() {
    // Connection events
    this.socket.on('connect', () => {
      console.log('Socket connected:', this.socket.id);
      this.reconnectAttempts = 0;
      store.dispatch(setConnected());
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason);
      store.dispatch(setDisconnected());
    });

    this.socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
      this.reconnectAttempts++;

      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached');
        this.disconnect();
      }
    });

    // Kit message events
    this.socket.on('new_kit_message', (message) => {
      console.log('New kit message received:', message);
      store.dispatch(addMessage({ type: 'kit', message }));

      // Show notification
      this.showNotification('New Message', {
        body: `${message.sender_name}: ${message.subject}`,
        icon: '/icon.png'
      });
    });

    this.socket.on('kit_message_sent', (message) => {
      console.log('Kit message sent confirmation:', message);
      store.dispatch(addMessage({ type: 'kit', message }));
    });

    this.socket.on('kit_message_read', (data) => {
      console.log('Message read:', data);
      store.dispatch(updateMessageReadStatus({
        messageId: data.message_id,
        readBy: data.read_by,
        readDate: data.read_date
      }));
    });

    // Channel message events
    this.socket.on('new_channel_message', (message) => {
      console.log('New channel message received:', message);
      store.dispatch(addMessage({ type: 'channel', message }));

      // Show notification
      this.showNotification('New Channel Message', {
        body: `${message.sender_name}: ${message.message.substring(0, 50)}...`,
        icon: '/icon.png'
      });
    });

    // User presence events
    this.socket.on('user_online', (data) => {
      console.log('User came online:', data);
      store.dispatch(updateUserPresence({
        userId: data.user_id,
        isOnline: true,
        timestamp: data.timestamp
      }));
    });

    this.socket.on('user_offline', (data) => {
      console.log('User went offline:', data);
      store.dispatch(updateUserPresence({
        userId: data.user_id,
        isOnline: false,
        timestamp: data.timestamp
      }));
    });

    this.socket.on('status_updated', (data) => {
      console.log('User status updated:', data);
      store.dispatch(updateUserPresence({
        userId: data.user_id,
        statusMessage: data.status_message
      }));
    });

    // Typing indicator events
    this.socket.on('user_typing', (data) => {
      console.log('User typing:', data);
      store.dispatch(setTypingIndicator({
        userId: data.user_id,
        channelId: data.channel_id,
        kitId: data.kit_id,
        isTyping: data.typing
      }));

      // Auto-clear typing indicator after 5 seconds
      if (data.typing) {
        setTimeout(() => {
          store.dispatch(setTypingIndicator({
            userId: data.user_id,
            channelId: data.channel_id,
            kitId: data.kit_id,
            isTyping: false
          }));
        }, 5000);
      }
    });

    // Reaction events
    this.socket.on('reaction_added', (reaction) => {
      console.log('Reaction added:', reaction);
      store.dispatch(addReaction(reaction));
    });

    this.socket.on('reaction_removed', (data) => {
      console.log('Reaction removed:', data);
      store.dispatch(removeReactionFromState(data.reaction_id));
    });

    // Channel events
    this.socket.on('channel_joined', (data) => {
      console.log('Joined channel:', data);
    });

    this.socket.on('user_joined_channel', (data) => {
      console.log('User joined channel:', data);
    });

    this.socket.on('user_left_channel', (data) => {
      console.log('User left channel:', data);
    });

    // Error handling
    this.socket.on('error', (error) => {
      console.error('Socket error:', error);
      alert(error.message || 'WebSocket error occurred');
    });

    // Pong response
    this.socket.on('pong', (data) => {
      // Keep-alive acknowledgment
      console.debug('Pong received:', data);
    });
  }

  /**
   * Show browser notification
   * @param {string} title - Notification title
   * @param {object} options - Notification options
   */
  showNotification(title, options) {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, options);
    }
  }

  /**
   * Request notification permission
   */
  static requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      console.log('Socket disconnected');
    }
  }

  /**
   * Check if socket is connected
   */
  isConnected() {
    return this.socket?.connected || false;
  }

  // === Emit Methods ===

  /**
   * Send a kit message
   */
  sendKitMessage(data) {
    if (!this.socket?.connected) {
      console.error('Socket not connected');
      return;
    }
    this.socket.emit('send_kit_message', data);
  }

  /**
   * Mark a kit message as read
   */
  markKitMessageRead(messageId) {
    if (!this.socket?.connected) return;
    this.socket.emit('mark_kit_message_read', { message_id: messageId });
  }

  /**
   * Send a channel message
   */
  sendChannelMessage(data) {
    if (!this.socket?.connected) {
      console.error('Socket not connected');
      return;
    }
    this.socket.emit('send_channel_message', data);
  }

  /**
   * Join a channel
   */
  joinChannel(channelId) {
    if (!this.socket?.connected) return;
    this.socket.emit('join_channel', { channel_id: channelId });
  }

  /**
   * Leave a channel
   */
  leaveChannel(channelId) {
    if (!this.socket?.connected) return;
    this.socket.emit('leave_channel', { channel_id: channelId });
  }

  /**
   * Start typing indicator
   */
  startTyping(context) {
    if (!this.socket?.connected) return;
    this.socket.emit('typing_start', context);
  }

  /**
   * Stop typing indicator
   */
  stopTyping(context) {
    if (!this.socket?.connected) return;
    this.socket.emit('typing_stop', context);
  }

  /**
   * Add a reaction to a message
   */
  addReaction(data) {
    if (!this.socket?.connected) return;
    this.socket.emit('add_reaction', data);
  }

  /**
   * Remove a reaction from a message
   */
  removeReaction(reactionId) {
    if (!this.socket?.connected) return;
    this.socket.emit('remove_reaction', { reaction_id: reactionId });
  }

  /**
   * Update user status message
   */
  updateStatus(statusMessage) {
    if (!this.socket?.connected) return;
    this.socket.emit('update_status', { status_message: statusMessage });
  }

  /**
   * Send keep-alive ping
   */
  ping() {
    if (!this.socket?.connected) return;
    this.socket.emit('ping', {});
  }

  /**
   * Start periodic ping to keep connection alive
   */
  startPing(intervalMs = 30000) {
    this.stopPing();
    this.pingInterval = setInterval(() => {
      this.ping();
    }, intervalMs);
  }

  /**
   * Stop periodic ping
   */
  stopPing() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }
}

// Create singleton instance
const socketService = new SocketService();

export default socketService;
