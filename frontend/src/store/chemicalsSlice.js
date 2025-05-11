import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import ChemicalService from '../services/chemicalService';

// Async thunks
export const fetchChemicals = createAsyncThunk(
  'chemicals/fetchChemicals',
  async (_, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.getAllChemicals();
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch chemicals' });
    }
  }
);

export const fetchChemicalById = createAsyncThunk(
  'chemicals/fetchChemicalById',
  async (id, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.getChemicalById(id);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch chemical' });
    }
  }
);

export const createChemical = createAsyncThunk(
  'chemicals/createChemical',
  async (chemicalData, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.createChemical(chemicalData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to create chemical' });
    }
  }
);

export const updateChemical = createAsyncThunk(
  'chemicals/updateChemical',
  async ({ id, chemicalData }, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.updateChemical(id, chemicalData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to update chemical' });
    }
  }
);

export const deleteChemical = createAsyncThunk(
  'chemicals/deleteChemical',
  async (id, { rejectWithValue }) => {
    try {
      await ChemicalService.deleteChemical(id);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to delete chemical' });
    }
  }
);

export const issueChemical = createAsyncThunk(
  'chemicals/issueChemical',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await ChemicalService.issueChemical(id, data);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to issue chemical' });
    }
  }
);

export const fetchChemicalIssuances = createAsyncThunk(
  'chemicals/fetchIssuances',
  async (id, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.getChemicalIssuances(id);
      return { chemicalId: id, issuances: data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch issuance history' });
    }
  }
);

export const searchChemicals = createAsyncThunk(
  'chemicals/searchChemicals',
  async (query, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.searchChemicals(query);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to search chemicals' });
    }
  }
);

export const archiveChemical = createAsyncThunk(
  'chemicals/archiveChemical',
  async ({ id, reason }, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.archiveChemical(id, reason);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to archive chemical' });
    }
  }
);

export const unarchiveChemical = createAsyncThunk(
  'chemicals/unarchiveChemical',
  async (id, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.unarchiveChemical(id);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to unarchive chemical' });
    }
  }
);

export const fetchArchivedChemicals = createAsyncThunk(
  'chemicals/fetchArchivedChemicals',
  async (filters = {}, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.getArchivedChemicals(filters);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch archived chemicals' });
    }
  }
);

export const fetchWasteAnalytics = createAsyncThunk(
  'chemicals/fetchWasteAnalytics',
  async (timeframe = 'month', { rejectWithValue }) => {
    try {
      const data = await ChemicalService.getWasteAnalytics(timeframe);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch waste analytics' });
    }
  }
);

// Initial state
const initialState = {
  chemicals: [],
  currentChemical: null,
  loading: false,
  error: null,
  searchResults: [],
  issuances: {},
  issuanceLoading: false,
  issuanceError: null,
  archivedChemicals: [],
  archivedLoading: false,
  archivedError: null,
  wasteAnalytics: null,
  wasteLoading: false,
  wasteError: null,
};

