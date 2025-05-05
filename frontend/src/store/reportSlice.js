import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

// Async thunks
export const fetchReportData = createAsyncThunk(
  'reports/fetchReportData',
  async ({ reportType, timeframe, filters }, { rejectWithValue }) => {
    try {
      const response = await api.get('/reports', {
        params: { reportType, timeframe, ...filters }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch report data' });
    }
  }
);

export const fetchToolInventoryReport = createAsyncThunk(
  'reports/fetchToolInventoryReport',
  async (filters, { rejectWithValue }) => {
    try {
      const response = await api.get('/reports/tools', { params: filters });
      console.log('Tool Inventory Report Data:', response.data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch tool inventory report' });
    }
  }
);

export const fetchCheckoutHistoryReport = createAsyncThunk(
  'reports/fetchCheckoutHistoryReport',
  async ({ timeframe, filters }, { rejectWithValue }) => {
    try {
      const response = await api.get('/reports/checkouts', {
        params: { timeframe, ...filters }
      });
      console.log('Checkout History Report Data:', response.data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch checkout history report' });
    }
  }
);

export const fetchDepartmentUsageReport = createAsyncThunk(
  'reports/fetchDepartmentUsageReport',
  async ({ timeframe }, { rejectWithValue }) => {
    try {
      const response = await api.get('/reports/departments', {
        params: { timeframe }
      });
      console.log('Department Usage Report Data:', response.data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch department usage report' });
    }
  }
);

// Initial state
const initialState = {
  currentReport: 'tool-inventory', // Default report type
  timeframe: 'month', // Default timeframe
  filters: {},
  data: null,
  loading: false,
  error: null,
  exportFormat: null, // 'pdf' or 'excel'
  exportLoading: false,
  exportError: null
};

// Slice
const reportSlice = createSlice({
  name: 'reports',
  initialState,
  reducers: {
    setReportType: (state, action) => {
      state.currentReport = action.payload;
      state.data = null; // Clear previous report data
      state.error = null;
    },
    setTimeframe: (state, action) => {
      state.timeframe = action.payload;
    },
    setFilters: (state, action) => {
      state.filters = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    setExportFormat: (state, action) => {
      state.exportFormat = action.payload;
    },
    clearExportError: (state) => {
      state.exportError = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // fetchReportData
      .addCase(fetchReportData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchReportData.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchReportData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while fetching report data' };
      })

      // fetchToolInventoryReport
      .addCase(fetchToolInventoryReport.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchToolInventoryReport.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchToolInventoryReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while fetching tool inventory report' };
      })

      // fetchCheckoutHistoryReport
      .addCase(fetchCheckoutHistoryReport.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCheckoutHistoryReport.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchCheckoutHistoryReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while fetching checkout history report' };
      })

      // fetchDepartmentUsageReport
      .addCase(fetchDepartmentUsageReport.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDepartmentUsageReport.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchDepartmentUsageReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while fetching department usage report' };
      });
  }
});

export const {
  setReportType,
  setTimeframe,
  setFilters,
  clearError,
  setExportFormat,
  clearExportError
} = reportSlice.actions;

export default reportSlice.reducer;
