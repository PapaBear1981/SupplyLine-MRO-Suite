/**
 * Test data fixtures for E2E tests
 */

export const testUsers = {
  admin: {
    employee_number: 'ADMIN001',
    password: 'admin123',
    name: 'Admin User',
    department: 'IT',
    is_admin: true
  },
  regularUser: {
    employee_number: 'USER001',
    password: 'user123',
    name: 'Regular User',
    department: 'Production',
    is_admin: false
  },
  materialsUser: {
    employee_number: 'MAT001',
    password: 'materials123',
    name: 'Materials User',
    department: 'Materials',
    is_admin: false
  }
};

export const testTools = {
  basicTool: {
    tool_number: 'TEST001',
    serial_number: 'SN001',
    description: 'Test Tool for E2E Testing',
    category: 'Testing',
    condition: 'Good',
    location: 'Test Storage',
    status: 'available'
  },
  calibrationTool: {
    tool_number: 'CAL001',
    serial_number: 'CAL001',
    description: 'Calibration Test Tool',
    category: 'Measurement',
    condition: 'Good',
    location: 'Calibration Lab',
    status: 'available',
    requires_calibration: true,
    calibration_frequency: 365
  },
  expensiveTool: {
    tool_number: 'EXP001',
    serial_number: 'EXP001',
    description: 'Expensive Test Tool',
    category: 'Precision',
    condition: 'Excellent',
    location: 'Secure Storage',
    status: 'available',
    cost: 5000.00
  }
};

export const testChemicals = {
  basicChemical: {
    part_number: 'CHEM001',
    description: 'Test Chemical for E2E Testing',
    category: 'Solvent',
    quantity: 100.0,
    unit: 'ml',
    location: 'Chemical Storage',
    status: 'available',
    safety_data_sheet: 'test-sds.pdf'
  },
  expiringChemical: {
    part_number: 'CHEM002',
    description: 'Expiring Test Chemical',
    category: 'Acid',
    quantity: 50.0,
    unit: 'ml',
    location: 'Chemical Storage',
    status: 'available',
    expiration_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] // 30 days from now
  },
  lowStockChemical: {
    part_number: 'CHEM003',
    description: 'Low Stock Test Chemical',
    category: 'Base',
    quantity: 5.0,
    unit: 'ml',
    location: 'Chemical Storage',
    status: 'available',
    minimum_quantity: 10.0
  }
};

export const testCycleCountSchedules = {
  weeklySchedule: {
    name: 'Weekly Test Schedule',
    frequency: 'weekly',
    method: 'ABC',
    is_active: true,
    description: 'Test schedule for E2E testing'
  },
  monthlySchedule: {
    name: 'Monthly Test Schedule',
    frequency: 'monthly',
    method: 'random',
    is_active: true,
    description: 'Monthly test schedule for E2E testing'
  }
};

export const testCalibrationStandards = {
  basicStandard: {
    name: 'Test Calibration Standard',
    description: 'Standard for E2E testing',
    certificate_number: 'CERT001',
    accuracy: '±0.1%',
    calibration_date: new Date().toISOString().split('T')[0],
    expiration_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] // 1 year from now
  }
};

export const testFormData = {
  toolForm: {
    valid: {
      tool_number: 'FORM001',
      serial_number: 'FORM001',
      description: 'Form Test Tool',
      category: 'Testing',
      condition: 'Good',
      location: 'Test Area'
    },
    invalid: {
      tool_number: '', // Required field empty
      serial_number: 'INVALID',
      description: 'Invalid Tool',
      category: 'Testing',
      condition: 'Good',
      location: 'Test Area'
    }
  },
  chemicalForm: {
    valid: {
      part_number: 'FORMCHEM001',
      description: 'Form Test Chemical',
      category: 'Testing',
      quantity: '100',
      unit: 'ml',
      location: 'Test Storage'
    },
    invalid: {
      part_number: '', // Required field empty
      description: 'Invalid Chemical',
      category: 'Testing',
      quantity: '-10', // Invalid quantity
      unit: 'ml',
      location: 'Test Storage'
    }
  }
};

export const apiEndpoints = {
  auth: {
    login: '/api/auth/login',
    logout: '/api/auth/logout',
    register: '/api/auth/register'
  },
  tools: {
    list: '/api/tools',
    create: '/api/tools',
    detail: (id) => `/api/tools/${id}`,
    update: (id) => `/api/tools/${id}`,
    delete: (id) => `/api/tools/${id}`
  },
  chemicals: {
    list: '/api/chemicals',
    create: '/api/chemicals',
    detail: (id) => `/api/chemicals/${id}`,
    update: (id) => `/api/chemicals/${id}`,
    delete: (id) => `/api/chemicals/${id}`
  },
  cycleCount: {
    schedules: '/api/cycle-count/schedules',
    batches: '/api/cycle-count/batches',
    items: '/api/cycle-count/items'
  }
};
