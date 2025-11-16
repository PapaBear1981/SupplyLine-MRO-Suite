import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

export const fetchOrders = createAsyncThunk(
  'orders/fetchOrders',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await api.get('/orders', { params });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch orders' });
    }
  }
);

export const fetchOrderById = createAsyncThunk(
  'orders/fetchOrderById',
  async ({ orderId, includeMessages = false }, { rejectWithValue }) => {
    try {
      const response = await api.get(`/orders/${orderId}`, {
        params: { include_messages: includeMessages },
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to load order' });
    }
  }
);

export const createOrder = createAsyncThunk(
  'orders/createOrder',
  async (orderData, { rejectWithValue }) => {
    try {
      let payload = orderData;
      let config;

      // When a documentation file is present, send multipart/form-data instead of JSON
      if (orderData?.documentation) {
        const formData = new FormData();

        Object.entries(orderData).forEach(([key, value]) => {
          if (value === undefined || value === null) return;

          if (key === 'documentation') {
            formData.append('documentation', value);
          } else {
            formData.append(key, value);
          }
        });

        payload = formData;
        config = {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        };
      }

      const response = await api.post('/orders', payload, config);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to create order' });
    }
  }
);

export const updateOrder = createAsyncThunk(
  'orders/updateOrder',
  async ({ orderId, orderData }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/orders/${orderId}`, orderData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to update order' });
    }
  }
);

export const fetchOrderAnalytics = createAsyncThunk(
  'orders/fetchOrderAnalytics',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/orders/analytics');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to load analytics' });
    }
  }
);

export const fetchLateOrders = createAsyncThunk(
  'orders/fetchLateOrders',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await api.get('/orders/late-alerts', { params });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to load late order alerts' });
    }
  }
);

export const fetchOrderMessages = createAsyncThunk(
  'orders/fetchOrderMessages',
  async (orderId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/orders/${orderId}/messages`);
      return { orderId, messages: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to load messages' });
    }
  }
);

export const sendOrderMessage = createAsyncThunk(
  'orders/sendOrderMessage',
  async ({ orderId, data }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/orders/${orderId}/messages`, data);
      return { orderId, message: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to send message' });
    }
  }
);

export const replyToOrderMessage = createAsyncThunk(
  'orders/replyToOrderMessage',
  async ({ messageId, data }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/orders/messages/${messageId}/reply`, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to reply to message' });
    }
  }
);

export const markOrderMessageRead = createAsyncThunk(
  'orders/markOrderMessageRead',
  async (messageId, { rejectWithValue }) => {
    try {
      const response = await api.put(`/orders/messages/${messageId}/read`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to mark message as read' });
    }
  }
);

export const markOrderAsDelivered = createAsyncThunk(
  'orders/markOrderAsDelivered',
  async ({ orderId, received_quantity }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/orders/${orderId}/mark-delivered`, {
        received_quantity,
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to mark order as delivered' });
    }
  }
);

export const markOrderAsOrdered = createAsyncThunk(
  'orders/markOrderAsOrdered',
  async ({ orderId, orderData }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/orders/${orderId}/mark-ordered`, orderData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to mark order as ordered' });
    }
  }
);

const initialState = {
  list: [],
  filters: {},
  loading: false,
  analytics: null,
  analyticsLoading: false,
  lateAlerts: [],
  alertsLoading: false,
  messages: {},
  selectedOrder: null,
  messageActionLoading: false,
  error: null,
};

