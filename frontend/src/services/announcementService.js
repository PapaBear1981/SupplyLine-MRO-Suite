import api from './api';

const AnnouncementService = {
  // Get all announcements with pagination and filters
  getAllAnnouncements: async (page = 1, limit = 10, filters = {}) => {
    try {
      const params = new URLSearchParams();
      params.append('page', page);
      params.append('limit', limit);
      
      // Add any filters
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value);
        }
      });
      
      const response = await api.get(`/announcements?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('API Error [GET] /announcements:', error);
      throw error;
    }
  },
  
  // Get announcement by ID
  getAnnouncementById: async (id) => {
    try {
      const response = await api.get(`/announcements/${id}`);
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] /announcements/${id}:`, error);
      throw error;
    }
  },
  
  // Create new announcement (admin only)
  createAnnouncement: async (announcementData) => {
    try {
      const response = await api.post('/announcements', announcementData);
      return response.data;
    } catch (error) {
      console.error('API Error [POST] /announcements:', error);
      throw error;
    }
  },
  
  // Update announcement (admin only)
  updateAnnouncement: async (id, announcementData) => {
    try {
      const response = await api.put(`/announcements/${id}`, announcementData);
      return response.data;
    } catch (error) {
      console.error(`API Error [PUT] /announcements/${id}:`, error);
      throw error;
    }
  },
  
  // Delete announcement (admin only)
  deleteAnnouncement: async (id) => {
    try {
      const response = await api.delete(`/announcements/${id}`);
      return response.data;
    } catch (error) {
      console.error(`API Error [DELETE] /announcements/${id}:`, error);
      throw error;
    }
  },
  
  // Mark announcement as read
  markAsRead: async (id) => {
    try {
      const response = await api.post(`/announcements/${id}/read`);
      return response.data;
    } catch (error) {
      console.error(`API Error [POST] /announcements/${id}/read:`, error);
      throw error;
    }
  }
};

export default AnnouncementService;
