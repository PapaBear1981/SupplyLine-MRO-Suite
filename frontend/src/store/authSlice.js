import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import AuthService from '../services/authService';
import UserService from '../services/userService';

// LocalStorage keys
const ACCESS_TOKEN_KEY = 'supplyline_access_token';
const REFRESH_TOKEN_KEY = 'supplyline_refresh_token';
const USER_DATA_KEY = 'supplyline_user_data';

// Helper to decode JWT token
const decodeToken = (token) => {
  try {
    const payload = token.split('.')[1];
    let decoded;
    if (typeof atob === 'function') {
      decoded = atob(payload);
    } else if (typeof Buffer !== 'undefined') {
      decoded = Buffer.from(payload, 'base64').toString('binary');
    } else {
      return null;
    }
    return JSON.parse(decoded);
  } catch (err) {
    return null;
  }
};

const isTokenExpired = (token) => {
  const data = decodeToken(token);
  if (!data || !data.exp) return true;
  return data.exp * 1000 < Date.now();
};

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
  async (_, { rejectWithValue }) => {
    try {
      const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

      if (!refreshToken) {
        return rejectWithValue({ message: 'Not authenticated' });
      }

      let tokenToUse = accessToken;
      if (!accessToken || isTokenExpired(accessToken)) {
        const newTokens = await AuthService.refreshToken(refreshToken);
        localStorage.setItem(ACCESS_TOKEN_KEY, newTokens.access_token);
        localStorage.setItem(REFRESH_TOKEN_KEY, newTokens.refresh_token);
        tokenToUse = newTokens.access_token;
      }

      if (!tokenToUse) {
        return rejectWithValue({ message: 'Not authenticated' });
      }

      const data = await AuthService.getCurrentUser();
      localStorage.setItem(USER_DATA_KEY, JSON.stringify(data.user));
      return data.user;
    } catch (error) {
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

// Load initial auth state from localStorage
const storedAccess = localStorage.getItem(ACCESS_TOKEN_KEY);
const storedRefresh = localStorage.getItem(REFRESH_TOKEN_KEY);
const storedUser = localStorage.getItem(USER_DATA_KEY);

// Initial state
const initialState = {
  user: storedUser ? JSON.parse(storedUser) : null,
  accessToken: storedAccess || null,
  refreshToken: storedRefresh || null,
  isAuthenticated: !!storedAccess,
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
        // Persist to localStorage
        localStorage.setItem(USER_DATA_KEY, JSON.stringify(action.payload.user));
        localStorage.setItem(ACCESS_TOKEN_KEY, action.payload.access_token);
        localStorage.setItem(REFRESH_TOKEN_KEY, action.payload.refresh_token);
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
        localStorage.removeItem(USER_DATA_KEY);
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
      })
      .addCase(logout.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch current user
      .addCase(fetchCurrentUser.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
        state.refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
        state.isAuthenticated = true;
      })
      .addCase(fetchCurrentUser.rejected, (state, action) => {
        state.loading = false;
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
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
