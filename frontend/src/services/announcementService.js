import api from './api';

const AnnouncementService = {
  // Get all announcements with pagination and filters
  getAllAnnouncements: async (page = 1, limit = 10, filters = {}) => {
    try {
      // Validate pagination parameters
      if (!Number.isInteger(page) || page < 1) page = 1;
      if (!Number.isInteger(limit) || limit < 1) limit = 10;

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
      if (!id) {
        throw new Error('Announcement ID is required');
      }
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
      // Validate required fields
      if (!announcementData || !announcementData.title || !announcementData.content) {
        throw new Error('Announcement title and content are required');
      }
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
      if (!id) {
        throw new Error('Announcement ID is required');
      }
      if (!announcementData || !announcementData.title || !announcementData.content) {
        throw new Error('Announcement title and content are required');
      }
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
      if (!id) {
        throw new Error('Announcement ID is required');
      }
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
      if (!id) {
        throw new Error('Announcement ID is required');
      }
      const response = await api.post(`/announcements/${id}/read`);
      return response.data;
    } catch (error) {
      console.error(`API Error [POST] /announcements/${id}/read:`, error);
      throw error;
    }
  }
};

export default AnnouncementService;
