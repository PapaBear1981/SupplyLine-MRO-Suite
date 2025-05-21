import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async thunks for API calls
export const fetchCycleCountSchedules = createAsyncThunk(
  'cycleCount/fetchSchedules',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/cycle-counts/schedules', { params });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: 'Failed to fetch cycle count schedules' });
    }
  }
);

export const fetchCycleCountSchedule = createAsyncThunk(
  'cycleCount/fetchSchedule',
  async ({ id, includeBatches = false }, { rejectWithValue }) => {
    try {
      const response = await axios.get(`/api/cycle-counts/schedules/${id}`, {
        params: { include_batches: includeBatches }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: `Failed to fetch cycle count schedule ${id}` });
    }
  }
);

export const createCycleCountSchedule = createAsyncThunk(
  'cycleCount/createSchedule',
  async (scheduleData, { rejectWithValue }) => {
    try {
      const response = await axios.post('/api/cycle-counts/schedules', scheduleData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: 'Failed to create cycle count schedule' });
    }
  }
);

export const updateCycleCountSchedule = createAsyncThunk(
  'cycleCount/updateSchedule',
  async ({ id, scheduleData }, { rejectWithValue }) => {
    try {
      const response = await axios.put(`/api/cycle-counts/schedules/${id}`, scheduleData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: `Failed to update cycle count schedule ${id}` });
    }
  }
);

export const deleteCycleCountSchedule = createAsyncThunk(
  'cycleCount/deleteSchedule',
  async (id, { rejectWithValue }) => {
    try {
      const response = await axios.delete(`/api/cycle-counts/schedules/${id}`);
      return { id, ...(response.data || {}) };
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: `Failed to delete cycle count schedule ${id}` });
    }
  }
);

export const fetchCycleCountBatches = createAsyncThunk(
  'cycleCount/fetchBatches',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/cycle-counts/batches', { params });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: 'Failed to fetch cycle count batches' });
    }
  }
);

export const fetchCycleCountBatch = createAsyncThunk(
  'cycleCount/fetchBatch',
  async ({ id, includeItems = false }, { rejectWithValue }) => {
    try {
      const response = await axios.get(`/api/cycle-counts/batches/${id}`, {
        params: { include_items: includeItems }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: `Failed to fetch cycle count batch ${id}` });
    }
  }
);

export const createCycleCountBatch = createAsyncThunk(
  'cycleCount/createBatch',
  async (batchData, { rejectWithValue }) => {
    try {
      const response = await axios.post('/api/cycle-counts/batches', batchData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: 'Failed to create cycle count batch' });
    }
  }
);

export const updateCycleCountBatch = createAsyncThunk(
  'cycleCount/updateBatch',
  async ({ id, batchData }, { rejectWithValue }) => {
    try {
      const response = await axios.put(`/api/cycle-counts/batches/${id}`, batchData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: `Failed to update cycle count batch ${id}` });
    }
  }
);

export const deleteCycleCountBatch = createAsyncThunk(
  'cycleCount/deleteBatch',
  async (id, { rejectWithValue }) => {
    try {
      const response = await axios.delete(`/api/cycle-counts/batches/${id}`);
      return { id, ...(response.data || {}) };
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: `Failed to delete cycle count batch ${id}` });
    }
  }
);

export const fetchCycleCountItems = createAsyncThunk(
  'cycleCount/fetchItems',
  async ({ batchId, params = {} }, { rejectWithValue }) => {
    try {
      const response = await axios.get(`/api/cycle-counts/batches/${batchId}/items`, { params });
      return { batchId, items: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: `Failed to fetch cycle count items for batch ${batchId}` });
    }
  }
);

export const updateCycleCountItem = createAsyncThunk(
  'cycleCount/updateItem',
  async ({ id, itemData }, { rejectWithValue }) => {
    try {
      const response = await axios.put(`/api/cycle-counts/items/${id}`, itemData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: `Failed to update cycle count item ${id}` });
    }
  }
);

export const submitCountResult = createAsyncThunk(
  'cycleCount/submitResult',
  async ({ itemId, resultData }, { rejectWithValue }) => {
    try {
      const response = await axios.post(`/api/cycle-counts/items/${itemId}/count`, resultData);
      return { itemId, ...(response.data || {}) };
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: `Failed to submit count result for item ${itemId}` });
    }
  }
);