// Slice
const chemicalsSlice = createSlice({
  name: 'chemicals',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentChemical: (state) => {
      state.currentChemical = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // fetchChemicals
      .addCase(fetchChemicals.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchChemicals.fulfilled, (state, action) => {
        state.loading = false;
        state.chemicals = action.payload;
      })
      .addCase(fetchChemicals.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while fetching chemicals' };
      })

      // fetchChemicalById
      .addCase(fetchChemicalById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchChemicalById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentChemical = action.payload;
      })
      .addCase(fetchChemicalById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while fetching chemical' };
      })

      // createChemical
      .addCase(createChemical.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createChemical.fulfilled, (state, action) => {
        state.loading = false;
        state.chemicals.push(action.payload);
      })
      .addCase(createChemical.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while creating chemical' };
      })

      // updateChemical
      .addCase(updateChemical.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateChemical.fulfilled, (state, action) => {
        state.loading = false;
        state.currentChemical = action.payload;
        const index = state.chemicals.findIndex(c => c.id === action.payload.id);
        if (index !== -1) {
          state.chemicals[index] = action.payload;
        }
      })
      .addCase(updateChemical.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while updating chemical' };
      })

      // deleteChemical
      .addCase(deleteChemical.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteChemical.fulfilled, (state, action) => {
        state.loading = false;
        state.chemicals = state.chemicals.filter(c => c.id !== action.payload);
        if (state.currentChemical && state.currentChemical.id === action.payload) {
          state.currentChemical = null;
        }
      })
      .addCase(deleteChemical.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while deleting chemical' };
      })

      // issueChemical
      .addCase(issueChemical.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(issueChemical.fulfilled, (state, action) => {
        state.loading = false;
        state.currentChemical = action.payload.chemical;
        const index = state.chemicals.findIndex(c => c.id === action.payload.chemical.id);
        if (index !== -1) {
          state.chemicals[index] = action.payload.chemical;
        }
      })
      .addCase(issueChemical.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while issuing chemical' };
      })

      // fetchChemicalIssuances
      .addCase(fetchChemicalIssuances.pending, (state) => {
        state.issuanceLoading = true;
        state.issuanceError = null;
      })
      .addCase(fetchChemicalIssuances.fulfilled, (state, action) => {
        state.issuanceLoading = false;
        state.issuances[action.payload.chemicalId] = action.payload.issuances;
      })
      .addCase(fetchChemicalIssuances.rejected, (state, action) => {
        state.issuanceLoading = false;
        state.issuanceError = action.payload || { message: 'An error occurred while fetching issuances' };
      })

      // searchChemicals
      .addCase(searchChemicals.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchChemicals.fulfilled, (state, action) => {
        state.loading = false;
        state.searchResults = action.payload;
      })
      .addCase(searchChemicals.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while searching chemicals' };
      })

      // archiveChemical
      .addCase(archiveChemical.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(archiveChemical.fulfilled, (state, action) => {
        state.loading = false;
        state.currentChemical = action.payload.chemical;
        // Remove from active chemicals list
        state.chemicals = state.chemicals.filter(c => c.id !== action.payload.chemical.id);
        // Add to archived chemicals if it exists
        if (state.archivedChemicals.length > 0) {
          state.archivedChemicals.unshift(action.payload.chemical);
        }
      })
      .addCase(archiveChemical.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while archiving chemical' };
      })

      // unarchiveChemical
      .addCase(unarchiveChemical.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(unarchiveChemical.fulfilled, (state, action) => {
        state.loading = false;
        state.currentChemical = action.payload.chemical;
        // Remove from archived chemicals list
        state.archivedChemicals = state.archivedChemicals.filter(c => c.id !== action.payload.chemical.id);
        // Add to active chemicals if it exists
        if (state.chemicals.length > 0) {
          state.chemicals.unshift(action.payload.chemical);
        }
      })
      .addCase(unarchiveChemical.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while unarchiving chemical' };
      })

      // fetchArchivedChemicals
      .addCase(fetchArchivedChemicals.pending, (state) => {
        state.archivedLoading = true;
        state.archivedError = null;
      })
      .addCase(fetchArchivedChemicals.fulfilled, (state, action) => {
        state.archivedLoading = false;
        state.archivedChemicals = action.payload;
      })
      .addCase(fetchArchivedChemicals.rejected, (state, action) => {
        state.archivedLoading = false;
        state.archivedError = action.payload || { message: 'An error occurred while fetching archived chemicals' };
      })

      // fetchWasteAnalytics
      .addCase(fetchWasteAnalytics.pending, (state) => {
        state.wasteLoading = true;
        state.wasteError = null;
      })
      .addCase(fetchWasteAnalytics.fulfilled, (state, action) => {
        state.wasteLoading = false;
        state.wasteAnalytics = action.payload;
      })
      .addCase(fetchWasteAnalytics.rejected, (state, action) => {
        state.wasteLoading = false;
        state.wasteError = action.payload || { message: 'An error occurred while fetching waste analytics' };
      });
  }
});

export const { clearError, clearCurrentChemical } = chemicalsSlice.actions;

export default chemicalsSlice.reducer;
