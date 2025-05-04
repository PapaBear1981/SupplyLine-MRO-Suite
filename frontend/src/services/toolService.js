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
      const response = await api.put(`/tools/${id}`, toolData);
      return response.data;
    } catch (error) {
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
  }
};

export default ToolService;
