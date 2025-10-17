import api from './api';
// Removed legacy client-side export libraries - now using server-side export
import { formatISODate } from '../utils/dateUtils';

const ReportService = {
  // Fetch tool inventory report
  getToolInventoryReport: async (filters = {}) => {
    try {
      const response = await api.get('/reports/tools', { params: filters });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Fetch checkout history report
  getCheckoutHistoryReport: async (timeframe = 'month', filters = {}) => {
    try {
      const response = await api.get('/reports/checkouts', {
        params: { timeframe, ...filters }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Fetch department usage report
  getDepartmentUsageReport: async (timeframe = 'month') => {
    try {
      const response = await api.get('/reports/departments', {
        params: { timeframe }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Export report as PDF
  exportAsPdf: async (reportData, reportType, timeframe) => {
    try {
      const response = await api.post('/reports/export/pdf', {
        report_type: reportType,
        report_data: reportData,
        timeframe: timeframe
      }, {
        responseType: 'blob'
      });

      // Create blob and download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${reportType}-report-${formatISODate(new Date())}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('PDF export error:', error);
      throw new Error('Failed to export PDF: ' + (error.response?.data?.error || error.message));
    }
  },

  // Export report as Excel
  exportAsExcel: async (reportData, reportType, timeframe) => {
    try {
      const response = await api.post('/reports/export/excel', {
        report_type: reportType,
        report_data: reportData,
        timeframe: timeframe
      }, {
        responseType: 'blob'
      });

      // Create blob and download
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${reportType}-report-${formatISODate(new Date())}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Excel export error:', error);
      throw new Error('Failed to export Excel: ' + (error.response?.data?.error || error.message));
    }
  }
};

// Legacy helper functions removed - export functionality moved to server-side

export default ReportService;
