import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import ToolService from '../services/toolService';

// Async thunks
export const fetchTools = createAsyncThunk(
  'tools/fetchTools',
  async (_, { rejectWithValue }) => {
    try {
      const data = await ToolService.getAllTools();
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch tools' });
    }
  }
);

export const fetchToolById = createAsyncThunk(
  'tools/fetchToolById',
  async (id, { rejectWithValue }) => {
    try {
      const data = await ToolService.getToolById(id);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch tool' });
    }
  }
);

export const createTool = createAsyncThunk(
  'tools/createTool',
  async (toolData, { rejectWithValue }) => {
    try {
      const data = await ToolService.createTool(toolData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to create tool' });
    }
  }
);

export const updateTool = createAsyncThunk(
  'tools/updateTool',
  async ({ id, toolData }, { rejectWithValue }) => {
    try {
      const data = await ToolService.updateTool(id, toolData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to update tool' });
    }
  }
);

export const deleteTool = createAsyncThunk(
  'tools/deleteTool',
  async (id, { rejectWithValue }) => {
    try {
      await ToolService.deleteTool(id);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to delete tool' });
    }
  }
);

export const searchTools = createAsyncThunk(
  'tools/searchTools',
  async (query, { rejectWithValue }) => {
    try {
      const data = await ToolService.searchTools(query);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to search tools' });
    }
  }
);

// Initial state
const initialState = {
  tools: [],
  currentTool: null,
  loading: false,
  error: null,
  searchResults: [],
};

// Slice
const toolsSlice = createSlice({
  name: 'tools',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentTool: (state) => {
      state.currentTool = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch all tools
      .addCase(fetchTools.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTools.fulfilled, (state, action) => {
        state.loading = false;
        state.tools = action.payload;
      })
      .addCase(fetchTools.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch tool by ID
      .addCase(fetchToolById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchToolById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentTool = action.payload;
      })
      .addCase(fetchToolById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Create tool
      .addCase(createTool.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createTool.fulfilled, (state, action) => {
        state.loading = false;
        state.tools.push(action.payload);
      })
      .addCase(createTool.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Update tool
      .addCase(updateTool.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateTool.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.tools.findIndex(tool => tool.id === action.payload.id);
        if (index !== -1) {
          state.tools[index] = action.payload;
        }
        state.currentTool = action.payload;
      })
      .addCase(updateTool.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Delete tool
      .addCase(deleteTool.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteTool.fulfilled, (state, action) => {
        state.loading = false;
        state.tools = state.tools.filter(tool => tool.id !== action.payload);
        if (state.currentTool && state.currentTool.id === action.payload) {
          state.currentTool = null;
        }
      })
      .addCase(deleteTool.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Search tools
      .addCase(searchTools.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchTools.fulfilled, (state, action) => {
        state.loading = false;
        state.searchResults = action.payload;
      })
      .addCase(searchTools.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError, clearCurrentTool } = toolsSlice.actions;
export default toolsSlice.reducer;
