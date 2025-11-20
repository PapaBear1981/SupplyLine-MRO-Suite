import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

export const fetchRequestAlerts = createAsyncThunk(
  'requestAlerts/fetchRequestAlerts',
  async (includeDismissed = false, { rejectWithValue }) => {
    try {
      const response = await api.get('/user-requests/alerts', {
        params: { include_dismissed: includeDismissed },
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch alerts' });
    }
  }
);

export const dismissAlert = createAsyncThunk(
  'requestAlerts/dismissAlert',
  async (alertId, { rejectWithValue }) => {
    try {
      const response = await api.post(`/user-requests/alerts/${alertId}/dismiss`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to dismiss alert' });
    }
  }
);

export const dismissAllAlerts = createAsyncThunk(
  'requestAlerts/dismissAllAlerts',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.post('/user-requests/alerts/dismiss-all');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to dismiss alerts' });
    }
  }
);

const requestAlertsSlice = createSlice({
  name: 'requestAlerts',
  initialState: {
    alerts: [],
    loading: false,
    error: null,
  },
  reducers: {
    clearAlerts: (state) => {
      state.alerts = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch alerts
      .addCase(fetchRequestAlerts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRequestAlerts.fulfilled, (state, action) => {
        state.loading = false;
        state.alerts = action.payload;
      })
      .addCase(fetchRequestAlerts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || 'Failed to fetch alerts';
      })
      // Dismiss alert
      .addCase(dismissAlert.fulfilled, (state, action) => {
        const dismissedAlert = action.payload;
        const index = state.alerts.findIndex((a) => a.id === dismissedAlert.id);
        if (index !== -1) {
          state.alerts[index] = dismissedAlert;
          // Remove dismissed alert from list
          state.alerts = state.alerts.filter((a) => !a.is_dismissed);
        }
      })
      .addCase(dismissAlert.rejected, (state, action) => {
        state.error = action.payload?.message || 'Failed to dismiss alert';
      })
      // Dismiss all alerts
      .addCase(dismissAllAlerts.fulfilled, (state) => {
        state.alerts = [];
      })
      .addCase(dismissAllAlerts.rejected, (state, action) => {
        state.error = action.payload?.message || 'Failed to dismiss all alerts';
      });
  },
});

export const { clearAlerts } = requestAlertsSlice.actions;
export default requestAlertsSlice.reducer;
