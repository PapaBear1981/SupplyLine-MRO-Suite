/**
 * Redux Slice for Enhanced Messaging
 * Manages messages, channels, presence, and real-time updates
 */
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

// Async thunks for API calls

export const fetchChannels = createAsyncThunk(
  'messaging/fetchChannels',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/api/channels');
      return response.data.channels;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch channels');
    }
  }
);

export const fetchChannelMessages = createAsyncThunk(
  'messaging/fetchChannelMessages',
  async ({ channelId, limit = 50, offset = 0 }, { rejectWithValue }) => {
    try {
      const response = await api.get(`/api/channels/${channelId}/messages`, {
        params: { limit, offset }
      });
      return { channelId, messages: response.data.messages };
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch messages');
    }
  }
);

export const createChannel = createAsyncThunk(
  'messaging/createChannel',
  async (channelData, { rejectWithValue }) => {
    try {
      const response = await api.post('/api/channels', channelData);
      return response.data.channel;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to create channel');
    }
  }
);

export const searchMessages = createAsyncThunk(
  'messaging/searchMessages',
  async (searchParams, { rejectWithValue }) => {
    try {
      const response = await api.get('/api/messages/search', { params: searchParams });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to search messages');
    }
  }
);

export const fetchMessageStats = createAsyncThunk(
  'messaging/fetchMessageStats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/api/messages/search/stats');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch stats');
    }
  }
);

export const uploadAttachment = createAsyncThunk(
  'messaging/uploadAttachment',
  async ({ file, messageType, messageId }, { rejectWithValue }) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('message_type', messageType);
      if (messageId) {
        formData.append('message_id', messageId);
      }

      // Don't set Content-Type header manually - axios will automatically
      // set it with the correct boundary when it detects FormData
      const response = await api.post('/api/attachments/upload', formData);
      return response.data.attachment;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to upload file');
    }
  }
);

const initialState = {
  // WebSocket connection
  connected: false,

  // Channels
  channels: [],
  activeChannelId: null,
  channelsLoading: false,
  channelsError: null,

  // Messages
  channelMessages: {}, // { channelId: [messages] }
  kitMessages: [],
  messagesLoading: false,
  messagesError: null,

  // Search
  searchResults: [],
  searchQuery: '',
  searchLoading: false,

  // User presence
  userPresence: {}, // { userId: { isOnline, lastSeen, statusMessage } }

  // Typing indicators
  typingIndicators: {}, // { channelId: [userIds], kitId: [userIds] }

  // Reactions
  reactions: {}, // { messageId: [reactions] }

  // Attachments
  attachments: {},
  uploadProgress: {},

  // Stats
  stats: {
    kit_messages: { received: 0, unread: 0, sent: 0, total: 0 },
    channel_messages: { total: 0, unread: 0 },
    totals: { all_messages: 0, unread: 0 }
  },

  // UI state
  showEmojiPicker: false,
  activeMessageId: null,
  unreadCounts: {} // { channelId: count }
};

