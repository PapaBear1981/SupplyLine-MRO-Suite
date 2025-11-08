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

export const lookupChemicalReturn = createAsyncThunk(
  'chemicals/lookupReturn',
  async (payload, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.lookupChemicalReturn(payload);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to locate issued lot' });
    }
  }
);

export const submitChemicalReturn = createAsyncThunk(
  'chemicals/submitReturn',
  async ({ chemicalId, data }, { rejectWithValue }) => {
    try {
      const response = await ChemicalService.returnChemical(chemicalId, data);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to complete return' });
    }
  }
);

export const fetchChemicalReturns = createAsyncThunk(
  'chemicals/fetchReturns',
  async (id, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.getChemicalReturns(id);
      return { chemicalId: id, returns: data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch returns history' });
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
  async (params, { rejectWithValue }) => {
    try {
      // Handle both string (timeframe only) and object (with part_number) params
      let timeframe = 'month';
      let part_number = null;

      if (typeof params === 'string') {
        timeframe = params;
      } else if (params && typeof params === 'object') {
        timeframe = params.timeframe || 'month';
        part_number = params.part_number || null;
      }

      const data = await ChemicalService.getWasteAnalytics(timeframe, part_number);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch waste analytics' });
    }
  }
);

export const fetchUsageAnalytics = createAsyncThunk(
  'chemicals/fetchUsageAnalytics',
  async (params, { rejectWithValue }) => {
    try {
      // Handle both string (part_number only) and object (with timeframe) params
      let part_number = '';
      let timeframe = 'month';

      if (typeof params === 'string') {
        part_number = params;
      } else if (params && typeof params === 'object') {
        part_number = params.part_number || '';
        timeframe = params.timeframe || 'month';
      }

      if (!part_number) {
        return rejectWithValue({ message: 'Part number is required' });
      }

      const data = await ChemicalService.getUsageAnalytics(part_number, timeframe);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch usage analytics' });
    }
  }
);

export const fetchPartNumberAnalytics = createAsyncThunk(
  'chemicals/fetchPartNumberAnalytics',
  async (part_number, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.getPartNumberAnalytics(part_number);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch part number analytics' });
    }
  }
);

export const fetchUniquePartNumbers = createAsyncThunk(
  'chemicals/fetchUniquePartNumbers',
  async (_, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.getUniquePartNumbers();
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch unique part numbers' });
    }
  }
);

// New thunks for reordering functionality
export const fetchChemicalsNeedingReorder = createAsyncThunk(
  'chemicals/fetchChemicalsNeedingReorder',
  async (_, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.getChemicalsNeedingReorder();
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch chemicals needing reorder' });
    }
  }
);

export const fetchChemicalsOnOrder = createAsyncThunk(
  'chemicals/fetchChemicalsOnOrder',
  async (_, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.getChemicalsOnOrder();
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch chemicals on order' });
    }
  }
);

export const fetchChemicalsExpiringSoon = createAsyncThunk(
  'chemicals/fetchChemicalsExpiringSoon',
  async (days = 30, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.getChemicalsExpiringSoon(days);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch chemicals expiring soon' });
    }
  }
);

export const markChemicalAsOrdered = createAsyncThunk(
  'chemicals/markChemicalAsOrdered',
  async ({ id, expected_delivery_date, notes }, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.markChemicalAsOrdered(id, { expected_delivery_date, notes });
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to mark chemical as ordered' });
    }
  }
);

export const markChemicalAsDelivered = createAsyncThunk(
  'chemicals/markChemicalAsDelivered',
  async ({ id, received_quantity }, { rejectWithValue }) => {
    try {
      const data = await ChemicalService.markChemicalAsDelivered(id, { received_quantity });
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to mark chemical as delivered' });
    }
  }
);

