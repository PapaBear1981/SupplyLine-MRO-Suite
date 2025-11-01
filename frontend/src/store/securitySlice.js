import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import SecurityService from '../services/securityService';
import { fetchCurrentUser, forceLogout, login, logout } from './authSlice';

export const fetchSecuritySettings = createAsyncThunk(
  'security/fetchSecuritySettings',
  async (_, { rejectWithValue }) => {
    try {
      const data = await SecurityService.getSecuritySettings();
      return data;
    } catch (error) {
      return rejectWithValue(
        error.response?.data || { message: 'Failed to load security settings' }
      );
    }
  }
);

export const updateSessionTimeout = createAsyncThunk(
  'security/updateSessionTimeout',
  async (minutes, { rejectWithValue }) => {
    try {
      const data = await SecurityService.updateSecuritySettings(minutes);
      return data;
    } catch (error) {
      return rejectWithValue(
        error.response?.data || { message: 'Failed to update security settings' }
      );
    }
  }
);

const initialState = {
  sessionTimeoutMinutes: 30,
  defaultTimeoutMinutes: 30,
  minTimeoutMinutes: 5,
  maxTimeoutMinutes: 240,
  loading: false,
  error: null,
  hasLoaded: false,
  saving: false,
  saveError: null,
  updateSuccess: false,
  updatedAt: null,
  updatedBy: null,
};

const securitySlice = createSlice({
  name: 'security',
  initialState,
  reducers: {
    clearSecurityErrors: (state) => {
      state.error = null;
      state.saveError = null;
    },
    clearUpdateSuccess: (state) => {
      state.updateSuccess = false;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSecuritySettings.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSecuritySettings.fulfilled, (state, action) => {
        state.loading = false;
        state.hasLoaded = true;
        state.error = null;

        const payload = action.payload || {};
        if (typeof payload.session_timeout_minutes === 'number') {
          state.sessionTimeoutMinutes = payload.session_timeout_minutes;
        }
        if (typeof payload.default_timeout_minutes === 'number') {
          state.defaultTimeoutMinutes = payload.default_timeout_minutes;
        }
        if (typeof payload.min_timeout_minutes === 'number') {
          state.minTimeoutMinutes = payload.min_timeout_minutes;
        }
        if (typeof payload.max_timeout_minutes === 'number') {
          state.maxTimeoutMinutes = payload.max_timeout_minutes;
        }

        state.updatedAt = payload.updated_at || null;
        state.updatedBy = payload.updated_by || null;
        state.updateSuccess = false;
      })
      .addCase(fetchSecuritySettings.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to load security settings' };
        state.hasLoaded = true;
      })
      .addCase(updateSessionTimeout.pending, (state) => {
        state.saving = true;
        state.saveError = null;
        state.updateSuccess = false;
      })
      .addCase(updateSessionTimeout.fulfilled, (state, action) => {
        state.saving = false;
        const payload = action.payload || {};

        if (typeof payload.session_timeout_minutes === 'number') {
          state.sessionTimeoutMinutes = payload.session_timeout_minutes;
        }
        if (typeof payload.default_timeout_minutes === 'number') {
          state.defaultTimeoutMinutes = payload.default_timeout_minutes;
        }
        if (typeof payload.min_timeout_minutes === 'number') {
          state.minTimeoutMinutes = payload.min_timeout_minutes;
        }
        if (typeof payload.max_timeout_minutes === 'number') {
          state.maxTimeoutMinutes = payload.max_timeout_minutes;
        }

        state.updatedAt = payload.updated_at || null;
        state.updatedBy = payload.updated_by || null;
        state.updateSuccess = true;
      })
      .addCase(updateSessionTimeout.rejected, (state, action) => {
        state.saving = false;
        state.saveError = action.payload || { message: 'Failed to update security settings' };
        state.updateSuccess = false;
      })
      .addCase(logout.fulfilled, (state) => {
        state.hasLoaded = false;
      })
      .addCase(forceLogout, (state) => {
        state.hasLoaded = false;
      })
      .addCase(login.fulfilled, (state) => {
        state.hasLoaded = false;
      })
      .addCase(fetchCurrentUser.rejected, (state) => {
        state.hasLoaded = false;
      });
  },
});

export const { clearSecurityErrors, clearUpdateSuccess } = securitySlice.actions;
export default securitySlice.reducer;
