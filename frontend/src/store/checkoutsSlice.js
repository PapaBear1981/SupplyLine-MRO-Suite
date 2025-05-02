import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import CheckoutService from '../services/checkoutService';

// Async thunks
export const fetchCheckouts = createAsyncThunk(
  'checkouts/fetchCheckouts',
  async (_, { rejectWithValue }) => {
    try {
      const data = await CheckoutService.getAllCheckouts();
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch checkouts' });
    }
  }
);

export const fetchUserCheckouts = createAsyncThunk(
  'checkouts/fetchUserCheckouts',
  async (_, { rejectWithValue }) => {
    try {
      const data = await CheckoutService.getUserCheckouts();
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch user checkouts' });
    }
  }
);

export const checkoutTool = createAsyncThunk(
  'checkouts/checkoutTool',
  async ({ toolId, expectedReturnDate }, { rejectWithValue }) => {
    try {
      const data = await CheckoutService.checkoutTool(toolId, expectedReturnDate);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to checkout tool' });
    }
  }
);

export const returnTool = createAsyncThunk(
  'checkouts/returnTool',
  async ({ checkoutId, condition }, { rejectWithValue }) => {
    try {
      const data = await CheckoutService.returnTool(checkoutId, condition);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to return tool' });
    }
  }
);

export const checkoutToolToUser = createAsyncThunk(
  'checkouts/checkoutToolToUser',
  async ({ toolId, userId, expectedReturnDate }, { rejectWithValue }) => {
    try {
      const data = await CheckoutService.checkoutToolToUser(toolId, userId, expectedReturnDate);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to checkout tool to user' });
    }
  }
);

export const fetchToolCheckoutHistory = createAsyncThunk(
  'checkouts/fetchToolCheckoutHistory',
  async (toolId, { rejectWithValue }) => {
    try {
      const data = await CheckoutService.getToolCheckoutHistory(toolId);
      return { toolId, history: data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch checkout history' });
    }
  }
);

// Initial state
const initialState = {
  checkouts: [],
  userCheckouts: [],
  checkoutHistory: {},
  loading: false,
  error: null,
};

// Slice
const checkoutsSlice = createSlice({
  name: 'checkouts',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch all checkouts
      .addCase(fetchCheckouts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCheckouts.fulfilled, (state, action) => {
        state.loading = false;
        state.checkouts = action.payload;
      })
      .addCase(fetchCheckouts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch user checkouts
      .addCase(fetchUserCheckouts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserCheckouts.fulfilled, (state, action) => {
        state.loading = false;
        state.userCheckouts = action.payload;
      })
      .addCase(fetchUserCheckouts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Checkout tool
      .addCase(checkoutTool.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(checkoutTool.fulfilled, (state, action) => {
        state.loading = false;
        state.checkouts.push(action.payload);
        state.userCheckouts.push(action.payload);
      })
      .addCase(checkoutTool.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Return tool
      .addCase(returnTool.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(returnTool.fulfilled, (state, action) => {
        state.loading = false;
        // Update in all checkouts
        const checkoutIndex = state.checkouts.findIndex(c => c.id === action.payload.id);
        if (checkoutIndex !== -1) {
          state.checkouts[checkoutIndex] = action.payload;
        }
        // Update in user checkouts
        const userCheckoutIndex = state.userCheckouts.findIndex(c => c.id === action.payload.id);
        if (userCheckoutIndex !== -1) {
          state.userCheckouts[userCheckoutIndex] = action.payload;
        }
      })
      .addCase(returnTool.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch tool checkout history
      .addCase(fetchToolCheckoutHistory.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchToolCheckoutHistory.fulfilled, (state, action) => {
        state.loading = false;
        state.checkoutHistory[action.payload.toolId] = action.payload.history;
      })
      .addCase(fetchToolCheckoutHistory.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Checkout tool to user
      .addCase(checkoutToolToUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(checkoutToolToUser.fulfilled, (state, action) => {
        state.loading = false;
        state.checkouts.push(action.payload);
      })
      .addCase(checkoutToolToUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError } = checkoutsSlice.actions;
export default checkoutsSlice.reducer;
