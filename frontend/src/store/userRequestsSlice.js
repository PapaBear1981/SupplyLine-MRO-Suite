import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

export const fetchUserRequests = createAsyncThunk(
  'userRequests/fetchUserRequests',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await api.get('/user-requests', { params });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch requests' });
    }
  }
);

export const fetchUserRequestById = createAsyncThunk(
  'userRequests/fetchUserRequestById',
  async ({ requestId, includeMessages = false }, { rejectWithValue }) => {
    try {
      const response = await api.get(`/user-requests/${requestId}`, {
        params: { include_messages: includeMessages },
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to load request' });
    }
  }
);

export const createUserRequest = createAsyncThunk(
  'userRequests/createUserRequest',
  async (requestData, { rejectWithValue }) => {
    try {
      const response = await api.post('/user-requests', requestData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to create request' });
    }
  }
);

export const updateUserRequest = createAsyncThunk(
  'userRequests/updateUserRequest',
  async ({ requestId, requestData }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/user-requests/${requestId}`, requestData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to update request' });
    }
  }
);

export const cancelUserRequest = createAsyncThunk(
  'userRequests/cancelUserRequest',
  async (requestId, { rejectWithValue }) => {
    try {
      const response = await api.delete(`/user-requests/${requestId}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to cancel request' });
    }
  }
);

export const addRequestItem = createAsyncThunk(
  'userRequests/addRequestItem',
  async ({ requestId, itemData }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/user-requests/${requestId}/items`, itemData);
      return { requestId, item: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to add item' });
    }
  }
);

export const updateRequestItem = createAsyncThunk(
  'userRequests/updateRequestItem',
  async ({ requestId, itemId, itemData }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/user-requests/${requestId}/items/${itemId}`, itemData);
      return { requestId, item: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to update item' });
    }
  }
);

export const removeRequestItem = createAsyncThunk(
  'userRequests/removeRequestItem',
  async ({ requestId, itemId }, { rejectWithValue }) => {
    try {
      await api.delete(`/user-requests/${requestId}/items/${itemId}`);
      return { requestId, itemId };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to remove item' });
    }
  }
);

export const markItemsOrdered = createAsyncThunk(
  'userRequests/markItemsOrdered',
  async ({ requestId, items }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/user-requests/${requestId}/items/mark-ordered`, { items });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to mark items as ordered' });
    }
  }
);

export const markItemsReceived = createAsyncThunk(
  'userRequests/markItemsReceived',
  async ({ requestId, itemIds }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/user-requests/${requestId}/items/mark-received`, { item_ids: itemIds });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to mark items as received' });
    }
  }
);

export const fetchRequestMessages = createAsyncThunk(
  'userRequests/fetchRequestMessages',
  async (requestId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/user-requests/${requestId}/messages`);
      return { requestId, messages: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to load messages' });
    }
  }
);

export const sendRequestMessage = createAsyncThunk(
  'userRequests/sendRequestMessage',
  async ({ requestId, messageData }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/user-requests/${requestId}/messages`, messageData);
      return { requestId, message: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to send message' });
    }
  }
);

export const markMessageRead = createAsyncThunk(
  'userRequests/markMessageRead',
  async (messageId, { rejectWithValue }) => {
    try {
      const response = await api.put(`/user-requests/messages/${messageId}/read`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to mark message as read' });
    }
  }
);

export const fetchRequestAnalytics = createAsyncThunk(
  'userRequests/fetchRequestAnalytics',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/user-requests/analytics');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to load analytics' });
    }
  }
);

const initialState = {
  list: [],
  selectedRequest: null,
  loading: false,
  error: null,
  messages: {}, // Keyed by requestId
  analytics: null,
  analyticsLoading: false,
  messageActionLoading: false,
};

