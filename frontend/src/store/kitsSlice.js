import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

// ==================== Async Thunks ====================

// Aircraft Types
export const fetchAircraftTypes = createAsyncThunk(
  'kits/fetchAircraftTypes',
  async (includeInactive = false, { rejectWithValue }) => {
    try {
      const response = await api.get('/aircraft-types', {
        params: { include_inactive: includeInactive }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch aircraft types' });
    }
  }
);

export const createAircraftType = createAsyncThunk(
  'kits/createAircraftType',
  async (data, { rejectWithValue }) => {
    try {
      const response = await api.post('/aircraft-types', data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to create aircraft type' });
    }
  }
);

export const updateAircraftType = createAsyncThunk(
  'kits/updateAircraftType',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/aircraft-types/${id}`, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to update aircraft type' });
    }
  }
);

export const deactivateAircraftType = createAsyncThunk(
  'kits/deactivateAircraftType',
  async (id, { rejectWithValue }) => {
    try {
      const response = await api.delete(`/aircraft-types/${id}`);
      return { id, ...response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to deactivate aircraft type' });
    }
  }
);

// Kits
export const fetchKits = createAsyncThunk(
  'kits/fetchKits',
  async (filters = {}, { rejectWithValue }) => {
    try {
      const response = await api.get('/kits', { params: filters });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch kits' });
    }
  }
);

export const fetchKitById = createAsyncThunk(
  'kits/fetchKitById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await api.get(`/kits/${id}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch kit details' });
    }
  }
);

export const createKit = createAsyncThunk(
  'kits/createKit',
  async (data, { rejectWithValue }) => {
    try {
      const response = await api.post('/kits', data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to create kit' });
    }
  }
);

export const updateKit = createAsyncThunk(
  'kits/updateKit',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/kits/${id}`, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to update kit' });
    }
  }
);

export const deleteKit = createAsyncThunk(
  'kits/deleteKit',
  async (id, { rejectWithValue }) => {
    try {
      await api.delete(`/kits/${id}`);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to delete kit' });
    }
  }
);

export const duplicateKit = createAsyncThunk(
  'kits/duplicateKit',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/kits/${id}/duplicate`, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to duplicate kit' });
    }
  }
);

// Kit Wizard
export const kitWizardStep = createAsyncThunk(
  'kits/kitWizardStep',
  async (data, { rejectWithValue }) => {
    try {
      const response = await api.post('/kits/wizard', data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Wizard step failed' });
    }
  }
);

// Kit Boxes
export const fetchKitBoxes = createAsyncThunk(
  'kits/fetchKitBoxes',
  async (kitId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/kits/${kitId}/boxes`);
      return { kitId, boxes: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch kit boxes' });
    }
  }
);

export const addKitBox = createAsyncThunk(
  'kits/addKitBox',
  async ({ kitId, data }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/kits/${kitId}/boxes`, data);
      return { kitId, box: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to add box' });
    }
  }
);

export const updateKitBox = createAsyncThunk(
  'kits/updateKitBox',
  async ({ kitId, boxId, data }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/kits/${kitId}/boxes/${boxId}`, data);
      return { kitId, box: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to update box' });
    }
  }
);

export const deleteKitBox = createAsyncThunk(
  'kits/deleteKitBox',
  async ({ kitId, boxId }, { rejectWithValue }) => {
    try {
      await api.delete(`/kits/${kitId}/boxes/${boxId}`);
      return { kitId, boxId };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to delete box' });
    }
  }
);

// Kit Items
export const fetchKitItems = createAsyncThunk(
  'kits/fetchKitItems',
  async ({ kitId, filters = {} }, { rejectWithValue }) => {
    try {
      const response = await api.get(`/kits/${kitId}/items`, { params: filters });
      return { kitId, items: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch kit items' });
    }
  }
);

export const addKitItem = createAsyncThunk(
  'kits/addKitItem',
  async ({ kitId, data }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/kits/${kitId}/items`, data);
      return { kitId, item: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to add item' });
    }
  }
);

