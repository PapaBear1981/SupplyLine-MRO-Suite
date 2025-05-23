import api from './api';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { formatDate, formatISODate } from '../utils/dateUtils';

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

// Helper functions
const getReportTitle = (reportType, timeframe) => {
  let title = '';

  switch (reportType) {
    case 'tool-inventory':
      title = 'Tool Inventory Report';
      break;
    case 'checkout-history':
      title = 'Checkout History Report';
      break;
    case 'department-usage':
      title = 'Department Usage Report';
      break;
    default:
      title = 'Report';
  }

  if (timeframe) {
    const timeframeText = timeframe.charAt(0).toUpperCase() + timeframe.slice(1);
    title += ` (${timeframeText})`;
  }

  return title;
};

// PDF export helpers
const exportToolInventoryPdf = (doc, data) => {
  const tableColumn = ['Tool #', 'Serial #', 'Description', 'Category', 'Location', 'Status'];
  const tableRows = data.map(tool => [
    tool.tool_number,
    tool.serial_number,
    tool.description || 'N/A',
    tool.category || 'General',
    tool.location || 'N/A',
    tool.status || 'Available'
  ]);

  doc.autoTable({
    head: [tableColumn],
    body: tableRows,
    startY: 40,
    styles: { fontSize: 10 },
    headStyles: { fillColor: [66, 66, 66] }
  });
};

const exportCheckoutHistoryPdf = (doc, data) => {
  const tableColumn = ['Tool #', 'User', 'Checkout Date', 'Return Date', 'Duration (Days)'];
  const tableRows = data.checkouts.map(checkout => [
    checkout.tool_number,
    checkout.user_name,
    formatDate(checkout.checkout_date),
    checkout.return_date ? formatDate(checkout.return_date) : 'Not Returned',
    checkout.duration || 'N/A'
  ]);

  // Add summary statistics
  doc.setFontSize(12);
  doc.text('Summary Statistics:', 14, 40);
  doc.setFontSize(10);
  doc.text(`Total Checkouts: ${data.stats.totalCheckouts}`, 14, 48);
  doc.text(`Average Checkout Duration: ${data.stats.averageDuration} days`, 14, 54);
  doc.text(`Currently Checked Out: ${data.stats.currentlyCheckedOut}`, 14, 60);

  doc.autoTable({
    head: [tableColumn],
    body: tableRows,
    startY: 70,
    styles: { fontSize: 10 },
    headStyles: { fillColor: [66, 66, 66] }
  });
};

const exportDepartmentUsagePdf = (doc, data) => {
  const tableColumn = ['Department', 'Total Checkouts', 'Average Duration (Days)', 'Currently Checked Out'];
  const tableRows = data.departments.map(dept => [
    dept.name,
    dept.totalCheckouts,
    dept.averageDuration,
    dept.currentlyCheckedOut
  ]);

  doc.autoTable({
    head: [tableColumn],
    body: tableRows,
    startY: 40,
    styles: { fontSize: 10 },
    headStyles: { fillColor: [66, 66, 66] }
  });
};

// Excel export helpers
const formatToolInventoryForExcel = (data) => {
  return data.map(tool => ({
    'Tool Number': tool.tool_number,
    'Serial Number': tool.serial_number,
    'Description': tool.description || 'N/A',
    'Category': tool.category || 'General',
    'Location': tool.location || 'N/A',
    'Status': tool.status || 'Available',
    'Condition': tool.condition || 'N/A'
  }));
};

const formatCheckoutHistoryForExcel = (data) => {
  return data.checkouts.map(checkout => ({
    'Tool Number': checkout.tool_number,
    'Serial Number': checkout.serial_number || 'N/A',
    'Description': checkout.description || 'N/A',
    'User': checkout.user_name,
    'Checkout Date': formatDate(checkout.checkout_date),
    'Return Date': checkout.return_date ? formatDate(checkout.return_date) : 'Not Returned',
    'Duration (Days)': checkout.duration || 'N/A'
  }));
};

const formatDepartmentUsageForExcel = (data) => {
  return data.departments.map(dept => ({
    'Department': dept.name,
    'Total Checkouts': dept.totalCheckouts,
    'Average Duration (Days)': dept.averageDuration,
    'Currently Checked Out': dept.currentlyCheckedOut,
    'Most Used Tool': dept.mostUsedTool || 'N/A'
  }));
};

export default ReportService;