export const fetchCountDiscrepancies = createAsyncThunk(
  'cycleCount/fetchDiscrepancies',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/cycle-counts/discrepancies', { params });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: 'Failed to fetch count discrepancies' });
    }
  }
);

export const approveCountAdjustment = createAsyncThunk(
  'cycleCount/approveAdjustment',
  async ({ resultId, adjustmentData }, { rejectWithValue }) => {
    try {
      const response = await axios.post(`/api/cycle-counts/results/${resultId}/adjust`, adjustmentData);
      return { resultId, ...(response.data || {}) };
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: `Failed to approve count adjustment for result ${resultId}` });
    }
  }
);

export const fetchCycleCountStats = createAsyncThunk(
  'cycleCount/fetchStats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/cycle-counts/stats');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: 'Failed to fetch cycle count statistics' });
    }
  }
);

// Initial state
const initialState = {
  schedules: {
    items: [],
    loading: false,
    error: null
  },
  currentSchedule: {
    data: null,
    loading: false,
    error: null
  },
  batches: {
    items: [],
    loading: false,
    error: null
  },
  currentBatch: {
    data: null,
    loading: false,
    error: null
  },
  items: {
    byBatchId: {},
    loadingByBatchId: {},   // { [batchId]: true | false }
    errorByBatchId: {}
  },
  discrepancies: {
    items: [],
    loading: false,
    error: null
  },
  stats: {
    data: null,
    loading: false,
    error: null
  }
};

