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
    try {
      // Create a new PDF document with default settings
      const doc = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      // Get title and format date for display
      const title = getReportTitle(reportType, timeframe);
      const displayDate = new Date().toLocaleDateString();

      // Format date for filename (remove slashes and other special characters)
      const fileDate = new Date().toISOString().split('T')[0];

      // Add title and date to the PDF
      doc.setFontSize(18);
      doc.text(title, 14, 22);
      doc.setFontSize(11);
      doc.text(`Generated on: ${displayDate}`, 14, 30);

      // Add report data based on report type
      if (reportType === 'tool-inventory') {
        exportToolInventoryPdf(doc, reportData);
      } else if (reportType === 'checkout-history') {
        exportCheckoutHistoryPdf(doc, reportData);
      } else if (reportType === 'department-usage') {
        exportDepartmentUsagePdf(doc, reportData);
      } else if (reportType === 'calibration') {
        exportCalibrationReportDataToPdf(doc, reportData, timeframe);
      }

      // Output the PDF as a blob and save it
      const pdfBlob = doc.output('blob');
      saveAs(pdfBlob, `${reportType}-report-${fileDate}.pdf`);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF. Please try again.');
    }
  },

  // Export calibration report as PDF
  exportCalibrationReportPdf: (reportData, reportType, dateRange) => {
    try {
      // Create a new PDF document with default settings
      const doc = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      // Get title and format date for display
      const title = getCalibrationReportTitle(reportType, dateRange);
      const displayDate = new Date().toLocaleDateString();

      // Format date for filename (remove slashes and other special characters)
      const fileDate = new Date().toISOString().split('T')[0];

      // Add title and date to the PDF
      doc.setFontSize(18);
      doc.text(title, 14, 22);
      doc.setFontSize(11);
      doc.text(`Generated on: ${displayDate}`, 14, 30);

      // Add calibration report data based on report type
      exportCalibrationReportDataToPdf(doc, reportData, reportType);

      // Output the PDF as a blob and save it
      const pdfBlob = doc.output('blob');
      saveAs(pdfBlob, `calibration-${reportType}-report-${fileDate}.pdf`);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF. Please try again.');
    }
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
    } else if (reportType === 'calibration') {
      worksheet = XLSX.utils.json_to_sheet(formatCalibrationReportForExcel(reportData, timeframe));
    }

    // Create workbook and add worksheet
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, title);

    // Generate Excel file and save
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    saveAs(blob, `${reportType}-report-${date}.xlsx`);
  },

  // Export calibration report as Excel
  exportCalibrationReportAsExcel: (reportData, reportType, dateRange) => {
    try {
      const title = getCalibrationReportTitle(reportType, dateRange);
      const date = new Date().toLocaleDateString();

      // Create worksheet from calibration data
      const worksheet = XLSX.utils.json_to_sheet(formatCalibrationReportForExcel(reportData, reportType));

      // Create workbook and add worksheet
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, title);

      // Generate Excel file and save
      const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
      const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      saveAs(blob, `calibration-${reportType}-report-${date}.xlsx`);
    } catch (error) {
      console.error('Error generating Excel:', error);
      alert('Failed to generate Excel file. Please try again.');
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
    case 'calibration':
      title = 'Calibration Report';
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

// Get calibration report title based on report type and date range
const getCalibrationReportTitle = (reportType, dateRange) => {
  let title = '';

  switch (reportType) {
    case 'due':
      title = `Calibrations Due in the Next ${dateRange} Days`;
      break;
    case 'overdue':
      title = 'Overdue Calibrations';
      break;
    case 'history':
      title = 'Calibration History';
      break;
    case 'compliance':
      title = 'Calibration Compliance';
      break;
    default:
      title = 'Calibration Report';
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

// Export calibration report data to PDF
const exportCalibrationReportDataToPdf = (doc, data, reportType) => {
  try {
    // Validate input data
    if (!data || !Array.isArray(data) || data.length === 0) {
      doc.setTextColor(255, 0, 0);
      doc.setFontSize(12);
      doc.text('No data available for this report.', 14, 40);
      doc.setTextColor(0, 0, 0);
      return;
    }

    let tableColumn = [];
    let tableRows = [];

    // Define columns based on report type
    if (reportType === 'due' || reportType === 'overdue') {
      tableColumn = ['Tool #', 'Serial #', 'Description', 'Last Calibration', 'Next Due Date', 'Days Remaining'];

      tableRows = data.map(item => {
        // Calculate days remaining
        let daysRemaining = 'N/A';
        if (item.next_calibration_date) {
          const nextDueDate = new Date(item.next_calibration_date);
          const today = new Date();

          // Reset time part to compare just the dates
          nextDueDate.setHours(0, 0, 0, 0);
          today.setHours(0, 0, 0, 0);

          // Calculate the difference in days
          const diffTime = nextDueDate.getTime() - today.getTime();
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

          if (diffDays < 0) {
            daysRemaining = 'Overdue';
          } else {
            daysRemaining = diffDays.toString();
          }
        }

        return [
          item.tool_number || 'N/A',
          item.serial_number || 'N/A',
          (item.description || 'N/A').toString().substring(0, 30), // Limit description length
          item.last_calibration_date
            ? new Date(item.last_calibration_date).toLocaleDateString()
            : 'Never',
          item.next_calibration_date
            ? new Date(item.next_calibration_date).toLocaleDateString()
            : 'N/A',
          daysRemaining
        ];
      });
    } else if (reportType === 'history') {
      tableColumn = ['Tool #', 'Serial #', 'Description', 'Calibration Date', 'Next Due Date', 'Performed By', 'Status'];

      tableRows = data.map(item => [
        item.tool_number || 'N/A',
        item.serial_number || 'N/A',
        (item.description || 'N/A').toString().substring(0, 30), // Limit description length
        item.calibration_date
          ? new Date(item.calibration_date).toLocaleDateString()
          : 'N/A',
        item.next_calibration_date
          ? new Date(item.next_calibration_date).toLocaleDateString()
          : 'N/A',
        item.performed_by || 'N/A',
        item.calibration_status === 'completed' ? 'Completed' :
        item.calibration_status === 'failed' ? 'Failed' : 'In Progress'
      ]);
    } else if (reportType === 'compliance') {
      tableColumn = ['Tool #', 'Serial #', 'Description', 'Last Calibration', 'Next Due Date', 'Status'];

      tableRows = data.map(item => [
        item.tool_number || 'N/A',
        item.serial_number || 'N/A',
        (item.description || 'N/A').toString().substring(0, 30), // Limit description length
        item.last_calibration_date
          ? new Date(item.last_calibration_date).toLocaleDateString()
          : 'Never',
        item.next_calibration_date
          ? new Date(item.next_calibration_date).toLocaleDateString()
          : 'N/A',
        item.calibration_status === 'current' ? 'Current' :
        item.calibration_status === 'due_soon' ? 'Due Soon' :
        item.calibration_status === 'overdue' ? 'Overdue' : 'N/A'
      ]);
    } else {
      // Default columns for any other report type
      tableColumn = ['Tool #', 'Serial #', 'Description', 'Next Due Date'];

      tableRows = data.map(item => [
        item.tool_number || 'N/A',
        item.serial_number || 'N/A',
        (item.description || 'N/A').toString().substring(0, 30), // Limit description length
        item.next_calibration_date
          ? new Date(item.next_calibration_date).toLocaleDateString()
          : 'N/A'
      ]);
    }

    // Add the table to the PDF with proper configuration
    doc.autoTable({
      head: [tableColumn],
      body: tableRows,
      startY: 40,
      styles: {
        fontSize: 10,
        cellPadding: 2,
        overflow: 'linebreak'
      },
      headStyles: {
        fillColor: [66, 66, 66],
        textColor: [255, 255, 255],
        fontStyle: 'bold'
      },
      margin: { top: 40, right: 14, bottom: 20, left: 14 },
      didDrawPage: function(data) {
        // Add page number at the bottom
        doc.setFontSize(8);
        doc.text(
          'Page ' + doc.internal.getCurrentPageInfo().pageNumber,
          data.settings.margin.left,
          doc.internal.pageSize.height - 10
        );
      }
    });

    // Add footer with generation info
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(100, 100, 100);
      doc.text(
        `Generated by SupplyLine MRO Suite on ${new Date().toLocaleString()}`,
        doc.internal.pageSize.width / 2,
        doc.internal.pageSize.height - 5,
        { align: 'center' }
      );
    }

  } catch (error) {
    console.error('Error generating PDF table:', error);
    // Add error message to PDF
    doc.setTextColor(255, 0, 0);
    doc.setFontSize(12);
    doc.text('Error generating report table. Please try again.', 14, 40);
    doc.setTextColor(0, 0, 0);
  }
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

// Format calibration report data for Excel
const formatCalibrationReportForExcel = (data, reportType) => {
  try {
    if (!data || !Array.isArray(data) || data.length === 0) {
      return [{ 'Error': 'No data available for export' }];
    }

    if (reportType === 'due' || reportType === 'overdue') {
      return data.map(item => {
        // Calculate days remaining
        let daysRemaining = 'N/A';
        if (item.next_calibration_date) {
          const nextDueDate = new Date(item.next_calibration_date);
          const today = new Date();

          // Reset time part to compare just the dates
          nextDueDate.setHours(0, 0, 0, 0);
          today.setHours(0, 0, 0, 0);

          // Calculate the difference in days
          const diffTime = nextDueDate.getTime() - today.getTime();
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

          if (diffDays < 0) {
            daysRemaining = 'Overdue';
          } else {
            daysRemaining = diffDays.toString();
          }
        }

        return {
          'Tool Number': item.tool_number || 'N/A',
          'Serial Number': item.serial_number || 'N/A',
          'Description': item.description || 'N/A',
          'Last Calibration': item.last_calibration_date
            ? new Date(item.last_calibration_date).toLocaleDateString()
            : 'Never',
          'Next Due Date': item.next_calibration_date
            ? new Date(item.next_calibration_date).toLocaleDateString()
            : 'N/A',
          'Days Remaining': daysRemaining,
          'Location': item.location || 'N/A',
          'Category': item.category || 'General'
        };
      });
    } else if (reportType === 'history') {
      return data.map(item => ({
        'Tool Number': item.tool_number || 'N/A',
        'Serial Number': item.serial_number || 'N/A',
        'Description': item.description || 'N/A',
        'Calibration Date': item.calibration_date
          ? new Date(item.calibration_date).toLocaleDateString()
          : 'N/A',
        'Next Due Date': item.next_calibration_date
          ? new Date(item.next_calibration_date).toLocaleDateString()
          : 'N/A',
        'Performed By': item.performed_by || 'N/A',
        'Status': item.calibration_status === 'completed' ? 'Completed' :
                  item.calibration_status === 'failed' ? 'Failed' : 'In Progress',
        'Notes': item.calibration_notes || ''
      }));
    } else if (reportType === 'compliance') {
      return data.map(item => ({
        'Tool Number': item.tool_number || 'N/A',
        'Serial Number': item.serial_number || 'N/A',
        'Description': item.description || 'N/A',
        'Last Calibration': item.last_calibration_date
          ? new Date(item.last_calibration_date).toLocaleDateString()
          : 'Never',
        'Next Due Date': item.next_calibration_date
          ? new Date(item.next_calibration_date).toLocaleDateString()
          : 'N/A',
        'Status': item.calibration_status === 'current' ? 'Current' :
                  item.calibration_status === 'due_soon' ? 'Due Soon' :
                  item.calibration_status === 'overdue' ? 'Overdue' : 'N/A',
        'Location': item.location || 'N/A',
        'Category': item.category || 'General'
      }));
    } else {
      // Default format
      return data.map(item => ({
        'Tool Number': item.tool_number || 'N/A',
        'Serial Number': item.serial_number || 'N/A',
        'Description': item.description || 'N/A',
        'Next Due Date': item.next_calibration_date
          ? new Date(item.next_calibration_date).toLocaleDateString()
          : 'N/A'
      }));
    }
  } catch (error) {
    console.error('Error formatting Excel data:', error);
    return [{ 'Error': 'Failed to format data for Excel export' }];
  }
};

export default ReportService;
