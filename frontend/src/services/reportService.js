import api from './api';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

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
  exportAsPdf: (reportData, reportType, timeframe) => {
    const doc = new jsPDF();
    const title = getReportTitle(reportType, timeframe);
    const date = new Date().toLocaleDateString();
    
    // Add title and date
    doc.setFontSize(18);
    doc.text(title, 14, 22);
    doc.setFontSize(11);
    doc.text(`Generated on: ${date}`, 14, 30);
    
    // Add report data based on report type
    if (reportType === 'tool-inventory') {
      exportToolInventoryPdf(doc, reportData);
    } else if (reportType === 'checkout-history') {
      exportCheckoutHistoryPdf(doc, reportData);
    } else if (reportType === 'department-usage') {
      exportDepartmentUsagePdf(doc, reportData);
    }
    
    // Save the PDF
    doc.save(`${reportType}-report-${date}.pdf`);
  },

  // Export report as Excel
  exportAsExcel: (reportData, reportType, timeframe) => {
    const title = getReportTitle(reportType, timeframe);
    const date = new Date().toLocaleDateString();
    let worksheet;
    
    // Create worksheet based on report type
    if (reportType === 'tool-inventory') {
      worksheet = XLSX.utils.json_to_sheet(formatToolInventoryForExcel(reportData));
    } else if (reportType === 'checkout-history') {
      worksheet = XLSX.utils.json_to_sheet(formatCheckoutHistoryForExcel(reportData));
    } else if (reportType === 'department-usage') {
      worksheet = XLSX.utils.json_to_sheet(formatDepartmentUsageForExcel(reportData));
    }
    
    // Create workbook and add worksheet
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, title);
    
    // Generate Excel file and save
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    saveAs(blob, `${reportType}-report-${date}.xlsx`);
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
    new Date(checkout.checkout_date).toLocaleDateString(),
    checkout.return_date ? new Date(checkout.return_date).toLocaleDateString() : 'Not Returned',
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
    'Checkout Date': new Date(checkout.checkout_date).toLocaleDateString(),
    'Return Date': checkout.return_date ? new Date(checkout.return_date).toLocaleDateString() : 'Not Returned',
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
