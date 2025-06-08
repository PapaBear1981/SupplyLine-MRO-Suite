import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import ReportService from '../services/reportService';

// Async thunks
export const fetchReportData = createAsyncThunk(
  'reports/fetchReportData',
  async ({ reportType, timeframe, filters }, { rejectWithValue }) => {
    try {
      // Use appropriate ReportService method based on reportType
      let data;
      switch (reportType) {
        case 'tool-inventory':
          data = await ReportService.getToolInventoryReport(filters);
          break;
        case 'checkout-history':
          data = await ReportService.getCheckoutHistoryReport(timeframe, filters);
          break;
        case 'department-usage':
          data = await ReportService.getDepartmentUsageReport(timeframe);
          break;
        default:
          throw new Error(`Unknown report type: ${reportType}`);
      }
      return data;
    } catch (error) {
      return rejectWithValue(error.message || 'Failed to fetch report data');
    }
  }
);

export const fetchToolInventoryReport = createAsyncThunk(
  'reports/fetchToolInventoryReport',
  async (filters, { rejectWithValue }) => {
    try {
      const data = await ReportService.getToolInventoryReport(filters);
      console.log('Tool Inventory Report Data:', data);
      return data;
    } catch (error) {
      return rejectWithValue(error.message || 'Failed to fetch tool inventory report');
    }
  }
);

export const fetchCheckoutHistoryReport = createAsyncThunk(
  'reports/fetchCheckoutHistoryReport',
  async ({ timeframe, filters }, { rejectWithValue }) => {
    try {
      const data = await ReportService.getCheckoutHistoryReport(timeframe, filters);
      console.log('Checkout History Report Data:', data);
      return data;
    } catch (error) {
      return rejectWithValue(error.message || 'Failed to fetch checkout history report');
    }
  }
);

export const fetchDepartmentUsageReport = createAsyncThunk(
  'reports/fetchDepartmentUsageReport',
  async ({ timeframe }, { rejectWithValue }) => {
    try {
      const data = await ReportService.getDepartmentUsageReport(timeframe);
      console.log('Department Usage Report Data:', data);
      return data;
    } catch (error) {
      return rejectWithValue(error.message || 'Failed to fetch department usage report');
    }
  }
);

// Cycle Count Report Thunks
// Note: These will need to be implemented in ReportService when cycle count reports are migrated to Supabase
export const fetchCycleCountAccuracyReport = createAsyncThunk(
  'reports/fetchCycleCountAccuracyReport',
  async ({ timeframe, filters }, { rejectWithValue }) => {
    try {
      // TODO: Implement cycle count accuracy report in ReportService with Supabase
      // For now, return empty data to prevent errors
      console.warn('Cycle count accuracy report not yet migrated to Supabase');
      return { data: [], message: 'Cycle count reports not yet available with Supabase backend' };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch cycle count accuracy report' });
    }
  }
);

export const fetchCycleCountDiscrepancyReport = createAsyncThunk(
  'reports/fetchCycleCountDiscrepancyReport',
  async ({ timeframe, filters }, { rejectWithValue }) => {
    try {
      // TODO: Implement cycle count discrepancy report in ReportService with Supabase
      console.warn('Cycle count discrepancy report not yet migrated to Supabase');
      return { data: [], message: 'Cycle count reports not yet available with Supabase backend' };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch cycle count discrepancy report' });
    }
  }
);

export const fetchCycleCountPerformanceReport = createAsyncThunk(
  'reports/fetchCycleCountPerformanceReport',
  async ({ timeframe, filters }, { rejectWithValue }) => {
    try {
      // TODO: Implement cycle count performance report in ReportService with Supabase
      console.warn('Cycle count performance report not yet migrated to Supabase');
      return { data: [], message: 'Cycle count reports not yet available with Supabase backend' };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch cycle count performance report' });
    }
  }
);

export const fetchCycleCountCoverageReport = createAsyncThunk(
  'reports/fetchCycleCountCoverageReport',
  async ({ timeframe, filters }, { rejectWithValue }) => {
    try {
      // TODO: Implement cycle count coverage report in ReportService with Supabase
      console.warn('Cycle count coverage report not yet migrated to Supabase');
      return { data: [], message: 'Cycle count reports not yet available with Supabase backend' };
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