const userRequestsSlice = createSlice({
  name: 'userRequests',
  initialState,
  reducers: {
    clearSelectedRequest: (state) => {
      state.selectedRequest = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch requests
      .addCase(fetchUserRequests.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserRequests.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchUserRequests.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || 'Failed to fetch requests';
      })
      // Fetch single request
      .addCase(fetchUserRequestById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserRequestById.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedRequest = action.payload;
        // Update in list if exists
        const index = state.list.findIndex(r => r.id === action.payload.id);
        if (index !== -1) {
          state.list[index] = action.payload;
        }
      })
      .addCase(fetchUserRequestById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || 'Failed to load request';
      })
      // Create request
      .addCase(createUserRequest.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createUserRequest.fulfilled, (state, action) => {
        state.loading = false;
        state.list.unshift(action.payload);
      })
      .addCase(createUserRequest.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || 'Failed to create request';
      })
      // Update request
      .addCase(updateUserRequest.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateUserRequest.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.list.findIndex(r => r.id === action.payload.id);
        if (index !== -1) {
          state.list[index] = action.payload;
        }
        if (state.selectedRequest?.id === action.payload.id) {
          state.selectedRequest = action.payload;
        }
      })
      .addCase(updateUserRequest.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || 'Failed to update request';
      })
      // Cancel request
      .addCase(cancelUserRequest.fulfilled, (state, action) => {
        const index = state.list.findIndex(r => r.id === action.payload.request.id);
        if (index !== -1) {
          state.list[index] = action.payload.request;
        }
        if (state.selectedRequest?.id === action.payload.request.id) {
          state.selectedRequest = action.payload.request;
        }
      })
      // Mark items ordered
      .addCase(markItemsOrdered.fulfilled, (state, action) => {
        const index = state.list.findIndex(r => r.id === action.payload.id);
        if (index !== -1) {
          state.list[index] = action.payload;
        }
        if (state.selectedRequest?.id === action.payload.id) {
          state.selectedRequest = action.payload;
        }
      })
      // Mark items received
      .addCase(markItemsReceived.fulfilled, (state, action) => {
        const index = state.list.findIndex(r => r.id === action.payload.id);
        if (index !== -1) {
          state.list[index] = action.payload;
        }
        if (state.selectedRequest?.id === action.payload.id) {
          state.selectedRequest = action.payload;
        }
      })
      // Update item
      .addCase(updateRequestItem.fulfilled, (state, action) => {
        const { requestId, item } = action.payload;
        const requestIndex = state.list.findIndex(r => r.id === requestId);
        if (requestIndex !== -1 && state.list[requestIndex].items) {
          const itemIndex = state.list[requestIndex].items.findIndex(i => i.id === item.id);
          if (itemIndex !== -1) {
            state.list[requestIndex].items[itemIndex] = item;
          }
        }
        if (state.selectedRequest?.id === requestId && state.selectedRequest.items) {
          const itemIndex = state.selectedRequest.items.findIndex(i => i.id === item.id);
          if (itemIndex !== -1) {
            state.selectedRequest.items[itemIndex] = item;
          }
        }
      })
      // Messages
      .addCase(fetchRequestMessages.fulfilled, (state, action) => {
        state.messages[action.payload.requestId] = action.payload.messages;
      })
      .addCase(sendRequestMessage.pending, (state) => {
        state.messageActionLoading = true;
      })
      .addCase(sendRequestMessage.fulfilled, (state, action) => {
        state.messageActionLoading = false;
        const { requestId, message } = action.payload;
        if (!state.messages[requestId]) {
          state.messages[requestId] = [];
        }
        state.messages[requestId].unshift(message);
      })
      .addCase(sendRequestMessage.rejected, (state) => {
        state.messageActionLoading = false;
      })
      // Analytics
      .addCase(fetchRequestAnalytics.pending, (state) => {
        state.analyticsLoading = true;
      })
      .addCase(fetchRequestAnalytics.fulfilled, (state, action) => {
        state.analyticsLoading = false;
        state.analytics = action.payload;
      })
      .addCase(fetchRequestAnalytics.rejected, (state) => {
        state.analyticsLoading = false;
      });
  },
});

export const { clearSelectedRequest, clearError } = userRequestsSlice.actions;
export default userRequestsSlice.reducer;
