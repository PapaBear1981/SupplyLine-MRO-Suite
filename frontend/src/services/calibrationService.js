import api from './api';

const CalibrationService = {
  // Get all calibrations with pagination and filters
  getAllCalibrations: async (page = 1, limit = 20, filters = {}) => {
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
      
      const response = await api.get(`/calibrations?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Get tools due for calibration
  getCalibrationsDue: async (days = 30) => {
    try {
      const response = await api.get(`/calibrations/due?days=${days}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Get tools overdue for calibration
  getOverdueCalibrations: async () => {
    try {
      const response = await api.get('/calibrations/overdue');
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Get calibration history for a specific tool
  getToolCalibrations: async (toolId, page = 1, limit = 20) => {
    try {
      const response = await api.get(`/tools/${toolId}/calibrations?page=${page}&limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Add a new calibration record for a tool
  addCalibration: async (toolId, calibrationData) => {
    try {
      const response = await api.post(`/tools/${toolId}/calibrations`, calibrationData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Get all calibration standards
  getAllCalibrationStandards: async (page = 1, limit = 20, filters = {}) => {
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
      
      const response = await api.get(`/calibration-standards?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Get a specific calibration standard
  getCalibrationStandard: async (id) => {
    try {
      const response = await api.get(`/calibration-standards/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Add a new calibration standard
  addCalibrationStandard: async (standardData) => {
    try {
      const response = await api.post('/calibration-standards', standardData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Update a calibration standard
  updateCalibrationStandard: async (id, standardData) => {
    try {
      const response = await api.put(`/calibration-standards/${id}`, standardData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default CalibrationService;