const ordersSlice = createSlice({
  name: 'orders',
  initialState,
  reducers: {
    setOrderFilters: (state, action) => {
      state.filters = action.payload || {};
    },
    clearOrderError: (state) => {
      state.error = null;
    },
    clearSelectedOrder: (state) => {
      state.selectedOrder = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchOrders.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOrders.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchOrders.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(createOrder.fulfilled, (state, action) => {
        state.list = [action.payload, ...state.list];
      })
      .addCase(createOrder.rejected, (state, action) => {
        state.error = action.payload;
      })
      .addCase(updateOrder.fulfilled, (state, action) => {
        const index = state.list.findIndex((item) => item.id === action.payload.id);
        if (index !== -1) {
          state.list[index] = action.payload;
        }
        if (state.selectedOrder?.id === action.payload.id) {
          state.selectedOrder = action.payload;
        }
      })
      .addCase(updateOrder.rejected, (state, action) => {
        state.error = action.payload;
      })
      .addCase(fetchOrderById.fulfilled, (state, action) => {
        state.selectedOrder = action.payload;
        const index = state.list.findIndex((item) => item.id === action.payload.id);
        if (index !== -1) {
          state.list[index] = action.payload;
        }
        if (action.payload.messages) {
          state.messages[action.payload.id] = action.payload.messages;
        }
      })
      .addCase(fetchOrderById.rejected, (state, action) => {
        state.error = action.payload;
      })
      .addCase(fetchOrderAnalytics.pending, (state) => {
        state.analyticsLoading = true;
      })
      .addCase(fetchOrderAnalytics.fulfilled, (state, action) => {
        state.analyticsLoading = false;
        state.analytics = action.payload;
      })
      .addCase(fetchOrderAnalytics.rejected, (state, action) => {
        state.analyticsLoading = false;
        state.error = action.payload;
      })
      .addCase(fetchLateOrders.pending, (state) => {
        state.alertsLoading = true;
      })
      .addCase(fetchLateOrders.fulfilled, (state, action) => {
        state.alertsLoading = false;
        state.lateAlerts = action.payload;
      })
      .addCase(fetchLateOrders.rejected, (state, action) => {
        state.alertsLoading = false;
        state.error = action.payload;
      })
      .addCase(fetchOrderMessages.fulfilled, (state, action) => {
        state.messages[action.payload.orderId] = action.payload.messages;
      })
      .addCase(fetchOrderMessages.rejected, (state, action) => {
        state.error = action.payload;
      })
      .addCase(sendOrderMessage.pending, (state) => {
        state.messageActionLoading = true;
      })
      .addCase(sendOrderMessage.fulfilled, (state, action) => {
        state.messageActionLoading = false;
        const { orderId, message } = action.payload;
        if (!state.messages[orderId]) {
          state.messages[orderId] = [];
        }
        state.messages[orderId] = [message, ...state.messages[orderId]];
        if (state.selectedOrder?.id === orderId) {
          state.selectedOrder = {
            ...state.selectedOrder,
            message_count: (state.selectedOrder.message_count || 0) + 1,
            latest_message_at: message.sent_date,
          };
        }
      })
      .addCase(sendOrderMessage.rejected, (state, action) => {
        state.messageActionLoading = false;
        state.error = action.payload;
      })
      .addCase(replyToOrderMessage.pending, (state) => {
        state.messageActionLoading = true;
      })
      .addCase(replyToOrderMessage.fulfilled, (state, action) => {
        state.messageActionLoading = false;
        const message = action.payload;
        const orderId = message.order_id;
        if (!state.messages[orderId]) {
          state.messages[orderId] = [];
        }
        state.messages[orderId] = [message, ...state.messages[orderId]];
        if (state.selectedOrder?.id === orderId) {
          state.selectedOrder = {
            ...state.selectedOrder,
            message_count: (state.selectedOrder.message_count || 0) + 1,
            latest_message_at: message.sent_date,
          };
        }
      })
      .addCase(replyToOrderMessage.rejected, (state, action) => {
        state.messageActionLoading = false;
        state.error = action.payload;
      })
      .addCase(markOrderMessageRead.fulfilled, (state, action) => {
        const message = action.payload;
        const orderId = message.order_id;
        if (orderId && state.messages[orderId]) {
          const idx = state.messages[orderId].findIndex((item) => item.id === message.id);
          if (idx !== -1) {
            state.messages[orderId][idx] = message;
          }
        }
      })
      .addCase(markOrderMessageRead.rejected, (state, action) => {
        state.error = action.payload;
      })
      .addCase(markOrderAsDelivered.fulfilled, (state, action) => {
        const updatedOrder = action.payload?.order || action.payload;
        if (!updatedOrder?.id) return;

        const index = state.list.findIndex((item) => item.id === updatedOrder.id);
        if (index !== -1) {
          state.list[index] = updatedOrder;
        }

        if (state.selectedOrder?.id === updatedOrder.id) {
          state.selectedOrder = updatedOrder;
        }
      })
      .addCase(markOrderAsDelivered.rejected, (state, action) => {
        state.error = action.payload;
      })
      .addCase(markOrderAsOrdered.fulfilled, (state, action) => {
        const updatedOrder = action.payload?.order || action.payload;
        if (!updatedOrder?.id) return;

        const index = state.list.findIndex((item) => item.id === updatedOrder.id);
        if (index !== -1) {
          state.list[index] = updatedOrder;
        }

        if (state.selectedOrder?.id === updatedOrder.id) {
          state.selectedOrder = updatedOrder;
        }
      })
      .addCase(markOrderAsOrdered.rejected, (state, action) => {
        state.error = action.payload;
      });
  },
});

export const { setOrderFilters, clearOrderError, clearSelectedOrder } = ordersSlice.actions;
export default ordersSlice.reducer;
