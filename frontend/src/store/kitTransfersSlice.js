import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

// Async Thunks
export const createTransfer = createAsyncThunk(
  'kitTransfers/createTransfer',
  async (data, { rejectWithValue }) => {
    try {
      const response = await api.post('/transfers', data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to create transfer' });
    }
  }
);

export const fetchTransfers = createAsyncThunk(
  'kitTransfers/fetchTransfers',
  async (filters = {}, { rejectWithValue }) => {
    try {
      const response = await api.get('/transfers', { params: filters });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch transfers' });
    }
  }
);

export const fetchTransferById = createAsyncThunk(
  'kitTransfers/fetchTransferById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await api.get(`/transfers/${id}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch transfer' });
    }
  }
);

export const completeTransfer = createAsyncThunk(
  'kitTransfers/completeTransfer',
  async (id, { rejectWithValue }) => {
    try {
      const response = await api.put(`/transfers/${id}/complete`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to complete transfer' });
    }
  }
);

export const cancelTransfer = createAsyncThunk(
  'kitTransfers/cancelTransfer',
  async (id, { rejectWithValue }) => {
    try {
      const response = await api.put(`/transfers/${id}/cancel`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to cancel transfer' });
    }
  }
);

// Slice
const kitTransfersSlice = createSlice({
  name: 'kitTransfers',
  initialState: {
    transfers: [],
    currentTransfer: null,
    loading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentTransfer: (state) => {
      state.currentTransfer = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTransfers.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchTransfers.fulfilled, (state, action) => {
        state.loading = false;
        state.transfers = action.payload;
      })
      .addCase(fetchTransfers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchTransferById.fulfilled, (state, action) => {
        state.currentTransfer = action.payload;
      })
      .addCase(createTransfer.fulfilled, (state, action) => {
        state.transfers.unshift(action.payload);
      })
      .addCase(completeTransfer.fulfilled, (state, action) => {
        const index = state.transfers.findIndex(t => t.id === action.payload.id);
        if (index !== -1) {
          state.transfers[index] = action.payload;
        }
        state.currentTransfer = action.payload;
      })
      .addCase(cancelTransfer.fulfilled, (state, action) => {
        const index = state.transfers.findIndex(t => t.id === action.payload.id);
        if (index !== -1) {
          state.transfers[index] = action.payload;
        }
        state.currentTransfer = action.payload;
      });
  },
});

export const { clearError, clearCurrentTransfer } = kitTransfersSlice.actions;
export default kitTransfersSlice.reducer;

