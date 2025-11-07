import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Mock API calls for now
const fetchDashboardLayoutAPI = async () => {
  // In a real app, this would be an API call
  const layout = localStorage.getItem('dashboardLayout');
  return layout ? JSON.parse(layout) : null;
};

const saveDashboardLayoutAPI = async (layout) => {
  // In a real app, this would be an API call
  localStorage.setItem('dashboardLayout', JSON.stringify(layout));
  return layout;
};

export const fetchDashboardLayout = createAsyncThunk(
  'dashboard/fetchLayout',
  async (_, { rejectWithValue }) => {
    try {
      const response = await fetchDashboardLayoutAPI();
      return response;
    } catch (error) {
      return rejectWithValue(error.toString());
    }
  }
);

export const saveDashboardLayout = createAsyncThunk(
  'dashboard/saveLayout',
  async (layout, { rejectWithValue }) => {
    try {
      const response = await saveDashboardLayoutAPI(layout);
      return response;
    } catch (error) {
      return rejectWithValue(error.toString());
    }
  }
);

const initialState = {
  layout: [],
  initialLayout: [
    { i: 'Announcements', x: 8, y: 0, w: 4, h: 6 },
    { i: 'QuickActions', x: 8, y: 6, w: 4, h: 6 },
    { i: 'CalibrationNotifications', x: 0, y: 0, w: 8, h: 3 },
    { i: 'KitAlertsSummary', x: 0, y: 3, w: 8, h: 3 },
    { i: 'UserCheckoutStatus', x: 0, y: 6, w: 8, h: 6 },
    { i: 'MyKits', x: 0, y: 12, w: 4, h: 6 },
    { i: 'RecentKitActivity', x: 4, y: 12, w: 4, h: 6 },
  ],
  status: 'idle',
  error: null,
};

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    setLayout: (state, action) => {
      state.layout = action.payload;
    },
    addWidget: (state, action) => {
      state.layout.push(action.payload);
    },
    removeWidget: (state, action) => {
      state.layout = state.layout.filter((widget) => widget.i !== action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboardLayout.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchDashboardLayout.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.layout = action.payload || state.initialLayout;
      })
      .addCase(fetchDashboardLayout.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
        state.layout = state.initialLayout;
      })
      .addCase(saveDashboardLayout.fulfilled, (state, action) => {
        state.layout = action.payload;
      });
  },
});

export const { setLayout, addWidget, removeWidget } = dashboardSlice.actions;

export default dashboardSlice.reducer;
