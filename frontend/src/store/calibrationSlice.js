import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import CalibrationService from '../services/calibrationService';

// Async thunks
export const fetchCalibrations = createAsyncThunk(
  'calibration/fetchCalibrations',
  async ({ page = 1, limit = 20, filters = {} }, { rejectWithValue }) => {
    try {
      const data = await CalibrationService.getAllCalibrations(page, limit, filters);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch calibrations' });
    }
  }
);

export const fetchCalibrationsDue = createAsyncThunk(
  'calibration/fetchCalibrationsDue',
  async (days = 30, { rejectWithValue }) => {
    try {
      const data = await CalibrationService.getCalibrationsDue(days);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch calibrations due' });
    }
  }
);

export const fetchOverdueCalibrations = createAsyncThunk(
  'calibration/fetchOverdueCalibrations',
  async (_, { rejectWithValue }) => {
    try {
      const data = await CalibrationService.getOverdueCalibrations();
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch overdue calibrations' });
    }
  }
);

export const fetchToolCalibrations = createAsyncThunk(
  'calibration/fetchToolCalibrations',
  async ({ toolId, page = 1, limit = 20 }, { rejectWithValue }) => {
    try {
      const data = await CalibrationService.getToolCalibrations(toolId, page, limit);
      return { toolId, data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch tool calibrations' });
    }
  }
);

export const addCalibration = createAsyncThunk(
  'calibration/addCalibration',
  async ({ toolId, calibrationData }, { rejectWithValue }) => {
    try {
      const data = await CalibrationService.addCalibration(toolId, calibrationData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to add calibration' });
    }
  }
);

export const fetchCalibrationStandards = createAsyncThunk(
  'calibration/fetchCalibrationStandards',
  async ({ page = 1, limit = 20, filters = {} }, { rejectWithValue }) => {
    try {
      const data = await CalibrationService.getAllCalibrationStandards(page, limit, filters);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch calibration standards' });
    }
  }
);

export const fetchCalibrationStandard = createAsyncThunk(
  'calibration/fetchCalibrationStandard',
  async (id, { rejectWithValue }) => {
    try {
      const data = await CalibrationService.getCalibrationStandard(id);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch calibration standard' });
    }
  }
);

export const addCalibrationStandard = createAsyncThunk(
  'calibration/addCalibrationStandard',
  async (standardData, { rejectWithValue }) => {
    try {
      const data = await CalibrationService.addCalibrationStandard(standardData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to add calibration standard' });
    }
  }
);

export const updateCalibrationStandard = createAsyncThunk(
  'calibration/updateCalibrationStandard',
  async ({ id, standardData }, { rejectWithValue }) => {
    try {
      const data = await CalibrationService.updateCalibrationStandard(id, standardData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to update calibration standard' });
    }
  }
);

// Initial state
const initialState = {
  calibrations: [],
  calibrationsDue: [],
  overdueCalibrations: [],
  toolCalibrations: {},
  calibrationStandards: [],
  currentCalibrationStandard: null,
  pagination: {
    page: 1,
    limit: 20,
    total: 0,
    pages: 0
  },
  loading: false,
  error: null,
  standardsLoading: false,
  standardsError: null
};

// Slice
const calibrationSlice = createSlice({
  name: 'calibration',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearStandardsError: (state) => {
      state.standardsError = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch calibrations
      .addCase(fetchCalibrations.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCalibrations.fulfilled, (state, action) => {
        state.loading = false;
        state.calibrations = action.payload.calibrations;
        state.pagination = action.payload.pagination;
      })
      .addCase(fetchCalibrations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to fetch calibrations' };
      })
      
      // Fetch calibrations due
      .addCase(fetchCalibrationsDue.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCalibrationsDue.fulfilled, (state, action) => {
        state.loading = false;
        state.calibrationsDue = action.payload;
      })
      .addCase(fetchCalibrationsDue.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to fetch calibrations due' };
      })
      
      // Fetch overdue calibrations
      .addCase(fetchOverdueCalibrations.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOverdueCalibrations.fulfilled, (state, action) => {
        state.loading = false;
        state.overdueCalibrations = action.payload;
      })
      .addCase(fetchOverdueCalibrations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to fetch overdue calibrations' };
      })
      
      // Fetch tool calibrations
      .addCase(fetchToolCalibrations.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchToolCalibrations.fulfilled, (state, action) => {
        state.loading = false;
        state.toolCalibrations[action.payload.toolId] = action.payload.data;
      })
      .addCase(fetchToolCalibrations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to fetch tool calibrations' };
      })
      
      // Add calibration
      .addCase(addCalibration.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(addCalibration.fulfilled, (state, action) => {
        state.loading = false;
      })
      .addCase(addCalibration.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to add calibration' };
      })
      
      // Fetch calibration standards
      .addCase(fetchCalibrationStandards.pending, (state) => {
        state.standardsLoading = true;
        state.standardsError = null;
      })
      .addCase(fetchCalibrationStandards.fulfilled, (state, action) => {
        state.standardsLoading = false;
        state.calibrationStandards = action.payload.standards;
        state.pagination = action.payload.pagination;
      })
      .addCase(fetchCalibrationStandards.rejected, (state, action) => {
        state.standardsLoading = false;
        state.standardsError = action.payload || { message: 'Failed to fetch calibration standards' };
      })
      
      // Fetch calibration standard
      .addCase(fetchCalibrationStandard.pending, (state) => {
        state.standardsLoading = true;
        state.standardsError = null;
      })
      .addCase(fetchCalibrationStandard.fulfilled, (state, action) => {
        state.standardsLoading = false;
        state.currentCalibrationStandard = action.payload;
      })
      .addCase(fetchCalibrationStandard.rejected, (state, action) => {
        state.standardsLoading = false;
        state.standardsError = action.payload || { message: 'Failed to fetch calibration standard' };
      })
      
      // Add calibration standard
      .addCase(addCalibrationStandard.pending, (state) => {
        state.standardsLoading = true;
        state.standardsError = null;
      })
      .addCase(addCalibrationStandard.fulfilled, (state, action) => {
        state.standardsLoading = false;
      })
      .addCase(addCalibrationStandard.rejected, (state, action) => {
        state.standardsLoading = false;
        state.standardsError = action.payload || { message: 'Failed to add calibration standard' };
      })
      
      // Update calibration standard
      .addCase(updateCalibrationStandard.pending, (state) => {
        state.standardsLoading = true;
        state.standardsError = null;
      })
      .addCase(updateCalibrationStandard.fulfilled, (state, action) => {
        state.standardsLoading = false;
        if (state.currentCalibrationStandard?.id === action.payload.standard.id) {
          state.currentCalibrationStandard = action.payload.standard;
        }
      })
      .addCase(updateCalibrationStandard.rejected, (state, action) => {
        state.standardsLoading = false;
        state.standardsError = action.payload || { message: 'Failed to update calibration standard' };
      });
  }
});

export const { clearError, clearStandardsError } = calibrationSlice.actions;

export default calibrationSlice.reducer;
