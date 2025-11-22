/**
 * Chart.js theme configuration for dark mode support
 * Provides consistent styling across all charts with better text contrast
 */

// Common chart options for dark theme compatibility
export const darkChartDefaults = {
  scales: {
    x: {
      ticks: {
        color: '#e0e0e0'
      },
      grid: {
        color: '#444'
      }
    },
    y: {
      ticks: {
        color: '#e0e0e0'
      },
      grid: {
        color: '#444'
      }
    }
  },
  plugins: {
    legend: {
      labels: {
        color: '#e0e0e0'
      }
    },
    tooltip: {
      backgroundColor: '#2c2c2c',
      borderColor: '#444',
      borderWidth: 1,
      titleColor: '#e0e0e0',
      bodyColor: '#e0e0e0'
    }
  }
};

/**
 * Merge custom options with dark theme defaults
 * @param {Object} customOptions - Custom chart options
 * @returns {Object} Merged options
 */
export const getChartOptions = (customOptions = {}) => {
  return {
    ...darkChartDefaults,
    ...customOptions,
    scales: {
      ...darkChartDefaults.scales,
      ...customOptions.scales
    },
    plugins: {
      ...darkChartDefaults.plugins,
      ...customOptions.plugins,
      legend: {
        ...darkChartDefaults.plugins.legend,
        ...customOptions.plugins?.legend
      },
      tooltip: {
        ...darkChartDefaults.plugins.tooltip,
        ...customOptions.plugins?.tooltip
      }
    }
  };
};