// Create slice
const cycleCountSlice = createSlice({
  name: 'cycleCount',
  initialState,
  reducers: {
    clearCurrentSchedule: (state) => {
      state.currentSchedule.data = null;
      state.currentSchedule.error = null;
    },
    clearCurrentBatch: (state) => {
      state.currentBatch.data = null;
      state.currentBatch.error = null;
    }
  },
  extraReducers: (builder) => {
    // Schedules
    builder
      .addCase(fetchCycleCountSchedules.pending, (state) => {
        state.schedules.loading = true;
        state.schedules.error = null;
      })
      .addCase(fetchCycleCountSchedules.fulfilled, (state, action) => {
        state.schedules.loading = false;
        state.schedules.items = action.payload;
      })
      .addCase(fetchCycleCountSchedules.rejected, (state, action) => {
        state.schedules.loading = false;
        state.schedules.error = action.payload || { error: 'Failed to fetch schedules' };
      })
      .addCase(fetchCycleCountSchedule.pending, (state) => {
        state.currentSchedule.loading = true;
        state.currentSchedule.error = null;
      })
      .addCase(fetchCycleCountSchedule.fulfilled, (state, action) => {
        state.currentSchedule.loading = false;
        state.currentSchedule.data = action.payload;
      })
      .addCase(fetchCycleCountSchedule.rejected, (state, action) => {
        state.currentSchedule.loading = false;
        state.currentSchedule.error = action.payload || { error: 'Failed to fetch schedule' };
      })
      .addCase(createCycleCountSchedule.fulfilled, (state, action) => {
        state.schedules.items.push(action.payload);
      })
      .addCase(updateCycleCountSchedule.fulfilled, (state, action) => {
        const index = state.schedules.items.findIndex(s => s.id === action.payload.id);
        if (index !== -1) {
          state.schedules.items[index] = action.payload;
        }
        if (state.currentSchedule.data?.id === action.payload.id) {
          state.currentSchedule.data = action.payload;
        }
      })
      .addCase(deleteCycleCountSchedule.fulfilled, (state, action) => {
        state.schedules.items = state.schedules.items.filter(s => s.id !== action.payload.id);
        if (state.currentSchedule.data?.id === action.payload.id) {
          state.currentSchedule.data = null;
        }
      });

    // Batches
    builder
      .addCase(fetchCycleCountBatches.pending, (state) => {
        state.batches.loading = true;
        state.batches.error = null;
      })
      .addCase(fetchCycleCountBatches.fulfilled, (state, action) => {
        state.batches.loading = false;
        state.batches.items = action.payload;
      })
      .addCase(fetchCycleCountBatches.rejected, (state, action) => {
        state.batches.loading = false;
        state.batches.error = action.payload || { error: 'Failed to fetch batches' };
      })
      .addCase(fetchCycleCountBatch.pending, (state) => {
        state.currentBatch.loading = true;
        state.currentBatch.error = null;
      })
      .addCase(fetchCycleCountBatch.fulfilled, (state, action) => {
        state.currentBatch.loading = false;
        state.currentBatch.data = action.payload;
      })
      .addCase(fetchCycleCountBatch.rejected, (state, action) => {
        state.currentBatch.loading = false;
        state.currentBatch.error = action.payload || { error: 'Failed to fetch batch' };
      })
      .addCase(createCycleCountBatch.fulfilled, (state, action) => {
        state.batches.items.push(action.payload);
      })
      .addCase(updateCycleCountBatch.fulfilled, (state, action) => {
        const index = state.batches.items.findIndex(b => b.id === action.payload.id);
        if (index !== -1) {
          state.batches.items[index] = action.payload;
        }
        if (state.currentBatch.data?.id === action.payload.id) {
          state.currentBatch.data = action.payload;
        }
      })
      .addCase(deleteCycleCountBatch.fulfilled, (state, action) => {
        state.batches.items = state.batches.items.filter(b => b.id !== action.payload.id);
        if (state.currentBatch.data?.id === action.payload.id) {
          state.currentBatch.data = null;
        }
      });

    // Items
    builder
      .addCase(fetchCycleCountItems.pending, (state, action) => {
        const batchId = action.meta.arg.batchId;
        state.items.loadingByBatchId[batchId] = true;
        state.items.errorByBatchId[batchId] = null;
      })
      .addCase(fetchCycleCountItems.fulfilled, (state, action) => {
        const batchId = action.payload.batchId;
        state.items.loadingByBatchId[batchId] = false;
        state.items.byBatchId[batchId] = action.payload.items;
      })
      .addCase(fetchCycleCountItems.rejected, (state, action) => {
        const batchId = action.meta.arg.batchId;
        state.items.loadingByBatchId[batchId] = false;
        state.items.errorByBatchId[batchId] = action.payload || { error: 'Failed to fetch items' };
      })
      .addCase(updateCycleCountItem.fulfilled, (state, action) => {
        // Update item in all relevant places
        Object.keys(state.items.byBatchId).forEach(batchId => {
          const index = state.items.byBatchId[batchId].findIndex(i => i.id === action.payload.id);
          if (index !== -1) {
            state.items.byBatchId[batchId][index] = action.payload;
          }
        });
      })
      .addCase(submitCountResult.fulfilled, (state, action) => {
        // Update item status in all relevant places
        Object.keys(state.items.byBatchId).forEach(batchId => {
          const index = state.items.byBatchId[batchId].findIndex(i => i.id === action.payload.item_id);
          if (index !== -1) {
            state.items.byBatchId[batchId][index].status = 'counted';
          }
        });
      });

    // Discrepancies
    builder
      .addCase(fetchCountDiscrepancies.pending, (state) => {
        state.discrepancies.loading = true;
        state.discrepancies.error = null;
      })
      .addCase(fetchCountDiscrepancies.fulfilled, (state, action) => {
        state.discrepancies.loading = false;
        state.discrepancies.items = action.payload;
      })
      .addCase(fetchCountDiscrepancies.rejected, (state, action) => {
        state.discrepancies.loading = false;
        state.discrepancies.error = action.payload || { error: 'Failed to fetch discrepancies' };
      });

    // Stats
    builder
      .addCase(fetchCycleCountStats.pending, (state) => {
        state.stats.loading = true;
        state.stats.error = null;
      })
      .addCase(fetchCycleCountStats.fulfilled, (state, action) => {
        state.stats.loading = false;
        state.stats.data = action.payload;
      })
      .addCase(fetchCycleCountStats.rejected, (state, action) => {
        state.stats.loading = false;
        state.stats.error = action.payload || { error: 'Failed to fetch stats' };
      });
  }
});

export const { clearCurrentSchedule, clearCurrentBatch } = cycleCountSlice.actions;

export default cycleCountSlice.reducer;
