import api from './api';

const ChemicalService = {
  // Get all chemicals
  getAllChemicals: async () => {
    try {
      const response = await api.get('/chemicals');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get chemical by ID
  getChemicalById: async (id) => {
    try {
      const response = await api.get(`/chemicals/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Create new chemical
  createChemical: async (chemicalData) => {
    try {
      const response = await api.post('/chemicals', chemicalData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update chemical
  updateChemical: async (id, chemicalData) => {
    try {
      const response = await api.put(`/chemicals/${id}`, chemicalData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Delete chemical
  deleteChemical: async (id) => {
    try {
      const response = await api.delete(`/chemicals/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Search chemicals
  searchChemicals: async (query) => {
    try {
      const response = await api.get(`/chemicals?q=${query}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Issue chemical
  issueChemical: async (id, data) => {
    try {
      const response = await api.post(`/chemicals/${id}/issue`, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get chemical issuances
  getChemicalIssuances: async (id) => {
    try {
      const response = await api.get(`/chemicals/${id}/issuances`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get all issuances
  getAllIssuances: async (filters = {}) => {
    try {
      const response = await api.get('/issuances', { params: filters });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Archive a chemical
  archiveChemical: async (id, reason) => {
    try {
      const response = await api.post(`/chemicals/${id}/archive`, { reason });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Unarchive a chemical
  unarchiveChemical: async (id) => {
    try {
      const response = await api.post(`/chemicals/${id}/unarchive`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get archived chemicals
  getArchivedChemicals: async (filters = {}) => {
    try {
      const response = await api.get('/chemicals/archived', { params: filters });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get waste analytics
  getWasteAnalytics: async (timeframe = 'month', part_number = null) => {
    try {
      const params = { timeframe };
      if (part_number) {
        params.part_number = part_number;
      }

      const response = await api.get('/chemicals/waste-analytics', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get part number analytics
  getPartNumberAnalytics: async (part_number) => {
    try {
      if (!part_number) {
        throw new Error('Part number is required');
      }

      const response = await api.get('/chemicals/part-analytics', {
        params: { part_number }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get all unique part numbers
  getUniquePartNumbers: async () => {
    try {
      // Get all chemicals and extract unique part numbers
      const chemicals = await ChemicalService.getAllChemicals();
      const partNumbers = [...new Set(chemicals.map(c => c.part_number))];
      return partNumbers.sort();
    } catch (error) {
      throw error;
    }
  }
};

export default ChemicalService;
