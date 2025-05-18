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

  // Checkout a tool for the current user
  checkoutTool: async (toolId, expectedReturnDate) => {
    try {
      console.log('Checking out tool:', { toolId, expectedReturnDate });

      // Simplified approach - let the backend handle user identification from session
      const requestData = {
        tool_id: toolId,
        expected_return_date: expectedReturnDate
      };
      console.log('Sending checkout request with data:', requestData);

      const response = await api.post('/checkouts', requestData);
      console.log('Checkout response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Checkout error details:', error.response?.data || error.message);
      throw error;
    }
  },

  // Checkout a tool to another user
  checkoutToolToUser: async (toolId, userId, expectedReturnDate) => {
    try {
      const response = await api.post('/checkouts', {
        tool_id: toolId,
        user_id: userId,
        expected_return_date: expectedReturnDate
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Return a tool
  returnTool: async (returnData) => {
    try {
      const { checkoutId, condition, returned_by, found, notes } = returnData;
      const response = await api.put(`/checkouts/${checkoutId}/return`, {
        condition,
        returned_by,
        found,
        notes
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
