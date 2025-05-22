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

// Cycle Count Report Thunks
export const fetchCycleCountAccuracyReport = createAsyncThunk(
  'reports/fetchCycleCountAccuracyReport',
  async ({ timeframe, filters }, { rejectWithValue }) => {
    try {
      const response = await api.get('/reports/cycle-counts/accuracy', {
        params: { timeframe, ...filters }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch cycle count accuracy report' });
    }
  }
);

export const fetchCycleCountDiscrepancyReport = createAsyncThunk(
  'reports/fetchCycleCountDiscrepancyReport',
  async ({ timeframe, filters }, { rejectWithValue }) => {
    try {
      const response = await api.get('/reports/cycle-counts/discrepancies', {
        params: { timeframe, ...filters }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch cycle count discrepancy report' });
    }
  }
);

export const fetchCycleCountPerformanceReport = createAsyncThunk(
  'reports/fetchCycleCountPerformanceReport',
  async ({ timeframe, filters }, { rejectWithValue }) => {
    try {
      const response = await api.get('/reports/cycle-counts/performance', {
        params: { timeframe, ...filters }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch cycle count performance report' });
    }
  }
);

export const fetchCycleCountCoverageReport = createAsyncThunk(
  'reports/fetchCycleCountCoverageReport',
  async ({ timeframe, filters }, { rejectWithValue }) => {
    try {
      const response = await api.get('/reports/cycle-counts/coverage', {
        params: { timeframe, ...filters }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch cycle count coverage report' });
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
      })

      // Cycle Count Reports
      .addCase(fetchCycleCountAccuracyReport.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCycleCountAccuracyReport.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchCycleCountAccuracyReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while fetching cycle count accuracy report' };
      })

      .addCase(fetchCycleCountDiscrepancyReport.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCycleCountDiscrepancyReport.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchCycleCountDiscrepancyReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while fetching cycle count discrepancy report' };
      })

      .addCase(fetchCycleCountPerformanceReport.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCycleCountPerformanceReport.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchCycleCountPerformanceReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while fetching cycle count performance report' };
      })

      .addCase(fetchCycleCountCoverageReport.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCycleCountCoverageReport.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchCycleCountCoverageReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while fetching cycle count coverage report' };
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
