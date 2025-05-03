import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import AuditService from '../services/auditService';

// Async thunks
export const fetchAuditLogs = createAsyncThunk(
  'audit/fetchAuditLogs',
  async ({ page = 1, limit = 10 }, { rejectWithValue }) => {
    try {
      const data = await AuditService.getAllLogs(page, limit);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch audit logs' });
    }
  }
);

export const fetchUserLogs = createAsyncThunk(
  'audit/fetchUserLogs',
  async ({ userId, page = 1, limit = 10 }, { rejectWithValue }) => {
    try {
      const data = await AuditService.getUserLogs(userId, page, limit);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch user logs' });
    }
  }
);

export const fetchActivityMetrics = createAsyncThunk(
  'audit/fetchActivityMetrics',
  async (timeframe = 'week', { rejectWithValue }) => {
    try {
      const data = await AuditService.getActivityMetrics(timeframe);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch activity metrics' });
    }
  }
);

// Initial state
const initialState = {
  logs: [],
  userLogs: [],
  metrics: null,
  loading: false,
  error: null,
};

// Slice
const auditSlice = createSlice({
  name: 'audit',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch audit logs
      .addCase(fetchAuditLogs.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAuditLogs.fulfilled, (state, action) => {
        state.loading = false;
        state.logs = action.payload;
      })
      .addCase(fetchAuditLogs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch user logs
      .addCase(fetchUserLogs.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserLogs.fulfilled, (state, action) => {
        state.loading = false;
        state.userLogs = action.payload;
      })
      .addCase(fetchUserLogs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch activity metrics
      .addCase(fetchActivityMetrics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchActivityMetrics.fulfilled, (state, action) => {
        state.loading = false;
        state.metrics = action.payload;
      })
      .addCase(fetchActivityMetrics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError } = auditSlice.actions;
export default auditSlice.reducer;
