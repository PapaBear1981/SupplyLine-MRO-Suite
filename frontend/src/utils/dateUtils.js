/**
 * Date formatting utility functions
 * 
 * This file provides standardized date formatting functions for use throughout the application.
 * Using these functions ensures consistent date display across all components.
 */

/**
 * Format a date string to a standard date and time format (MM/DD/YYYY hh:mm A)
 * 
 * @param {string|Date} dateString - The date to format
 * @param {boolean} includeTime - Whether to include time in the formatted string
 * @returns {string} Formatted date string or 'N/A' if date is invalid
 */
export const formatDateTime = (dateString, includeTime = true) => {
  if (!dateString) return 'N/A';
  
  try {
    const date = new Date(dateString);
    
    // Check if date is valid
    if (isNaN(date.getTime())) return 'N/A';
    
    const options = {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    };
    
    if (includeTime) {
      options.hour = '2-digit';
      options.minute = '2-digit';
      options.hour12 = true;
    }
    
    return date.toLocaleString('en-US', options);
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'N/A';
  }
};

/**
 * Format a date string to a standard date-only format (MM/DD/YYYY)
 * 
 * @param {string|Date} dateString - The date to format
 * @returns {string} Formatted date string or 'N/A' if date is invalid
 */
export const formatDate = (dateString) => {
  return formatDateTime(dateString, false);
};

/**
 * Format a date for chart display (MM/DD)
 * 
 * @param {string|Date} dateString - The date to format
 * @returns {string} Formatted date string for charts
 */
export const formatChartDate = (dateString) => {
  if (!dateString) return '';
  
  try {
    const date = new Date(dateString);
    
    // Check if date is valid
    if (isNaN(date.getTime())) return '';
    
    return date.toLocaleString('en-US', {
      month: '2-digit',
      day: '2-digit'
    });
  } catch (error) {
    console.error('Error formatting chart date:', error);
    return '';
  }
};

/**
 * Format a date for ISO format (YYYY-MM-DD)
 * Used primarily for input fields and API requests
 * 
 * @param {Date} date - The date object to format
 * @returns {string} ISO formatted date string
 */
export const formatISODate = (date) => {
  if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
    return '';
  }
  
  return date.toISOString().split('T')[0];
};

/**
 * Calculate the number of days between a date and today
 * 
 * @param {string|Date} dateString - The date to calculate days from
 * @returns {number|string} Number of days or 'N/A' if date is invalid
 */
export const getDaysFromToday = (dateString) => {
  if (!dateString) return 'N/A';
  
  try {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const date = new Date(dateString);
    date.setHours(0, 0, 0, 0);
    
    const diffTime = date - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays;
  } catch (error) {
    console.error('Error calculating days:', error);
    return 'N/A';
  }
};