// Kit Expendables
export const fetchKitExpendables = createAsyncThunk(
  'kits/fetchKitExpendables',
  async ({ kitId, filters = {} }, { rejectWithValue }) => {
    try {
      const response = await api.get(`/kits/${kitId}/expendables`, { params: filters });
      return { kitId, expendables: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch expendables' });
    }
  }
);

export const addKitExpendable = createAsyncThunk(
  'kits/addKitExpendable',
  async ({ kitId, data }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/kits/${kitId}/expendables`, data);
      return { kitId, expendable: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to add expendable' });
    }
  }
);

// Kit Issuance
export const issueFromKit = createAsyncThunk(
  'kits/issueFromKit',
  async ({ kitId, data }, { rejectWithValue }) => {
    try {
      const response = await api.post(`/kits/${kitId}/issue`, data);
      return { kitId, issuance: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to issue item' });
    }
  }
);

export const fetchKitIssuances = createAsyncThunk(
  'kits/fetchKitIssuances',
  async ({ kitId, filters = {} }, { rejectWithValue }) => {
    try {
      const response = await api.get(`/kits/${kitId}/issuances`, { params: filters });
      return { kitId, issuances: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch issuances' });
    }
  }
);

// Kit Analytics
export const fetchKitAnalytics = createAsyncThunk(
  'kits/fetchKitAnalytics',
  async ({ kitId, days = 30 }, { rejectWithValue }) => {
    try {
      const response = await api.get(`/kits/${kitId}/analytics`, { params: { days } });
      return { kitId, analytics: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch analytics' });
    }
  }
);

// Kit Alerts
export const fetchKitAlerts = createAsyncThunk(
  'kits/fetchKitAlerts',
  async (kitId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/kits/${kitId}/alerts`);
      return { kitId, alerts: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch alerts' });
    }
  }
);

// Reports
export const fetchInventoryReport = createAsyncThunk(
  'kits/fetchInventoryReport',
  async (filters = {}, { rejectWithValue }) => {
    try {
      const response = await api.get('/kits/reports/inventory', { params: filters });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch inventory report' });
    }
  }
);

export const fetchIssuanceReport = createAsyncThunk(
  'kits/fetchIssuanceReport',
  async ({ kitId = null, filters = {} }, { rejectWithValue }) => {
    try {
      // Use different endpoint based on whether we're fetching for a specific kit or all kits
      const endpoint = kitId ? `/kits/${kitId}/issuances` : '/kits/issuances';

      // For all-kits endpoint, pass filters as query params (aircraft_type_id, start_date, end_date)
      // For specific kit endpoint, pass date filters only (kit is in URL)
      const params = { ...filters };
      // Remove kit_id from params since it's either in the URL or we want all kits
      delete params.kit_id;

      const response = await api.get(endpoint, { params });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch issuance report' });
    }
  }
);

export const fetchTransferReport = createAsyncThunk(
  'kits/fetchTransferReport',
  async (filters = {}, { rejectWithValue }) => {
    try {
      const response = await api.get('/transfers', { params: filters });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch transfer report' });
    }
  }
);

export const fetchReorderReport = createAsyncThunk(
  'kits/fetchReorderReport',
  async (filters = {}, { rejectWithValue }) => {
    try {
      const response = await api.get('/kits/reorders', { params: filters });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch reorder report' });
    }
  }
);

export const fetchKitUtilization = createAsyncThunk(
  'kits/fetchKitUtilization',
  async ({ kitId = null, aircraftTypeId = null, days = 30 } = {}, { rejectWithValue }) => {
    try {
      const endpoint = kitId ? `/kits/${kitId}/analytics` : '/kits/analytics/utilization';
      const params = { days };

      // Add filters for the all-kits endpoint
      if (!kitId) {
        if (aircraftTypeId) params.aircraft_type_id = aircraftTypeId;
      }

      const response = await api.get(endpoint, { params });

      return {
        scope: kitId ? 'kit' : 'all',
        kitId: kitId ? Number(kitId) : null,
        data: response.data,
      };
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch kit utilization' });
    }
  }
);

