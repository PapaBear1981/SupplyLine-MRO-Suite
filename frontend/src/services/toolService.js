import api from './api';

const ToolService = {
  // Get all tools
  getAllTools: async () => {
    try {
      const response = await api.get('/tools');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get tool by ID
  getToolById: async (id) => {
    try {
      const response = await api.get(`/tools/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Create new tool
  createTool: async (toolData) => {
    try {
      const response = await api.post('/tools', toolData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update tool
  updateTool: async (id, toolData) => {
    try {
      console.log('Sending tool update request:', { id, toolData });
      const response = await api.put(`/tools/${id}`, toolData);
      console.log('Tool update response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error updating tool:', error);
      throw error;
    }
  },

  // Delete tool
  deleteTool: async (id) => {
    try {
      const response = await api.delete(`/tools/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Search tools
  searchTools: async (query) => {
    try {
      const response = await api.get(`/tools?q=${query}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Remove tool from service (temporarily or permanently)
  removeFromService: async (id, data) => {
    try {
      const response = await api.post(`/tools/${id}/service/remove`, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Return tool to service
  returnToService: async (id, data) => {
    try {
      const response = await api.post(`/tools/${id}/service/return`, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get tool service history
  getServiceHistory: async (id, page = 1, limit = 20) => {
    try {
      const response = await api.get(`/tools/${id}/service/history?page=${page}&limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default ToolService;
