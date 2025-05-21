import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import AnnouncementService from '../services/announcementService';

// Async thunks
export const fetchAnnouncements = createAsyncThunk(
  'announcements/fetchAnnouncements',
  async ({ page = 1, limit = 10, filters = {} }, { rejectWithValue }) => {
    try {
      const data = await AnnouncementService.getAllAnnouncements(page, limit, filters);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch announcements' });
    }
  }
);

export const fetchAnnouncementById = createAsyncThunk(
  'announcements/fetchAnnouncementById',
  async (id, { rejectWithValue }) => {
    try {
      const data = await AnnouncementService.getAnnouncementById(id);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch announcement' });
    }
  }
);

export const createAnnouncement = createAsyncThunk(
  'announcements/createAnnouncement',
  async (announcementData, { rejectWithValue }) => {
    try {
      const data = await AnnouncementService.createAnnouncement(announcementData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to create announcement' });
    }
  }
);

export const updateAnnouncement = createAsyncThunk(
  'announcements/updateAnnouncement',
  async ({ id, announcementData }, { rejectWithValue }) => {
    try {
      const data = await AnnouncementService.updateAnnouncement(id, announcementData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to update announcement' });
    }
  }
);

export const deleteAnnouncement = createAsyncThunk(
  'announcements/deleteAnnouncement',
  async (id, { rejectWithValue }) => {
    try {
      await AnnouncementService.deleteAnnouncement(id);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to delete announcement' });
    }
  }
);

export const markAnnouncementAsRead = createAsyncThunk(
  'announcements/markAsRead',
  async (id, { rejectWithValue }) => {
    try {
      await AnnouncementService.markAsRead(id);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to mark announcement as read' });
    }
  }
);

// Initial state
const initialState = {
  announcements: [],
  currentAnnouncement: null,
  pagination: {
    total: 0,
    page: 1,
    limit: 10,
    pages: 0
  },
  loading: {
    fetchAnnouncements: false,
    fetchAnnouncement: false,
    createAnnouncement: false,
    updateAnnouncement: false,
    deleteAnnouncement: false,
    markAsRead: false
  },
  error: {
    fetchAnnouncements: null,
    fetchAnnouncement: null,
    createAnnouncement: null,
    updateAnnouncement: null,
    deleteAnnouncement: null,
    markAsRead: null
  }
};

// Slice
const announcementSlice = createSlice({
  name: 'announcements',
  initialState,
  reducers: {
    clearErrors: (state) => {
      state.error = {
        fetchAnnouncements: null,
        fetchAnnouncement: null,
        createAnnouncement: null,
        updateAnnouncement: null,
        deleteAnnouncement: null,
        markAsRead: null
      };
    },
    clearCurrentAnnouncement: (state) => {
      state.currentAnnouncement = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch announcements
      .addCase(fetchAnnouncements.pending, (state) => {
        state.loading.fetchAnnouncements = true;
        state.error.fetchAnnouncements = null;
      })
      .addCase(fetchAnnouncements.fulfilled, (state, action) => {
        state.loading.fetchAnnouncements = false;
        state.announcements = action.payload.announcements;
        state.pagination = {
          total: action.payload.total,
          page: action.payload.page,
          limit: action.payload.limit,
          pages: action.payload.pages
        };
      })
      .addCase(fetchAnnouncements.rejected, (state, action) => {
        state.loading.fetchAnnouncements = false;
        state.error.fetchAnnouncements = action.payload || { message: 'Failed to fetch announcements' };
      })

      // Fetch announcement by ID
      .addCase(fetchAnnouncementById.pending, (state) => {
        state.loading.fetchAnnouncement = true;
        state.error.fetchAnnouncement = null;
      })
      .addCase(fetchAnnouncementById.fulfilled, (state, action) => {
        state.loading.fetchAnnouncement = false;
        state.currentAnnouncement = action.payload;
      })
      .addCase(fetchAnnouncementById.rejected, (state, action) => {
        state.loading.fetchAnnouncement = false;
        state.error.fetchAnnouncement = action.payload || { message: 'Failed to fetch announcement' };
      })

      // Create announcement
      .addCase(createAnnouncement.pending, (state) => {
        state.loading.createAnnouncement = true;
        state.error.createAnnouncement = null;
      })
      .addCase(createAnnouncement.fulfilled, (state, action) => {
        state.loading.createAnnouncement = false;
        // Don't modify the list here - let the component refetch if needed
      })
      .addCase(createAnnouncement.rejected, (state, action) => {
        state.loading.createAnnouncement = false;
        state.error.createAnnouncement = action.payload || { message: 'Failed to create announcement' };
      })

      // Update announcement
      .addCase(updateAnnouncement.pending, (state) => {
        state.loading.updateAnnouncement = true;
        state.error.updateAnnouncement = null;
      })
      .addCase(updateAnnouncement.fulfilled, (state, action) => {
        state.loading.updateAnnouncement = false;
        if (state.currentAnnouncement && state.currentAnnouncement.id === action.payload.id) {
          state.currentAnnouncement = action.payload;
        }
        // Update in the list if it exists there
        const index = state.announcements.findIndex(a => a.id === action.payload.id);
        if (index !== -1) {
          state.announcements[index] = action.payload;
        }
      })
      .addCase(updateAnnouncement.rejected, (state, action) => {
        state.loading.updateAnnouncement = false;
        state.error.updateAnnouncement = action.payload || { message: 'Failed to update announcement' };
      })

      // Delete announcement
      .addCase(deleteAnnouncement.pending, (state) => {
        state.loading.deleteAnnouncement = true;
        state.error.deleteAnnouncement = null;
      })
      .addCase(deleteAnnouncement.fulfilled, (state, action) => {
        state.loading.deleteAnnouncement = false;
        state.announcements = state.announcements.filter(a => a.id !== action.payload);
        if (state.currentAnnouncement && state.currentAnnouncement.id === action.payload) {
          state.currentAnnouncement = null;
        }
      })
      .addCase(deleteAnnouncement.rejected, (state, action) => {
        state.loading.deleteAnnouncement = false;
        state.error.deleteAnnouncement = action.payload || { message: 'Failed to delete announcement' };
      })

      // Mark as read
      .addCase(markAnnouncementAsRead.pending, (state) => {
        state.loading.markAsRead = true;
        state.error.markAsRead = null;
      })
      .addCase(markAnnouncementAsRead.fulfilled, (state, action) => {
        state.loading.markAsRead = false;
        // Update the read status in the list
        const index = state.announcements.findIndex(a => a.id === action.payload);
        if (index !== -1) {
          state.announcements[index].read = true;
        }
        // Update current announcement if it's the same one
        if (state.currentAnnouncement && state.currentAnnouncement.id === action.payload) {
          state.currentAnnouncement.read = true;
        }
      })
      .addCase(markAnnouncementAsRead.rejected, (state, action) => {
        state.loading.markAsRead = false;
        state.error.markAsRead = action.payload || { message: 'Failed to mark announcement as read' };
      });
  }
});

export const { clearErrors, clearCurrentAnnouncement } = announcementSlice.actions;

export default announcementSlice.reducer;
