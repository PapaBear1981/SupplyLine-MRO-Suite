import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async thunks
export const fetchNotifications = createAsyncThunk(
  'cycleCountNotifications/fetchNotifications',
  async ({ unreadOnly = false, limit = 10 } = {}, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/cycle-counts/notifications', {
        params: { unread_only: unreadOnly, limit }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: 'Failed to fetch notifications' });
    }
  }
);

export const markNotificationAsRead = createAsyncThunk(
  'cycleCountNotifications/markAsRead',
  async (id, { rejectWithValue }) => {
    try {
      await axios.post(`/api/cycle-counts/notifications/${id}/read`);
      return { id };
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: 'Failed to mark notification as read' });
    }
  }
);

export const markAllNotificationsAsRead = createAsyncThunk(
  'cycleCountNotifications/markAllAsRead',
  async (_, { rejectWithValue }) => {
    try {
      await axios.post('/api/cycle-counts/notifications/read-all');
      return {};
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: 'Failed to mark all notifications as read' });
    }
  }
);

// Slice
const cycleCountNotificationsSlice = createSlice({
  name: 'cycleCountNotifications',
  initialState: {
    notifications: [],
    unreadCount: 0,
    loading: false,
    error: null
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      // Fetch notifications
      .addCase(fetchNotifications.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchNotifications.fulfilled, (state, action) => {
        state.loading = false;
        state.notifications = action.payload.notifications;
        state.unreadCount = action.payload.unread_count;
      })
      .addCase(fetchNotifications.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.error || 'Failed to fetch notifications';
      })
      
      // Mark notification as read
      .addCase(markNotificationAsRead.fulfilled, (state, action) => {
        const index = state.notifications.findIndex(n => n.id === action.payload.id);
        if (index !== -1) {
          state.notifications[index].is_read = true;
          state.unreadCount = Math.max(0, state.unreadCount - 1);
        }
      })
      
      // Mark all notifications as read
      .addCase(markAllNotificationsAsRead.fulfilled, (state) => {
        state.notifications.forEach(notification => {
          notification.is_read = true;
        });
        state.unreadCount = 0;
      });
  }
});

export default cycleCountNotificationsSlice.reducer;
