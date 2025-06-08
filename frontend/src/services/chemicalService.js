import api from './api';

const ChemicalService = {
  // Get all chemicals
  getAllChemicals: async () => {
    try {
      const response = await api.get('/chemicals');
      return response.data;
    } catch (error) {
      console.error('API Error [GET] chemicals:', error);
      throw error;
    }
  },

  // Get chemical by ID
  getChemicalById: async (id) => {
    try {
      const response = await api.get(`/chemicals/${id}`);
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] chemical ${id}:`, error);
      throw error;
    }
  },

  // Create new chemical
  createChemical: async (chemicalData) => {
    try {
      const response = await api.post('/chemicals', chemicalData);
      return response.data;
    } catch (error) {
      console.error('API Error [POST] chemicals:', error);
      throw error;
    }
  },

  // Update chemical
  updateChemical: async (id, chemicalData) => {
    try {
      const response = await api.put(`/chemicals/${id}`, chemicalData);
      return response.data;
    } catch (error) {
      console.error(`API Error [PUT] chemical ${id}:`, error);
      throw error;
    }
  },

  // Delete chemical
  deleteChemical: async (id) => {
    try {
      const response = await api.delete(`/chemicals/${id}`);
      return response.data;
    } catch (error) {
      console.error(`API Error [DELETE] chemical ${id}:`, error);
      throw error;
    }
  },

  // Search chemicals
  searchChemicals: async (query) => {
    try {
      const response = await api.get(`/chemicals/search?q=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] chemicals search ${query}:`, error);
      throw error;
    }
  },

  // Issue chemical
  issueChemical: async (id, data) => {
    try {
      const response = await api.post(`/chemicals/${id}/issue`, data);
      return response.data;
    } catch (error) {
      console.error(`API Error [POST] chemical ${id} issue:`, error);
      throw error;
    }
  },

  // Get chemical issuances
  getChemicalIssuances: async (id) => {
    try {
      const response = await api.get(`/chemicals/${id}/issuances`);
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] chemical ${id} issuances:`, error);
      throw error;
    }
  },

  // Get all issuances
  getAllIssuances: async (filters = {}) => {
    try {
      const response = await api.get('/chemicals/issuances', { params: filters });
      return response.data;
    } catch (error) {
      console.error('API Error [GET] all issuances:', error);
      throw error;
    }
  },

  // Archive a chemical
  archiveChemical: async (id, reason) => {
    try {
      const response = await api.post(`/chemicals/${id}/archive`, { reason });
      return response.data;
    } catch (error) {
      console.error(`API Error [POST] chemical ${id} archive:`, error);
      throw error;
    }
  },

  // Unarchive a chemical
  unarchiveChemical: async (id) => {
    try {
      const response = await api.post(`/chemicals/${id}/unarchive`);
      return response.data;
    } catch (error) {
      console.error(`API Error [POST] chemical ${id} unarchive:`, error);
      throw error;
    }
  },

  // Get archived chemicals
  getArchivedChemicals: async (filters = {}) => {
    try {
      const response = await api.get('/chemicals/archived', { params: filters });
      return response.data;
    } catch (error) {
      console.error('API Error [GET] archived chemicals:', error);
      throw error;
    }
  },

  // Get waste analytics
  getWasteAnalytics: async (timeframe = 'month', part_number = null) => {
    try {
      const params = { timeframe };
      if (part_number) params.part_number = part_number;

      const response = await api.get('/chemicals/analytics/waste', { params });
      return response.data;
    } catch (error) {
      console.error('API Error [GET] waste analytics:', error);
      throw error;
    }
  },

  // Get usage analytics
  getUsageAnalytics: async (part_number, timeframe = 'month') => {
    try {
      if (!part_number) {
        throw new Error('Part number is required');
      }

      const response = await api.get('/chemicals/analytics/usage', {
        params: { part_number, timeframe }
      });
      return response.data;
    } catch (error) {
      console.error('API Error [GET] usage analytics:', error);
      throw error;
    }
  },

  // Get part number analytics
  getPartNumberAnalytics: async (part_number) => {
    try {
      if (!part_number) {
        throw new Error('Part number is required');
      }

      const response = await api.get(`/chemicals/analytics/part-number/${encodeURIComponent(part_number)}`);
      return response.data;
    } catch (error) {
      console.error('API Error [GET] part number analytics:', error);
      throw error;
    }
  },

  // Get all unique part numbers
  getUniquePartNumbers: async () => {
    try {
      const response = await api.get('/chemicals/part-numbers');
      return response.data;
    } catch (error) {
      console.error('API Error [GET] unique part numbers:', error);
      throw error;
    }
  },

  // Get chemicals that need to be reordered
  getChemicalsNeedingReorder: async () => {
    try {
      const response = await api.get('/chemicals/reorder/needed');
      return response.data;
    } catch (error) {
      console.error('API Error [GET] chemicals needing reorder:', error);
      throw error;
    }
  },

  // Get chemicals that are on order
  getChemicalsOnOrder: async () => {
    try {
      const response = await api.get('/chemicals/reorder/on-order');
      return response.data;
    } catch (error) {
      console.error('API Error [GET] chemicals on order:', error);
      throw error;
    }
  },

  // Get chemicals that are expiring soon
  getChemicalsExpiringSoon: async (days = 30) => {
    try {
      const response = await api.get('/chemicals/expiring', { params: { days } });
      return response.data;
    } catch (error) {
      console.error('API Error [GET] chemicals expiring soon:', error);
      throw error;
    }
  },

  // Mark a chemical as ordered
  markChemicalAsOrdered: async (id, expectedDeliveryDate) => {
    try {
      const response = await api.post(`/chemicals/${id}/mark-ordered`, { expectedDeliveryDate });
      return response.data;
    } catch (error) {
      console.error(`API Error [POST] chemical ${id} mark ordered:`, error);
      throw error;
    }
  },

  // Mark a chemical as delivered
  markChemicalAsDelivered: async (id, receivedQuantity = null) => {
    try {
      const response = await api.post(`/chemicals/${id}/mark-delivered`, { receivedQuantity });
      return response.data;
    } catch (error) {
      console.error(`API Error [POST] chemical ${id} mark delivered:`, error);
      throw error;
    }
  }
};

export default ChemicalService;