// Initial state
const initialState = {
  chemicals: [],
  pagination: null,
  currentChemical: null,
  loading: false,
  error: null,
  searchResults: [],
  issuances: {},
  issuanceLoading: false,
  issuanceError: null,
  returns: {},
  returnsLoading: false,
  returnsError: null,
  returnLookup: null,
  returnLookupLoading: false,
  returnLookupError: null,
  returnSubmitting: false,
  returnSubmitError: null,
  lastReturn: null,
  archivedChemicals: [],
  archivedLoading: false,
  archivedError: null,
  wasteAnalytics: null,
  wasteLoading: false,
  wasteError: null,
  usageAnalytics: null,
  usageLoading: false,
  usageError: null,
  partNumberAnalytics: null,
  partNumberLoading: false,
  partNumberError: null,
  uniquePartNumbers: [],
  uniquePartNumbersLoading: false,
  uniquePartNumbersError: null,
  // New state for reordering functionality
  chemicalsNeedingReorder: [],
  chemicalsOnOrder: [],
  chemicalsExpiringSoon: [],
  reorderLoading: false,
  reorderError: null,
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
        // Handle both array and object responses (with pagination)
        state.chemicals = Array.isArray(action.payload)
          ? action.payload
          : action.payload.chemicals || [];
        state.pagination = action.payload.pagination || null;
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

      // lookupChemicalReturn
      .addCase(lookupChemicalReturn.pending, (state) => {
        state.returnLookupLoading = true;
        state.returnLookupError = null;
        state.lastReturn = null;
      })
      .addCase(lookupChemicalReturn.fulfilled, (state, action) => {
        state.returnLookupLoading = false;
        state.returnLookup = action.payload;
        const chemicalKey = action.payload?.chemical?.id != null ? String(action.payload.chemical.id) : null;
        if (chemicalKey) {
          state.returns[chemicalKey] = action.payload.returns || [];
        }
      })
      .addCase(lookupChemicalReturn.rejected, (state, action) => {
        state.returnLookupLoading = false;
        state.returnLookupError = action.payload || { message: 'Failed to locate issued lot' };
      })

      // submitChemicalReturn
      .addCase(submitChemicalReturn.pending, (state) => {
        state.returnSubmitting = true;
        state.returnSubmitError = null;
      })
      .addCase(submitChemicalReturn.fulfilled, (state, action) => {
        state.returnSubmitting = false;
        state.lastReturn = action.payload.return;
        const chemicalKey = action.payload?.chemical?.id != null ? String(action.payload.chemical.id) : null;

        state.returnLookup = {
          ...state.returnLookup,
          ...action.payload,
        };

        if (chemicalKey) {
          state.currentChemical = action.payload.chemical;
          state.returns[chemicalKey] = action.payload.returns || [];

          if (state.issuances[chemicalKey]) {
            state.issuances[chemicalKey] = state.issuances[chemicalKey].map((issuance) =>
              issuance.id === action.payload.issuance.id ? action.payload.issuance : issuance
            );
          }
        }
      })
      .addCase(submitChemicalReturn.rejected, (state, action) => {
        state.returnSubmitting = false;
        state.returnSubmitError = action.payload || { message: 'Failed to complete return' };
      })

      // fetchChemicalReturns
      .addCase(fetchChemicalReturns.pending, (state) => {
        state.returnsLoading = true;
        state.returnsError = null;
      })
      .addCase(fetchChemicalReturns.fulfilled, (state, action) => {
        state.returnsLoading = false;
        const key = action.payload?.chemicalId != null ? String(action.payload.chemicalId) : null;
        if (key) {
          state.returns[key] = action.payload.returns;
        }
      })
      .addCase(fetchChemicalReturns.rejected, (state, action) => {
        state.returnsLoading = false;
        state.returnsError = action.payload || { message: 'Failed to fetch returns history' };
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
      })

      // fetchUsageAnalytics
      .addCase(fetchUsageAnalytics.pending, (state) => {
        state.usageLoading = true;
        state.usageError = null;
      })
      .addCase(fetchUsageAnalytics.fulfilled, (state, action) => {
        state.usageLoading = false;
        state.usageAnalytics = action.payload;
      })
      .addCase(fetchUsageAnalytics.rejected, (state, action) => {
        state.usageLoading = false;
        state.usageError = action.payload || { message: 'An error occurred while fetching usage analytics' };
      })

      // fetchPartNumberAnalytics
      .addCase(fetchPartNumberAnalytics.pending, (state) => {
        state.partNumberLoading = true;
        state.partNumberError = null;
      })
      .addCase(fetchPartNumberAnalytics.fulfilled, (state, action) => {
        state.partNumberLoading = false;
        state.partNumberAnalytics = action.payload;
      })
      .addCase(fetchPartNumberAnalytics.rejected, (state, action) => {
        state.partNumberLoading = false;
        state.partNumberError = action.payload || { message: 'An error occurred while fetching part number analytics' };
      })

      // fetchUniquePartNumbers
      .addCase(fetchUniquePartNumbers.pending, (state) => {
        state.uniquePartNumbersLoading = true;
        state.uniquePartNumbersError = null;
      })
      .addCase(fetchUniquePartNumbers.fulfilled, (state, action) => {
        state.uniquePartNumbersLoading = false;
        state.uniquePartNumbers = action.payload;
      })
      .addCase(fetchUniquePartNumbers.rejected, (state, action) => {
        state.uniquePartNumbersLoading = false;
        state.uniquePartNumbersError = action.payload || { message: 'An error occurred while fetching unique part numbers' };
      })

      // fetchChemicalsNeedingReorder
      .addCase(fetchChemicalsNeedingReorder.pending, (state) => {
        state.reorderLoading = true;
        state.reorderError = null;
      })
      .addCase(fetchChemicalsNeedingReorder.fulfilled, (state, action) => {
        state.reorderLoading = false;
        state.chemicalsNeedingReorder = action.payload;
      })
      .addCase(fetchChemicalsNeedingReorder.rejected, (state, action) => {
        state.reorderLoading = false;
        state.reorderError = action.payload || { message: 'An error occurred while fetching chemicals needing reorder' };
      })

      // fetchChemicalsOnOrder
      .addCase(fetchChemicalsOnOrder.pending, (state) => {
        state.reorderLoading = true;
        state.reorderError = null;
      })
      .addCase(fetchChemicalsOnOrder.fulfilled, (state, action) => {
        state.reorderLoading = false;
        state.chemicalsOnOrder = action.payload;
      })
      .addCase(fetchChemicalsOnOrder.rejected, (state, action) => {
        state.reorderLoading = false;
        state.reorderError = action.payload || { message: 'An error occurred while fetching chemicals on order' };
      })

      // fetchChemicalsExpiringSoon
      .addCase(fetchChemicalsExpiringSoon.pending, (state) => {
        state.reorderLoading = true;
        state.reorderError = null;
      })
      .addCase(fetchChemicalsExpiringSoon.fulfilled, (state, action) => {
        state.reorderLoading = false;
        state.chemicalsExpiringSoon = action.payload;
      })
      .addCase(fetchChemicalsExpiringSoon.rejected, (state, action) => {
        state.reorderLoading = false;
        state.reorderError = action.payload || { message: 'An error occurred while fetching chemicals expiring soon' };
      })

      // markChemicalAsOrdered
      .addCase(markChemicalAsOrdered.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(markChemicalAsOrdered.fulfilled, (state, action) => {
        state.loading = false;
        // Update the chemical in all relevant lists
        const updatedChemical = action.payload.chemical;

        // Update in main chemicals list
        const chemicalIndex = state.chemicals.findIndex(c => c.id === updatedChemical.id);
        if (chemicalIndex !== -1) {
          state.chemicals[chemicalIndex] = updatedChemical;
        }

        // Remove from chemicals needing reorder
        state.chemicalsNeedingReorder = state.chemicalsNeedingReorder.filter(c => c.id !== updatedChemical.id);

        // Add to chemicals on order
        state.chemicalsOnOrder.push(updatedChemical);

        // Update current chemical if it's the same one
        if (state.currentChemical && state.currentChemical.id === updatedChemical.id) {
          state.currentChemical = updatedChemical;
        }
      })
      .addCase(markChemicalAsOrdered.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while marking chemical as ordered' };
      })

      // markChemicalAsDelivered
      .addCase(markChemicalAsDelivered.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(markChemicalAsDelivered.fulfilled, (state, action) => {
        state.loading = false;
        // Update the chemical in all relevant lists
        const updatedChemical = action.payload.chemical;

        // Update in main chemicals list
        const chemicalIndex = state.chemicals.findIndex(c => c.id === updatedChemical.id);
        if (chemicalIndex !== -1) {
          state.chemicals[chemicalIndex] = updatedChemical;
        } else {
          // If the chemical doesn't exist in the main list, add it
          state.chemicals.push(updatedChemical);
        }

        // Remove from chemicals on order
        state.chemicalsOnOrder = state.chemicalsOnOrder.filter(c => c.id !== updatedChemical.id);

        // Update current chemical if it's the same one
        if (state.currentChemical && state.currentChemical.id === updatedChemical.id) {
          state.currentChemical = updatedChemical;
        }
      })
      .addCase(markChemicalAsDelivered.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || { message: 'An error occurred while marking chemical as delivered' };
      });
  }
});

export const { clearError, clearCurrentChemical } = chemicalsSlice.actions;

export default chemicalsSlice.reducer;
