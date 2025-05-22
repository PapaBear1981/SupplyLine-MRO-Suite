import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';
import axios from 'axios';

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

// Cycle Count Reports
export const fetchCycleCountAccuracyReport = createAsyncThunk(
  'reports/fetchCycleCountAccuracyReport',
  async ({ timeframe, location, category }, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/reports/cycle-counts/accuracy', {
        params: { timeframe, location, category }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch cycle count accuracy report' });
    }
  }
);

export const fetchCycleCountDiscrepancyReport = createAsyncThunk(
  'reports/fetchCycleCountDiscrepancyReport',
  async ({ timeframe, type, location, category }, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/reports/cycle-counts/discrepancies', {
        params: { timeframe, type, location, category }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch cycle count discrepancy report' });
    }
  }
);

export const fetchCycleCountPerformanceReport = createAsyncThunk(
  'reports/fetchCycleCountPerformanceReport',
  async ({ timeframe }, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/reports/cycle-counts/performance', {
        params: { timeframe }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch cycle count performance report' });
    }
  }
);

export const fetchCycleCountCoverageReport = createAsyncThunk(
  'reports/fetchCycleCountCoverageReport',
  async ({ days, location, category }, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/reports/cycle-counts/coverage', {
        params: { days, location, category }
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
  exportError: null,
  cycleCountReports: {
    accuracy: {
      data: null,
      loading: false,
      error: null
    },
    discrepancy: {
      data: null,
      loading: false,
      error: null
    },
    performance: {
      data: null,
      loading: false,
      error: null
    },
    coverage: {
      data: null,
      loading: false,
      error: null
    }
  }
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

      // Cycle Count Accuracy Report
      .addCase(fetchCycleCountAccuracyReport.pending, (state) => {
        state.cycleCountReports.accuracy.loading = true;
        state.cycleCountReports.accuracy.error = null;
      })
      .addCase(fetchCycleCountAccuracyReport.fulfilled, (state, action) => {
        state.cycleCountReports.accuracy.loading = false;
        state.cycleCountReports.accuracy.data = action.payload;
      })
      .addCase(fetchCycleCountAccuracyReport.rejected, (state, action) => {
        state.cycleCountReports.accuracy.loading = false;
        state.cycleCountReports.accuracy.error = action.payload || { message: 'An error occurred while fetching cycle count accuracy report' };
      })

      // Cycle Count Discrepancy Report
      .addCase(fetchCycleCountDiscrepancyReport.pending, (state) => {
        state.cycleCountReports.discrepancy.loading = true;
        state.cycleCountReports.discrepancy.error = null;
      })
      .addCase(fetchCycleCountDiscrepancyReport.fulfilled, (state, action) => {
        state.cycleCountReports.discrepancy.loading = false;
        state.cycleCountReports.discrepancy.data = action.payload;
      })
      .addCase(fetchCycleCountDiscrepancyReport.rejected, (state, action) => {
        state.cycleCountReports.discrepancy.loading = false;
        state.cycleCountReports.discrepancy.error = action.payload || { message: 'An error occurred while fetching cycle count discrepancy report' };
      })

      // Cycle Count Performance Report
      .addCase(fetchCycleCountPerformanceReport.pending, (state) => {
        state.cycleCountReports.performance.loading = true;
        state.cycleCountReports.performance.error = null;
      })
      .addCase(fetchCycleCountPerformanceReport.fulfilled, (state, action) => {
        state.cycleCountReports.performance.loading = false;
        state.cycleCountReports.performance.data = action.payload;
      })
      .addCase(fetchCycleCountPerformanceReport.rejected, (state, action) => {
        state.cycleCountReports.performance.loading = false;
        state.cycleCountReports.performance.error = action.payload || { message: 'An error occurred while fetching cycle count performance report' };
      })

      // Cycle Count Coverage Report
      .addCase(fetchCycleCountCoverageReport.pending, (state) => {
        state.cycleCountReports.coverage.loading = true;
        state.cycleCountReports.coverage.error = null;
      })
      .addCase(fetchCycleCountCoverageReport.fulfilled, (state, action) => {
        state.cycleCountReports.coverage.loading = false;
        state.cycleCountReports.coverage.data = action.payload;
      })
      .addCase(fetchCycleCountCoverageReport.rejected, (state, action) => {
        state.cycleCountReports.coverage.loading = false;
        state.cycleCountReports.coverage.error = action.payload || { message: 'An error occurred while fetching cycle count coverage report' };
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
