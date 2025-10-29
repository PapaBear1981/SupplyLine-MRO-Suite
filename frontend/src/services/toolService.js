import api from './api';

const ToolService = {
  // Get all tools
  getAllTools: async () => {
    try {
      // Fetch all tools by handling pagination
      let allTools = [];
      let page = 1;
      let hasMore = true;
      const perPage = 500; // Maximum allowed by backend

      while (hasMore) {
        const response = await api.get(`/tools?page=${page}&per_page=${perPage}`);
        const data = response.data;

        // Handle both array response and paginated response
        if (Array.isArray(data)) {
          allTools = allTools.concat(data);
          hasMore = false; // No pagination info, assume single page
        } else if (data.tools) {
          allTools = allTools.concat(data.tools);
          hasMore = data.pagination && data.pagination.has_next;
          page++;
        } else {
          hasMore = false;
        }
      }

      console.log(`Fetched ${allTools.length} total tools across ${page} page(s)`);

      // Return in the same format as backend (with tools array)
      return {
        tools: allTools,
        pagination: {
          total: allTools.length,
          page: 1,
          per_page: allTools.length,
          pages: 1,
          has_next: false,
          has_prev: false
        }
      };
    } catch (error) {
      throw error;
    }
  },

  // Get tool by ID
  getToolById: async (id) => {
    try {
      // Ensure id is a number
      const toolId = typeof id === 'string' ? parseInt(id, 10) : id;
      const response = await api.get(`/tools/${toolId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Create new tool
  createTool: async (toolData) => {
    try {
      console.log('Creating new tool with data:', toolData);
      const response = await api.post('/tools', toolData);
      console.log('Tool creation response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error creating tool:', error.response?.data || error.message);
      throw error.response?.data || error;
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
