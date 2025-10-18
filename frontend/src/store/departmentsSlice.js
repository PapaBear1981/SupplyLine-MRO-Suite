import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

// Async thunks
export const fetchDepartments = createAsyncThunk(
  'departments/fetchDepartments',
  async (includeInactive = false, { rejectWithValue }) => {
    try {
      const response = await api.get('/departments', {
        params: { include_inactive: includeInactive }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch departments' });
    }
  }
);

export const createDepartment = createAsyncThunk(
  'departments/createDepartment',
  async (departmentData, { rejectWithValue }) => {
    try {
      const response = await api.post('/departments', departmentData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to create department' });
    }
  }
);

export const updateDepartment = createAsyncThunk(
  'departments/updateDepartment',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/departments/${id}`, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to update department' });
    }
  }
);

export const deleteDepartment = createAsyncThunk(
  'departments/deleteDepartment',
  async (id, { rejectWithValue }) => {
    try {
      await api.delete(`/departments/${id}`);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to delete department' });
    }
  }
);

export const hardDeleteDepartment = createAsyncThunk(
  'departments/hardDeleteDepartment',
  async (id, { rejectWithValue }) => {
    try {
      await api.delete(`/departments/${id}/hard-delete`);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to permanently delete department' });
    }
  }
);

const departmentsSlice = createSlice({
  name: 'departments',
  initialState: {
    departments: [],
    loading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch departments
      .addCase(fetchDepartments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDepartments.fulfilled, (state, action) => {
        state.departments = action.payload;
        state.loading = false;
      })
      .addCase(fetchDepartments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to fetch departments' };
      })
      // Create department
      .addCase(createDepartment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createDepartment.fulfilled, (state, action) => {
        state.departments.push(action.payload);
        state.loading = false;
      })
      .addCase(createDepartment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to create department' };
      })
      // Update department
      .addCase(updateDepartment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateDepartment.fulfilled, (state, action) => {
        const index = state.departments.findIndex(d => d.id === action.payload.id);
        if (index !== -1) {
          state.departments[index] = action.payload;
        }
        state.loading = false;
      })
      .addCase(updateDepartment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to update department' };
      })
      // Delete department
      .addCase(deleteDepartment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteDepartment.fulfilled, (state, action) => {
        // Update the department in the list to mark as inactive
        const index = state.departments.findIndex(d => d.id === action.payload);
        if (index !== -1) {
          state.departments[index].is_active = false;
        }
        state.loading = false;
      })
      .addCase(deleteDepartment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to delete department' };
      })
      // Hard delete department
      .addCase(hardDeleteDepartment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(hardDeleteDepartment.fulfilled, (state, action) => {
        state.departments = state.departments.filter(d => d.id !== action.payload);
        state.loading = false;
      })
      .addCase(hardDeleteDepartment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'Failed to permanently delete department' };
      });
  },
});

export const { clearError } = departmentsSlice.actions;
export default departmentsSlice.reducer;