const messagingSlice = createSlice({
  name: 'messaging',
  initialState,
  reducers: {
    // WebSocket connection
    setConnected: (state) => {
      state.connected = true;
    },
    setDisconnected: (state) => {
      state.connected = false;
    },

    // Active channel
    setActiveChannel: (state, action) => {
      state.activeChannelId = action.payload;
    },

    // Add message
    addMessage: (state, action) => {
      const { type, message } = action.payload;

      if (type === 'channel') {
        const channelId = message.channel_id;
        if (!state.channelMessages[channelId]) {
          state.channelMessages[channelId] = [];
        }

        // Avoid duplicates
        const exists = state.channelMessages[channelId].some(m => m.id === message.id);
        if (!exists) {
          state.channelMessages[channelId].push(message);

          // Update unread count if not active channel
          if (state.activeChannelId !== channelId) {
            state.unreadCounts[channelId] = (state.unreadCounts[channelId] || 0) + 1;
          }
        }
      } else if (type === 'kit') {
        const exists = state.kitMessages.some(m => m.id === message.id);
        if (!exists) {
          state.kitMessages.push(message);
        }
      }
    },

    // Update message read status
    updateMessageReadStatus: (state, action) => {
      const { messageId, readDate } = action.payload;

      // Update in kit messages
      const kitMsg = state.kitMessages.find(m => m.id === messageId);
      if (kitMsg) {
        kitMsg.is_read = true;
        kitMsg.read_date = readDate;
      }
    },

    // Clear unread count for channel
    clearUnreadCount: (state, action) => {
      const channelId = action.payload;
      state.unreadCounts[channelId] = 0;
    },

    // User presence
    updateUserPresence: (state, action) => {
      const { userId, isOnline, timestamp, statusMessage } = action.payload;

      if (!state.userPresence[userId]) {
        state.userPresence[userId] = {};
      }

      if (isOnline !== undefined) {
        state.userPresence[userId].isOnline = isOnline;
      }
      if (timestamp) {
        state.userPresence[userId].lastSeen = timestamp;
      }
      if (statusMessage !== undefined) {
        state.userPresence[userId].statusMessage = statusMessage;
      }
    },

    // Typing indicators
    setTypingIndicator: (state, action) => {
      const { userId, channelId, kitId, isTyping } = action.payload;
      const key = channelId ? `channel_${channelId}` : `kit_${kitId}`;

      if (!state.typingIndicators[key]) {
        state.typingIndicators[key] = [];
      }

      if (isTyping) {
        if (!state.typingIndicators[key].includes(userId)) {
          state.typingIndicators[key].push(userId);
        }
      } else {
        state.typingIndicators[key] = state.typingIndicators[key].filter(id => id !== userId);
      }
    },

    // Reactions
    addReaction: (state, action) => {
      const reaction = action.payload;
      const messageId = reaction.kit_message_id || reaction.channel_message_id;

      if (!state.reactions[messageId]) {
        state.reactions[messageId] = [];
      }

      const exists = state.reactions[messageId].some(r => r.id === reaction.id);
      if (!exists) {
        state.reactions[messageId].push(reaction);
      }
    },

    removeReaction: (state, action) => {
      const reactionId = action.payload;

      // Find and remove reaction from all messages
      Object.keys(state.reactions).forEach(messageId => {
        state.reactions[messageId] = state.reactions[messageId].filter(
          r => r.id !== reactionId
        );
      });
    },

    // UI state
    toggleEmojiPicker: (state, action) => {
      state.showEmojiPicker = action.payload !== undefined
        ? action.payload
        : !state.showEmojiPicker;
      state.activeMessageId = action.payload?.messageId || null;
    },

    // Clear messages
    clearChannelMessages: (state, action) => {
      const channelId = action.payload;
      delete state.channelMessages[channelId];
    },

    clearAllMessages: (state) => {
      state.channelMessages = {};
      state.kitMessages = [];
      state.searchResults = [];
    },

    // Upload progress
    setUploadProgress: (state, action) => {
      const { fileId, progress } = action.payload;
      state.uploadProgress[fileId] = progress;
    },

    clearUploadProgress: (state, action) => {
      const fileId = action.payload;
      delete state.uploadProgress[fileId];
    }
  },

  extraReducers: (builder) => {
    // Fetch channels
    builder.addCase(fetchChannels.pending, (state) => {
      state.channelsLoading = true;
      state.channelsError = null;
    });
    builder.addCase(fetchChannels.fulfilled, (state, action) => {
      state.channelsLoading = false;
      state.channels = action.payload;
    });
    builder.addCase(fetchChannels.rejected, (state, action) => {
      state.channelsLoading = false;
      state.channelsError = action.payload;
    });

    // Fetch channel messages
    builder.addCase(fetchChannelMessages.pending, (state) => {
      state.messagesLoading = true;
      state.messagesError = null;
    });
    builder.addCase(fetchChannelMessages.fulfilled, (state, action) => {
      state.messagesLoading = false;
      const { channelId, messages } = action.payload;
      state.channelMessages[channelId] = messages;
    });
    builder.addCase(fetchChannelMessages.rejected, (state, action) => {
      state.messagesLoading = false;
      state.messagesError = action.payload;
    });

    // Create channel
    builder.addCase(createChannel.fulfilled, (state, action) => {
      state.channels.push(action.payload);
    });

    // Search messages
    builder.addCase(searchMessages.pending, (state) => {
      state.searchLoading = true;
    });
    builder.addCase(searchMessages.fulfilled, (state, action) => {
      state.searchLoading = false;
      state.searchResults = action.payload.results;
      state.searchQuery = action.payload.query;
    });
    builder.addCase(searchMessages.rejected, (state) => {
      state.searchLoading = false;
    });

    // Fetch stats
    builder.addCase(fetchMessageStats.fulfilled, (state, action) => {
      state.stats = action.payload;
    });

    // Upload attachment
    builder.addCase(uploadAttachment.fulfilled, (state, action) => {
      const attachment = action.payload;
      const messageId = attachment.kit_message_id || attachment.channel_message_id;

      if (!state.attachments[messageId]) {
        state.attachments[messageId] = [];
      }
      state.attachments[messageId].push(attachment);
    });
  }
});

export const {
  setConnected,
  setDisconnected,
  setActiveChannel,
  addMessage,
  updateMessageReadStatus,
  clearUnreadCount,
  updateUserPresence,
  setTypingIndicator,
  addReaction,
  removeReaction,
  toggleEmojiPicker,
  clearChannelMessages,
  clearAllMessages,
  setUploadProgress,
  clearUploadProgress
} = messagingSlice.actions;

// Selectors
export const selectConnected = (state) => state.messaging.connected;
export const selectChannels = (state) => state.messaging.channels;
export const selectActiveChannelId = (state) => state.messaging.activeChannelId;
export const selectActiveChannel = (state) => {
  const channelId = state.messaging.activeChannelId;
  return state.messaging.channels.find(c => c.id === channelId);
};
export const selectChannelMessages = (state, channelId) =>
  state.messaging.channelMessages[channelId] || [];
export const selectKitMessages = (state) => state.messaging.kitMessages;
export const selectUserPresence = (state, userId) =>
  state.messaging.userPresence[userId] || { isOnline: false };
export const selectTypingUsers = (state, channelId, kitId) => {
  const key = channelId ? `channel_${channelId}` : `kit_${kitId}`;
  return state.messaging.typingIndicators[key] || [];
};
export const selectMessageReactions = (state, messageId) =>
  state.messaging.reactions[messageId] || [];
export const selectUnreadCount = (state, channelId) =>
  state.messaging.unreadCounts[channelId] || 0;
export const selectTotalUnread = (state) =>
  state.messaging.stats.totals.unread;
export const selectMessageStats = (state) => state.messaging.stats;

export default messagingSlice.reducer;
