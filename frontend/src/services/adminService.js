import api from './api';

const AdminService = {
  // Get admin dashboard statistics
  getDashboardStats: async () => {
    try {
      const response = await api.get('/admin/dashboard/stats');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get system resources information
  getSystemResources: async () => {
    try {
      const response = await api.get('/admin/system-resources');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get registration requests
  getRegistrationRequests: async (status = 'pending') => {
    try {
      const response = await api.get('/admin/registration-requests', {
        params: { status }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Approve registration request
  approveRegistrationRequest: async (requestId, adminNotes = '') => {
    try {
      const response = await api.post(`/admin/registration-requests/${requestId}/approve`, {
        admin_notes: adminNotes
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Deny registration request
  denyRegistrationRequest: async (requestId, adminNotes = '') => {
    try {
      const response = await api.post(`/admin/registration-requests/${requestId}/deny`, {
        admin_notes: adminNotes
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Test admin dashboard connection
  testDashboardConnection: async () => {
    try {
      const response = await api.get('/admin/dashboard/test');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default AdminService;
