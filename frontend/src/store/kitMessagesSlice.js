import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

// Async Thunks
export const sendMessage = createAsyncThunk(
  'kitMessages/sendMessage',
  async ({ kitId, data }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/kits/${kitId}/messages`, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to send message' });
    }
  }
);

export const fetchKitMessages = createAsyncThunk(
  'kitMessages/fetchKitMessages',
  async ({ kitId, filters = {} }, { rejectWithValue }) => {
    try {
      const response = await api.get(`/kits/${kitId}/messages`, { params: filters });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch messages' });
    }
  }
);

export const fetchUserMessages = createAsyncThunk(
  'kitMessages/fetchUserMessages',
  async (filters = {}, { rejectWithValue }) => {
    try {
      const response = await api.get('/messages', { params: filters });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch messages' });
    }
  }
);

export const fetchMessageById = createAsyncThunk(
  'kitMessages/fetchMessageById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await api.get(`/messages/${id}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch message' });
    }
  }
);

export const markMessageAsRead = createAsyncThunk(
  'kitMessages/markAsRead',
  async (id, { rejectWithValue }) => {
    try {
      const response = await api.put(`/messages/${id}/read`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to mark message as read' });
    }
  }
);

export const replyToMessage = createAsyncThunk(
  'kitMessages/replyToMessage',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/messages/${id}/reply`, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to reply to message' });
    }
  }
);

export const fetchUnreadCount = createAsyncThunk(
  'kitMessages/fetchUnreadCount',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/messages/unread-count');
      return response.data.unread_count;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch unread count' });
    }
  }
);

// Slice
const kitMessagesSlice = createSlice({
  name: 'kitMessages',
  initialState: {
    messages: {}, // Changed to object keyed by kitId
    currentMessage: null,
    unreadCount: 0,
    loading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentMessage: (state) => {
      state.currentMessage = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUserMessages.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchUserMessages.fulfilled, (state, action) => {
        state.loading = false;
        // For user messages, store in a special 'all' key
        state.messages.all = action.payload;
      })
      .addCase(fetchUserMessages.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchKitMessages.fulfilled, (state, action) => {
        // Extract kitId from the action meta or use a default approach
        // The payload should include kitId or we need to get it from meta
        const kitId = action.meta?.arg?.kitId;
        if (kitId) {
          state.messages[kitId] = action.payload;
        }
      })
      .addCase(fetchMessageById.fulfilled, (state, action) => {
        state.currentMessage = action.payload;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        // Extract kitId from the action meta
        const kitId = action.meta?.arg?.kitId;
        if (kitId) {
          if (!state.messages[kitId]) {
            state.messages[kitId] = [];
          }
          state.messages[kitId].unshift(action.payload);
        }
      })
      .addCase(replyToMessage.fulfilled, (state, action) => {
        // Extract kitId from the message or action meta
        const kitId = action.payload.kit_id;
        if (kitId) {
          if (!state.messages[kitId]) {
            state.messages[kitId] = [];
          }
          state.messages[kitId].unshift(action.payload);
        }
      })
      .addCase(markMessageAsRead.fulfilled, (state, action) => {
        // Update message in all relevant kit arrays
        const kitId = action.payload.kit_id;
        if (kitId && state.messages[kitId]) {
          const index = state.messages[kitId].findIndex(m => m.id === action.payload.id);
          if (index !== -1) {
            state.messages[kitId][index] = action.payload;
          }
        }
        if (state.currentMessage?.id === action.payload.id) {
          state.currentMessage = action.payload;
        }
        state.unreadCount = Math.max(0, state.unreadCount - 1);
      })
      .addCase(fetchUnreadCount.fulfilled, (state, action) => {
        state.unreadCount = action.payload;
      });
  },
});

export const { clearError, clearCurrentMessage } = kitMessagesSlice.actions;
export default kitMessagesSlice.reducer;

