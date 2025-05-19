import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

// Async thunks
export const fetchRoles = createAsyncThunk(
  'rbac/fetchRoles',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/roles');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch roles' });
    }
  }
);

export const fetchRole = createAsyncThunk(
  'rbac/fetchRole',
  async (id, { rejectWithValue }) => {
    try {
      const response = await api.get(`/roles/${id}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch role' });
    }
  }
);

export const createRole = createAsyncThunk(
  'rbac/createRole',
  async (roleData, { rejectWithValue }) => {
    try {
      const response = await api.post('/roles', roleData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to create role' });
    }
  }
);

export const updateRole = createAsyncThunk(
  'rbac/updateRole',
  async ({ id, roleData }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/roles/${id}`, roleData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to update role' });
    }
  }
);

export const deleteRole = createAsyncThunk(
  'rbac/deleteRole',
  async (id, { rejectWithValue }) => {
    try {
      await api.delete(`/roles/${id}`);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to delete role' });
    }
  }
);

export const fetchPermissions = createAsyncThunk(
  'rbac/fetchPermissions',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/permissions/categories');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch permissions' });
    }
  }
);

export const fetchUserRoles = createAsyncThunk(
  'rbac/fetchUserRoles',
  async (userId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/users/${userId}/roles`);
      return { userId, roles: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch user roles' });
    }
  }
);

export const updateUserRoles = createAsyncThunk(
  'rbac/updateUserRoles',
  async ({ userId, roles }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/users/${userId}/roles`, { roles });
      return { userId, roles: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to update user roles' });
    }
  }
);

export const fetchCurrentUserPermissions = createAsyncThunk(
  'rbac/fetchCurrentUserPermissions',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/auth/permissions');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch permissions' });
    }
  }
);

// Initial state
const initialState = {
  roles: [],
  currentRole: null,
  permissions: [],
  permissionsByCategory: {},
  userRoles: {},
  currentUserPermissions: [],
  loading: false,
  error: null
};

// Slice
const rbacSlice = createSlice({
  name: 'rbac',
  initialState,
  reducers: {
    clearRbacError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // fetchRoles
      .addCase(fetchRoles.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRoles.fulfilled, (state, action) => {
        state.roles = action.payload;
        state.loading = false;
      })
      .addCase(fetchRoles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to fetch roles' };
      })
      
      // fetchRole
      .addCase(fetchRole.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRole.fulfilled, (state, action) => {
        state.currentRole = action.payload;
        state.loading = false;
      })
      .addCase(fetchRole.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to fetch role' };
      })
      
      // createRole
      .addCase(createRole.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createRole.fulfilled, (state, action) => {
        state.roles.push(action.payload);
        state.loading = false;
      })
      .addCase(createRole.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to create role' };
      })
      
      // updateRole
      .addCase(updateRole.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateRole.fulfilled, (state, action) => {
        const index = state.roles.findIndex(role => role.id === action.payload.id);
        if (index !== -1) {
          state.roles[index] = action.payload;
        }
        state.currentRole = action.payload;
        state.loading = false;
      })
      .addCase(updateRole.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to update role' };
      })
      
      // deleteRole
      .addCase(deleteRole.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteRole.fulfilled, (state, action) => {
        state.roles = state.roles.filter(role => role.id !== action.payload);
        state.loading = false;
      })
      .addCase(deleteRole.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to delete role' };
      })
      
      // fetchPermissions
      .addCase(fetchPermissions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPermissions.fulfilled, (state, action) => {
        state.permissionsByCategory = action.payload;
        
        // Flatten permissions for easier access
        const allPermissions = [];
        Object.keys(action.payload).forEach(category => {
          action.payload[category].forEach(permission => {
            allPermissions.push(permission);
          });
        });
        
        state.permissions = allPermissions;
        state.loading = false;
      })
      .addCase(fetchPermissions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to fetch permissions' };
      })
      
      // fetchUserRoles
      .addCase(fetchUserRoles.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserRoles.fulfilled, (state, action) => {
        state.userRoles[action.payload.userId] = action.payload.roles;
        state.loading = false;
      })
      .addCase(fetchUserRoles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to fetch user roles' };
      })
      
      // updateUserRoles
      .addCase(updateUserRoles.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateUserRoles.fulfilled, (state, action) => {
        state.userRoles[action.payload.userId] = action.payload.roles;
        state.loading = false;
      })
      .addCase(updateUserRoles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to update user roles' };
      })
      
      // fetchCurrentUserPermissions
      .addCase(fetchCurrentUserPermissions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCurrentUserPermissions.fulfilled, (state, action) => {
        state.currentUserPermissions = action.payload.permissions;
        state.loading = false;
      })
      .addCase(fetchCurrentUserPermissions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to fetch current user permissions' };
      });
  }
});

export const { clearRbacError } = rbacSlice.actions;

export default rbacSlice.reducer;