// Reorder Request Management
export const fetchReorderRequests = createAsyncThunk(
  'kits/fetchReorderRequests',
  async ({ kitId = null, filters = {} }, { rejectWithValue }) => {
    try {
      const params = { ...filters };
      if (kitId) {
        params.kit_id = kitId;
      }
      const response = await api.get('/reorder-requests', { params });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch reorder requests' });
    }
  }
);

export const approveReorderRequest = createAsyncThunk(
  'kits/approveReorderRequest',
  async (requestId, { rejectWithValue }) => {
    try {
      const response = await api.put(`/reorder-requests/${requestId}/approve`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to approve reorder request' });
    }
  }
);

export const markReorderAsOrdered = createAsyncThunk(
  'kits/markReorderAsOrdered',
  async (requestId, { rejectWithValue }) => {
    try {
      const response = await api.put(`/reorder-requests/${requestId}/order`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to mark reorder as ordered' });
    }
  }
);

export const fulfillReorderRequest = createAsyncThunk(
  'kits/fulfillReorderRequest',
  async ({ requestId, boxId }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/reorder-requests/${requestId}/fulfill`, {
        box_id: boxId
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fulfill reorder request' });
    }
  }
);

export const cancelReorderRequest = createAsyncThunk(
  'kits/cancelReorderRequest',
  async (requestId, { rejectWithValue }) => {
    try {
      const response = await api.put(`/reorder-requests/${requestId}/cancel`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to cancel reorder request' });
    }
  }
);

export const createReorderRequest = createAsyncThunk(
  'kits/createReorderRequest',
  async (data, { rejectWithValue }) => {
    try {
      const kitId = data.kitId;
      let requestData;
      let config = {};

      // If there's an image, use FormData
      if (data.image) {
        const formData = new FormData();
        Object.keys(data).forEach(key => {
          if (key !== 'kitId' && key !== 'image') {
            formData.append(key, data[key]);
          }
        });
        formData.append('image', data.image);
        requestData = formData;
        // Don't set Content-Type header - let axios set it automatically with boundary
      } else {
        // Otherwise use JSON
        const { kitId: _, ...rest } = data;
        requestData = rest;
      }

      const response = await api.post(`/kits/${kitId}/reorder`, requestData, config);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to create reorder request' });
    }
  }
);

// ==================== Slice ====================

const kitsSlice = createSlice({
  name: 'kits',
  initialState: {
    aircraftTypes: [],
    kits: [],
    currentKit: null,
    kitBoxes: {},
    kitItems: {},
    kitExpendables: {},
    kitIssuances: {},
    kitAnalytics: {
      dataByKit: {},
      loadingByKit: {},
      errorByKit: {}
    },
    kitAlerts: {},
    inventoryReport: [],
    issuanceReport: [],
    transferReport: [],
    reorderReport: [],
    utilizationReport: null,
    reorderRequests: [],
    wizardData: null,
    loading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentKit: (state) => {
      state.currentKit = null;
    },
    setWizardData: (state, action) => {
      state.wizardData = action.payload;
    },
    clearWizardData: (state) => {
      state.wizardData = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Aircraft Types
      .addCase(fetchAircraftTypes.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchAircraftTypes.fulfilled, (state, action) => {
        state.loading = false;
        state.aircraftTypes = action.payload;
      })
      .addCase(fetchAircraftTypes.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(createAircraftType.fulfilled, (state, action) => {
        state.aircraftTypes.push(action.payload);
      })
      .addCase(updateAircraftType.fulfilled, (state, action) => {
        const index = state.aircraftTypes.findIndex(at => at.id === action.payload.id);
        if (index !== -1) {
          state.aircraftTypes[index] = action.payload;
        }
      })
      .addCase(deactivateAircraftType.fulfilled, (state, action) => {
        const index = state.aircraftTypes.findIndex(at => at.id === action.payload.id);
        if (index !== -1) {
          state.aircraftTypes[index].is_active = false;
        }
      })

      // Kits
      .addCase(fetchKits.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchKits.fulfilled, (state, action) => {
        state.loading = false;
        state.kits = action.payload;
      })
      .addCase(fetchKits.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      .addCase(fetchKitById.fulfilled, (state, action) => {
        state.currentKit = action.payload;
      })
      
      .addCase(createKit.fulfilled, (state, action) => {
        state.kits.push(action.payload);
        state.currentKit = action.payload;
      })
      
      .addCase(updateKit.fulfilled, (state, action) => {
        const index = state.kits.findIndex(k => k.id === action.payload.id);
        if (index !== -1) {
          state.kits[index] = action.payload;
        }
        state.currentKit = action.payload;
      })
      
      .addCase(deleteKit.fulfilled, (state, action) => {
        state.kits = state.kits.filter(k => k.id !== action.payload);
      })
      
      // Kit Boxes
      .addCase(fetchKitBoxes.fulfilled, (state, action) => {
        state.kitBoxes[action.payload.kitId] = action.payload.boxes;
      })
      .addCase(addKitBox.fulfilled, (state, action) => {
        const { kitId, box } = action.payload;
        if (state.kitBoxes[kitId]) {
          state.kitBoxes[kitId].push(box);
        }
        // Update current kit's box count
        if (state.currentKit && state.currentKit.id === kitId) {
          state.currentKit.box_count = (state.currentKit.box_count || 0) + 1;
        }
      })
      .addCase(updateKitBox.fulfilled, (state, action) => {
        const { kitId, box } = action.payload;
        if (state.kitBoxes[kitId]) {
          const index = state.kitBoxes[kitId].findIndex(b => b.id === box.id);
          if (index !== -1) {
            state.kitBoxes[kitId][index] = box;
          }
        }
      })
      .addCase(deleteKitBox.fulfilled, (state, action) => {
        const { kitId, boxId } = action.payload;
        if (state.kitBoxes[kitId]) {
          state.kitBoxes[kitId] = state.kitBoxes[kitId].filter(b => b.id !== boxId);
        }
        // Update current kit's box count
        if (state.currentKit && state.currentKit.id === kitId) {
          state.currentKit.box_count = Math.max((state.currentKit.box_count || 1) - 1, 0);
        }
      })

      // Kit Items
      .addCase(fetchKitItems.fulfilled, (state, action) => {
        state.kitItems[action.payload.kitId] = action.payload.items;
      })
      .addCase(addKitItem.fulfilled, (state, action) => {
        const { kitId, item } = action.payload;
        // Update the items list if it exists
        if (state.kitItems[kitId]) {
          state.kitItems[kitId].push(item);
        }
        // Update the current kit's item count
        if (state.currentKit && state.currentKit.id === kitId) {
          state.currentKit.item_count = (state.currentKit.item_count || 0) + 1;
        }
      })
      .addCase(addKitExpendable.fulfilled, (state, action) => {
        const { kitId, expendable } = action.payload;
        // Update the items list if it exists (expendables are included in items)
        if (state.kitItems[kitId]) {
          state.kitItems[kitId].push(expendable);
        }
        // Update the current kit's item count
        if (state.currentKit && state.currentKit.id === kitId) {
          state.currentKit.item_count = (state.currentKit.item_count || 0) + 1;
        }
      })

      // Kit Issuances
      .addCase(issueFromKit.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(issueFromKit.fulfilled, (state, action) => {
        state.loading = false;
        const { kitId, issuance } = action.payload;
        // Update the kit items to reflect the issuance
        if (state.kitItems[kitId]) {
          const items = state.kitItems[kitId];
          // Find and update the issued item quantity
          if (items.items) {
            const itemIndex = items.items.findIndex(item => item.id === issuance.item_id);
            if (itemIndex !== -1) {
              items.items[itemIndex].quantity -= issuance.quantity;
              if (items.items[itemIndex].quantity <= 0) {
                items.items[itemIndex].status = 'issued';
              }
            }
          }
          if (items.expendables) {
            const expIndex = items.expendables.findIndex(exp => exp.id === issuance.item_id);
            if (expIndex !== -1) {
              items.expendables[expIndex].quantity -= issuance.quantity;
              if (items.expendables[expIndex].quantity <= 0) {
                items.expendables[expIndex].status = items.expendables[expIndex].source === 'item' ? 'issued' : 'out_of_stock';
              }
            }
          }
        }
        // Add to issuances list
        if (state.kitIssuances[kitId]) {
          state.kitIssuances[kitId].unshift(issuance);
        }
      })
      .addCase(issueFromKit.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchKitIssuances.fulfilled, (state, action) => {
        state.kitIssuances[action.payload.kitId] = action.payload.issuances;
      })

      // Kit Analytics
      .addCase(fetchKitAnalytics.pending, (state, action) => {
        const kitId = action.meta.arg?.kitId;
        if (kitId) {
          state.kitAnalytics.loadingByKit[kitId] = true;
          state.kitAnalytics.errorByKit[kitId] = null;
        }
      })
      .addCase(fetchKitAnalytics.fulfilled, (state, action) => {
        const { kitId, analytics } = action.payload;
        state.kitAnalytics.loadingByKit[kitId] = false;
        state.kitAnalytics.dataByKit[kitId] = analytics;
      })
      .addCase(fetchKitAnalytics.rejected, (state, action) => {
        const kitId = action.meta.arg?.kitId;
        if (kitId) {
          state.kitAnalytics.loadingByKit[kitId] = false;
          state.kitAnalytics.errorByKit[kitId] = action.payload || { message: 'Failed to fetch analytics' };
        }
      })

      // Kit Alerts
      .addCase(fetchKitAlerts.fulfilled, (state, action) => {
        state.kitAlerts[action.payload.kitId] = action.payload.alerts;
      })

      // Reorder Requests
      .addCase(fetchReorderRequests.fulfilled, (state, action) => {
        state.reorderRequests = action.payload;
      })
      .addCase(approveReorderRequest.fulfilled, (state, action) => {
        const index = state.reorderRequests.findIndex(r => r.id === action.payload.id);
        if (index !== -1) {
          state.reorderRequests[index] = action.payload;
        }
      })
      .addCase(markReorderAsOrdered.fulfilled, (state, action) => {
        const index = state.reorderRequests.findIndex(r => r.id === action.payload.id);
        if (index !== -1) {
          state.reorderRequests[index] = action.payload;
        }
      })
      .addCase(fulfillReorderRequest.fulfilled, (state, action) => {
        const index = state.reorderRequests.findIndex(r => r.id === action.payload.id);
        if (index !== -1) {
          state.reorderRequests[index] = action.payload;
        }
      })
      .addCase(cancelReorderRequest.fulfilled, (state, action) => {
        const index = state.reorderRequests.findIndex(r => r.id === action.payload.id);
        if (index !== -1) {
          state.reorderRequests[index] = action.payload;
        }
      })
      .addCase(createReorderRequest.fulfilled, (state, action) => {
        state.reorderRequests.unshift(action.payload);
      })

      // Reports
      .addCase(fetchInventoryReport.fulfilled, (state, action) => {
        state.inventoryReport = action.payload;
      })
      .addCase(fetchIssuanceReport.fulfilled, (state, action) => {
        state.issuanceReport = action.payload;
      })
      .addCase(fetchTransferReport.fulfilled, (state, action) => {
        state.transferReport = action.payload;
      })
      .addCase(fetchReorderReport.fulfilled, (state, action) => {
        state.reorderReport = action.payload;
      })
      .addCase(fetchKitUtilization.fulfilled, (state, action) => {
        state.utilizationReport = action.payload;
      });
  },
});

export const { clearError, clearCurrentKit, setWizardData, clearWizardData } = kitsSlice.actions;
export default kitsSlice.reducer;

