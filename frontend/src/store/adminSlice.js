import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import AdminService from '../services/adminService';

// Async thunks
export const fetchDashboardStats = createAsyncThunk(
  'admin/fetchDashboardStats',
  async (_, { rejectWithValue }) => {
    try {
      const data = await AdminService.getDashboardStats();
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch dashboard statistics' });
    }
  }
);

export const fetchRegistrationRequests = createAsyncThunk(
  'admin/fetchRegistrationRequests',
  async (status = 'pending', { rejectWithValue }) => {
    try {
      const data = await AdminService.getRegistrationRequests(status);
      return { data, status };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch registration requests' });
    }
  }
);

export const approveRegistrationRequest = createAsyncThunk(
  'admin/approveRegistrationRequest',
  async ({ requestId, adminNotes }, { rejectWithValue, dispatch }) => {
    try {
      const data = await AdminService.approveRegistrationRequest(requestId, adminNotes);
      // Refresh the registration requests list after approval
      dispatch(fetchRegistrationRequests('pending'));
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to approve registration request' });
    }
  }
);

export const denyRegistrationRequest = createAsyncThunk(
  'admin/denyRegistrationRequest',
  async ({ requestId, adminNotes }, { rejectWithValue, dispatch }) => {
    try {
      const data = await AdminService.denyRegistrationRequest(requestId, adminNotes);
      // Refresh the registration requests list after denial
      dispatch(fetchRegistrationRequests('pending'));
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to deny registration request' });
    }
  }
);

// Initial state
const initialState = {
  dashboardStats: null,
  registrationRequests: {
    pending: [],
    approved: [],
    denied: [],
    all: []
  },
  loading: {
    dashboardStats: false,
    registrationRequests: false,
    approveRequest: false,
    denyRequest: false
  },
  error: {
    dashboardStats: null,
    registrationRequests: null,
    approveRequest: null,
    denyRequest: null
  }
};

// Slice
const adminSlice = createSlice({
  name: 'admin',
  initialState,
  reducers: {
    clearErrors: (state) => {
      state.error = {
        dashboardStats: null,
        registrationRequests: null,
        approveRequest: null,
        denyRequest: null
      };
    }
  },
  extraReducers: (builder) => {
    builder
      // Dashboard stats
      .addCase(fetchDashboardStats.pending, (state) => {
        state.loading.dashboardStats = true;
        state.error.dashboardStats = null;
      })
      .addCase(fetchDashboardStats.fulfilled, (state, action) => {
        state.loading.dashboardStats = false;
        state.dashboardStats = action.payload;
      })
      .addCase(fetchDashboardStats.rejected, (state, action) => {
        state.loading.dashboardStats = false;
        state.error.dashboardStats = action.payload || { message: 'Failed to fetch dashboard statistics' };
      })

      // Registration requests
      .addCase(fetchRegistrationRequests.pending, (state) => {
        state.loading.registrationRequests = true;
        state.error.registrationRequests = null;
      })
      .addCase(fetchRegistrationRequests.fulfilled, (state, action) => {
        state.loading.registrationRequests = false;
        const { data, status } = action.payload;

        // Update the appropriate list based on status
        if (status === 'all') {
          state.registrationRequests.all = data;
        } else if (status === 'pending') {
          state.registrationRequests.pending = data;
        } else if (status === 'approved') {
          state.registrationRequests.approved = data;
        } else if (status === 'denied') {
          state.registrationRequests.denied = data;
        }
      })
      .addCase(fetchRegistrationRequests.rejected, (state, action) => {
        state.loading.registrationRequests = false;
        state.error.registrationRequests = action.payload || { message: 'Failed to fetch registration requests' };
      })

      // Approve request
      .addCase(approveRegistrationRequest.pending, (state) => {
        state.loading.approveRequest = true;
        state.error.approveRequest = null;
      })
      .addCase(approveRegistrationRequest.fulfilled, (state) => {
        state.loading.approveRequest = false;
      })
      .addCase(approveRegistrationRequest.rejected, (state, action) => {
        state.loading.approveRequest = false;
        state.error.approveRequest = action.payload || { message: 'Failed to approve registration request' };
      })

      // Deny request
      .addCase(denyRegistrationRequest.pending, (state) => {
        state.loading.denyRequest = true;
        state.error.denyRequest = null;
      })
      .addCase(denyRegistrationRequest.fulfilled, (state) => {
        state.loading.denyRequest = false;
      })
      .addCase(denyRegistrationRequest.rejected, (state, action) => {
        state.loading.denyRequest = false;
        state.error.denyRequest = action.payload || { message: 'Failed to deny registration request' };
      });
  }
});

export const { clearErrors } = adminSlice.actions;
export default adminSlice.reducer;
