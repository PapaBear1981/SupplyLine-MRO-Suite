import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import AuthService from '../services/authService';
import UserService from '../services/userService';

// Async thunks
export const login = createAsyncThunk(
  'auth/login',
  async ({ username, password }, { rejectWithValue }) => {
    try {
      const data = await AuthService.login(username, password);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Login failed' });
    }
  }
);

export const refreshAccessToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { rejectWithValue }) => {
    try {
      const data = await AuthService.refreshToken();
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Token refresh failed' });
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await AuthService.logout();
      return null;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Logout failed' });
    }
  }
);

export const fetchCurrentUser = createAsyncThunk(
  'auth/fetchCurrentUser',
  async (_, { rejectWithValue, dispatch }) => {
    try {
      const data = await AuthService.getCurrentUser();
      return data;
    } catch (error) {
      if (error.response && error.response.status === 401) {
        try {
          await dispatch(refreshAccessToken()).unwrap();
          const data = await AuthService.getCurrentUser();
          return data;
        } catch (refreshError) {
          return rejectWithValue(refreshError.response?.data || { message: 'Not authenticated' });
        }
      }
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch user' });
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (userData, { rejectWithValue }) => {
    try {
      const data = await AuthService.register(userData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Registration failed' });
    }
  }
);

export const updateProfile = createAsyncThunk(
  'auth/updateProfile',
  async (profileData, { rejectWithValue }) => {
    try {
      const data = await UserService.updateProfile(profileData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to update profile' });
    }
  }
);

export const updateAvatar = createAsyncThunk(
  'auth/updateAvatar',
  async (formData, { rejectWithValue }) => {
    try {
      const data = await UserService.uploadAvatar(formData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to upload avatar' });
    }
  }
);

export const changePassword = createAsyncThunk(
  'auth/changePassword',
  async (passwordData, { rejectWithValue }) => {
    try {
      const data = await UserService.changePassword(passwordData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to change password' });
    }
  }
);

export const fetchUserActivity = createAsyncThunk(
  'auth/fetchUserActivity',
  async (_, { rejectWithValue }) => {
    try {
      const data = await UserService.getUserActivity();
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch activity logs' });
    }
  }
);

// Initial state
const accessToken = localStorage.getItem('access_token');
const refreshToken = localStorage.getItem('refresh_token');

const initialState = {
  user: null,
  accessToken,
  refreshToken,
  isAuthenticated: !!accessToken,
  loading: false,
  error: null,
  registrationSuccess: null,
  activityLogs: [],
};

// Slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.isAuthenticated = true;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Logout
      .addCase(logout.pending, (state) => {
        state.loading = true;
      })
      .addCase(logout.fulfilled, (state) => {
        state.loading = false;
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
      })
      .addCase(logout.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Refresh access token
      .addCase(refreshAccessToken.fulfilled, (state, action) => {
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.isAuthenticated = true;
      })
      .addCase(refreshAccessToken.rejected, (state) => {
        state.accessToken = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
      })
      // Fetch current user
      .addCase(fetchCurrentUser.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
      })
      .addCase(fetchCurrentUser.rejected, (state, _action) => {
        state.loading = false;
        state.user = null;
        state.isAuthenticated = false;
      })
      // Register
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.loading = false;
        // With the new approval system, registration doesn't log the user in automatically
        // Instead, we show a success message but keep the user logged out
        state.user = null;
        state.isAuthenticated = false;
        // We'll use the success message from the backend
        state.registrationSuccess = action.payload.message || 'Registration request submitted successfully.';
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Update profile
      .addCase(updateProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(updateProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.error || 'Failed to update profile';
      })
      // Update avatar
      .addCase(updateAvatar.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateAvatar.fulfilled, (state, action) => {
        state.loading = false;
        if (state.user) {
          state.user.avatar = action.payload.avatar;
        }
      })
      .addCase(updateAvatar.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.error || 'Failed to upload avatar';
      })
      // Change password
      .addCase(changePassword.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(changePassword.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(changePassword.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.error || 'Failed to change password';
      })
      // Fetch user activity
      .addCase(fetchUserActivity.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserActivity.fulfilled, (state, action) => {
        state.loading = false;
        state.activityLogs = action.payload;
      })
      .addCase(fetchUserActivity.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.error || 'Failed to fetch activity logs';
      });
  },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;
