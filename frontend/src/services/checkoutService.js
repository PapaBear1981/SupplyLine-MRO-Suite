import api from './api';

const CheckoutService = {
  // Get all checkouts
  getAllCheckouts: async () => {
    try {
      const response = await api.get('/checkouts');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get checkout by ID
  getCheckoutById: async (id) => {
    try {
      const response = await api.get(`/checkouts/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get user's checkouts
  getUserCheckouts: async () => {
    try {
      const response = await api.get('/checkouts/user');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Checkout a tool
  checkoutTool: async (toolId, expectedReturnDate) => {
    try {
      const response = await api.post('/checkouts', {
        tool_id: toolId,
        expected_return_date: expectedReturnDate
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Return a tool
  returnTool: async (checkoutId, condition) => {
    try {
      const response = await api.put(`/checkouts/${checkoutId}/return`, {
        condition: condition
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get checkout history for a tool
  getToolCheckoutHistory: async (toolId) => {
    try {
      const response = await api.get(`/tools/${toolId}/checkouts`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default CheckoutService;
