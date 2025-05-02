// Settings and preferences management
const defaultSettings = {
  theme: 'light',
  colorScheme: 'default',
  autoRefresh: false,
  refreshInterval: 30
};

let userSettings = { ...defaultSettings };
let refreshTimer = null;
let currentUser = null;

// Load settings from localStorage
function loadSettings() {
  const savedSettings = localStorage.getItem('toolCheckoutSettings');
  if (savedSettings) {
    userSettings = { ...defaultSettings, ...JSON.parse(savedSettings) };
  }
  applySettings();
  updateSettingsForm();
}

// Save settings to localStorage
function saveSettings() {
  localStorage.setItem('toolCheckoutSettings', JSON.stringify(userSettings));
}

// Apply settings to the UI
function applySettings() {
  // Apply theme
  document.documentElement.setAttribute('data-theme', userSettings.theme);

  // Apply color scheme
  document.documentElement.setAttribute('data-color-scheme', userSettings.colorScheme);

  // Set up auto-refresh
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }

  if (userSettings.autoRefresh) {
    refreshTimer = setInterval(loadRecords, userSettings.refreshInterval * 1000);
  }
}

// Update settings form with current values
function updateSettingsForm() {
  // Set theme radio buttons
  document.querySelector(`input[name="theme"][value="${userSettings.theme}"]`).checked = true;

  // Set color scheme select
  document.getElementById('color_scheme').value = userSettings.colorScheme;

  // Set auto-refresh checkbox
  document.getElementById('auto_refresh').checked = userSettings.autoRefresh;

  // Set refresh interval
  document.getElementById('refresh_interval').value = userSettings.refreshInterval;
}

// Authentication functions
async function checkAuthStatus() {
  try {
    const response = await fetch('/auth/status');
    const data = await response.json();

    if (data.authenticated) {
      currentUser = data.user;
      updateUIForLoggedInUser();
    } else {
      currentUser = null;
      updateUIForLoggedOutUser();
    }
  } catch (error) {
    console.error('Error checking auth status:', error);
    currentUser = null;
    updateUIForLoggedOutUser();
  }
}

function updateUIForLoggedInUser() {
  // Update buttons
  document.getElementById('login_btn').style.display = 'none';
  document.getElementById('logout_btn').style.display = 'inline-block';

  // Update user info panel
  const userInfoPanel = document.getElementById('user_info');
  userInfoPanel.style.display = 'block';
  document.getElementById('user_name').textContent = currentUser.name;

  // Set user role text
  if (currentUser.is_admin) {
    document.getElementById('user_role').textContent = 'Administrator';
  } else if (currentUser.department === 'Materials') {
    document.getElementById('user_role').textContent = 'Materials (Tool Manager)';
  } else {
    document.getElementById('user_role').textContent = 'Regular User';
  }

  // Show admin-only elements if user is admin
  const adminElements = document.querySelectorAll('.admin-only');
  adminElements.forEach(el => {
    // Show for both admin and Materials department users
    el.style.display = (currentUser.is_admin || currentUser.department === 'Materials') ? 'block' : 'none';
  });
}

function updateUIForLoggedOutUser() {
  // Update buttons
  document.getElementById('login_btn').style.display = 'inline-block';
  document.getElementById('logout_btn').style.display = 'none';

  // Hide user info panel
  document.getElementById('user_info').style.display = 'none';

  // Hide admin-only elements
  const adminElements = document.querySelectorAll('.admin-only');
  adminElements.forEach(el => {
    el.style.display = 'none';
  });
}

async function login(employeeNumber, password, rememberMe = false) {
  try {
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        employee_number: employeeNumber,
        password,
        remember_me: rememberMe
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Login failed');
    }

    const userData = await response.json();
    currentUser = userData;
    updateUIForLoggedInUser();

    // Close login modal
    document.getElementById('login_modal').style.display = 'none';

    // Clear form
    document.getElementById('employee_number').value = '';
    document.getElementById('password').value = '';
    document.getElementById('remember_me').checked = false;
    document.getElementById('login_error').style.display = 'none';

    return true;
  } catch (error) {
    console.error('Login error:', error);
    document.getElementById('login_error').textContent = error.message;
    document.getElementById('login_error').style.display = 'block';
    return false;
  }
}

async function logout() {
  try {
    await fetch('/auth/logout', { method: 'POST' });
    currentUser = null;
    updateUIForLoggedOutUser();
  } catch (error) {
    console.error('Logout error:', error);
  }
}

// Modal functionality
const settingsModal = document.getElementById('settings_modal');
const loginModal = document.getElementById('login_modal');
const settingsBtn = document.getElementById('settings_btn');
const loginBtn = document.getElementById('login_btn');
const logoutBtn = document.getElementById('logout_btn');
const closeBtns = document.querySelectorAll('.close');

// Open modals
settingsBtn.addEventListener('click', () => {
  settingsModal.style.display = 'block';
  updateSettingsForm();
});

loginBtn.addEventListener('click', () => {
  loginModal.style.display = 'block';
});

// Close modals
closeBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const modalId = btn.dataset.modal || 'settings_modal';
    document.getElementById(modalId).style.display = 'none';
  });
});

// Close modal when clicking outside
window.addEventListener('click', (event) => {
  if (event.target === settingsModal) {
    settingsModal.style.display = 'none';
  } else if (event.target === loginModal) {
    loginModal.style.display = 'none';
  }
});

// Registration functions
async function register(name, employeeNumber, department, password) {
  try {
    const response = await fetch('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        employee_number: employeeNumber,
        department,
        password
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Registration failed');
    }

    return true;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
}

// Password reset functions
async function requestPasswordReset(employeeNumber) {
  try {
    const response = await fetch('/auth/reset-password/request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ employee_number: employeeNumber })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Password reset request failed');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Password reset request error:', error);
    throw error;
  }
}

async function confirmPasswordReset(employeeNumber, resetCode, newPassword) {
  try {
    const response = await fetch('/auth/reset-password/confirm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        employee_number: employeeNumber,
        reset_code: resetCode,
        new_password: newPassword
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Password reset confirmation failed');
    }

    return true;
  } catch (error) {
    console.error('Password reset confirmation error:', error);
    throw error;
  }
}

// Profile functions
async function getUserProfile() {
  try {
    const response = await fetch('/user/profile');

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to get user profile');
    }

    return await response.json();
  } catch (error) {
    console.error('Get profile error:', error);
    throw error;
  }
}

async function updateUserProfile(name, department) {
  try {
    const response = await fetch('/user/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, department })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to update profile');
    }

    return await response.json();
  } catch (error) {
    console.error('Update profile error:', error);
    throw error;
  }
}

async function changePassword(currentPassword, newPassword) {
  try {
    const response = await fetch('/user/password', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to change password');
    }

    return true;
  } catch (error) {
    console.error('Change password error:', error);
    throw error;
  }
}

async function getUserActivity() {
  try {
    const response = await fetch('/user/activity');

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to get user activity');
    }

    return await response.json();
  } catch (error) {
    console.error('Get user activity error:', error);
    throw error;
  }
}

// Login form submission
document.getElementById('login_submit').addEventListener('click', async () => {
  const employeeNumber = document.getElementById('employee_number').value;
  const password = document.getElementById('password').value;
  const rememberMe = document.getElementById('remember_me').checked;

  if (!employeeNumber || !password) {
    document.getElementById('login_error').textContent = 'Please enter both employee number and password';
    document.getElementById('login_error').style.display = 'block';
    return;
  }

  await login(employeeNumber, password, rememberMe);
});

// Registration form submission
document.getElementById('register_submit').addEventListener('click', async () => {
  const name = document.getElementById('reg_name').value;
  const employeeNumber = document.getElementById('reg_employee_number').value;
  const department = document.getElementById('reg_department').value;
  const password = document.getElementById('reg_password').value;
  const confirmPassword = document.getElementById('reg_confirm_password').value;

  // Clear previous errors
  document.getElementById('register_error').style.display = 'none';
  document.getElementById('register_success').style.display = 'none';

  // Validate form
  if (!name || !employeeNumber || !department || !password || !confirmPassword) {
    document.getElementById('register_error').textContent = 'Please fill in all fields';
    document.getElementById('register_error').style.display = 'block';
    return;
  }

  if (password !== confirmPassword) {
    document.getElementById('register_error').textContent = 'Passwords do not match';
    document.getElementById('register_error').style.display = 'block';
    return;
  }

  try {
    await register(name, employeeNumber, department, password);

    // Show success message
    document.getElementById('register_success').textContent = 'Registration successful! You can now log in.';
    document.getElementById('register_success').style.display = 'block';

    // Clear form
    document.getElementById('reg_name').value = '';
    document.getElementById('reg_employee_number').value = '';
    document.getElementById('reg_department').value = '';
    document.getElementById('reg_password').value = '';
    document.getElementById('reg_confirm_password').value = '';

    // Switch to login after a delay
    setTimeout(() => {
      document.getElementById('login_link').click();
    }, 3000);
  } catch (error) {
    document.getElementById('register_error').textContent = error.message;
    document.getElementById('register_error').style.display = 'block';
  }
});

// Password reset request
document.getElementById('request_reset').addEventListener('click', async () => {
  const employeeNumber = document.getElementById('reset_employee_number').value;

  // Clear previous messages
  document.getElementById('reset_error').style.display = 'none';
  document.getElementById('reset_success').style.display = 'none';

  if (!employeeNumber) {
    document.getElementById('reset_error').textContent = 'Please enter your employee number';
    document.getElementById('reset_error').style.display = 'block';
    return;
  }

  try {
    const result = await requestPasswordReset(employeeNumber);

    // Show success message
    document.getElementById('reset_success').textContent = 'Reset code sent! Check your email.';
    document.getElementById('reset_success').style.display = 'block';

    // For demo purposes, show the code (in production, this would be sent via email)
    if (result.reset_code) {
      document.getElementById('reset_success').textContent += ` (Code: ${result.reset_code})`;
    }

    // Show step 2
    document.getElementById('reset_step1').style.display = 'none';
    document.getElementById('reset_step2').style.display = 'block';
  } catch (error) {
    document.getElementById('reset_error').textContent = error.message;
    document.getElementById('reset_error').style.display = 'block';
  }
});

// Complete password reset
document.getElementById('complete_reset').addEventListener('click', async () => {
  const employeeNumber = document.getElementById('reset_employee_number').value;
  const resetCode = document.getElementById('reset_code').value;
  const newPassword = document.getElementById('new_password').value;
  const confirmNewPassword = document.getElementById('confirm_new_password').value;

  // Clear previous messages
  document.getElementById('reset_error').style.display = 'none';
  document.getElementById('reset_success').style.display = 'none';

  // Validate form
  if (!resetCode || !newPassword || !confirmNewPassword) {
    document.getElementById('reset_error').textContent = 'Please fill in all fields';
    document.getElementById('reset_error').style.display = 'block';
    return;
  }

  if (newPassword !== confirmNewPassword) {
    document.getElementById('reset_error').textContent = 'Passwords do not match';
    document.getElementById('reset_error').style.display = 'block';
    return;
  }

  try {
    await confirmPasswordReset(employeeNumber, resetCode, newPassword);

    // Show success message
    document.getElementById('reset_success').textContent = 'Password reset successful! You can now log in with your new password.';
    document.getElementById('reset_success').style.display = 'block';

    // Clear form
    document.getElementById('reset_code').value = '';
    document.getElementById('new_password').value = '';
    document.getElementById('confirm_new_password').value = '';

    // Switch to login after a delay
    setTimeout(() => {
      document.getElementById('back_to_login').click();
    }, 3000);
  } catch (error) {
    document.getElementById('reset_error').textContent = error.message;
    document.getElementById('reset_error').style.display = 'block';
  }
});

// Profile tab switching
const tabButtons = document.querySelectorAll('.tab-button');
tabButtons.forEach(button => {
  button.addEventListener('click', () => {
    // Remove active class from all tabs and content
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    // Add active class to clicked tab and corresponding content
    button.classList.add('active');
    const tabId = button.dataset.tab;
    document.getElementById(tabId).classList.add('active');

    // Load activity data if activity tab is selected
    if (tabId === 'activity_log') {
      loadUserActivity();
    }
  });
});

// Load user activity
async function loadUserActivity() {
  const activityList = document.getElementById('user_activity_list');
  activityList.innerHTML = '<p class="loading-text">Loading activity...</p>';

  try {
    const activities = await getUserActivity();

    if (activities.length === 0) {
      activityList.innerHTML = '<p>No activity found.</p>';
      return;
    }

    activityList.innerHTML = '';
    activities.forEach(activity => {
      const activityItem = document.createElement('div');
      activityItem.className = 'activity-item';

      const activityDate = new Date(activity.timestamp);

      activityItem.innerHTML = `
        <div>${activity.description || activity.activity_type}</div>
        <div class="activity-time">${activityDate.toLocaleString()}</div>
      `;

      activityList.appendChild(activityItem);
    });
  } catch (error) {
    activityList.innerHTML = `<p>Error loading activity: ${error.message}</p>`;
  }
}

// Update profile
document.getElementById('update_profile').addEventListener('click', async () => {
  const name = document.getElementById('profile_name').value;
  const department = document.getElementById('profile_department').value;

  // Clear previous messages
  document.getElementById('profile_error').style.display = 'none';
  document.getElementById('profile_success').style.display = 'none';

  if (!name || !department) {
    document.getElementById('profile_error').textContent = 'Please fill in all fields';
    document.getElementById('profile_error').style.display = 'block';
    return;
  }

  try {
    const updatedUser = await updateUserProfile(name, department);

    // Update current user data
    currentUser = updatedUser;
    updateUIForLoggedInUser();

    // Show success message
    document.getElementById('profile_success').textContent = 'Profile updated successfully!';
    document.getElementById('profile_success').style.display = 'block';
  } catch (error) {
    document.getElementById('profile_error').textContent = error.message;
    document.getElementById('profile_error').style.display = 'block';
  }
});

// Change password
document.getElementById('update_password').addEventListener('click', async () => {
  const currentPassword = document.getElementById('current_password').value;
  const newPassword = document.getElementById('profile_new_password').value;
  const confirmPassword = document.getElementById('profile_confirm_password').value;

  // Clear previous messages
  document.getElementById('profile_error').style.display = 'none';
  document.getElementById('profile_success').style.display = 'none';

  if (!currentPassword || !newPassword || !confirmPassword) {
    document.getElementById('profile_error').textContent = 'Please fill in all fields';
    document.getElementById('profile_error').style.display = 'block';
    return;
  }

  if (newPassword !== confirmPassword) {
    document.getElementById('profile_error').textContent = 'New passwords do not match';
    document.getElementById('profile_error').style.display = 'block';
    return;
  }

  try {
    await changePassword(currentPassword, newPassword);

    // Show success message
    document.getElementById('profile_success').textContent = 'Password changed successfully!';
    document.getElementById('profile_success').style.display = 'block';

    // Clear form
    document.getElementById('current_password').value = '';
    document.getElementById('profile_new_password').value = '';
    document.getElementById('profile_confirm_password').value = '';
  } catch (error) {
    document.getElementById('profile_error').textContent = error.message;
    document.getElementById('profile_error').style.display = 'block';
  }
});

// Navigation between modals
document.getElementById('register_link').addEventListener('click', (e) => {
  e.preventDefault();
  document.getElementById('login_modal').style.display = 'none';
  document.getElementById('register_modal').style.display = 'block';
});

document.getElementById('login_link').addEventListener('click', (e) => {
  e.preventDefault();
  document.getElementById('register_modal').style.display = 'none';
  document.getElementById('login_modal').style.display = 'block';
});

document.getElementById('forgot_password_link').addEventListener('click', (e) => {
  e.preventDefault();
  document.getElementById('login_modal').style.display = 'none';
  document.getElementById('reset_password_modal').style.display = 'block';
  // Reset the password reset form to step 1
  document.getElementById('reset_step1').style.display = 'block';
  document.getElementById('reset_step2').style.display = 'none';
  document.getElementById('reset_error').style.display = 'none';
  document.getElementById('reset_success').style.display = 'none';
});

document.getElementById('back_to_login').addEventListener('click', (e) => {
  e.preventDefault();
  document.getElementById('reset_password_modal').style.display = 'none';
  document.getElementById('login_modal').style.display = 'block';
});

document.getElementById('view_profile').addEventListener('click', (e) => {
  e.preventDefault();

  // Load user profile data
  getUserProfile().then(user => {
    document.getElementById('profile_name').value = user.name;
    document.getElementById('profile_employee_number').value = user.employee_number;
    document.getElementById('profile_department').value = user.department;

    // Show profile modal
    document.getElementById('profile_modal').style.display = 'block';

    // Reset to first tab
    document.querySelector('.tab-button[data-tab="profile_info"]').click();
  }).catch(error => {
    console.error('Error loading profile:', error);
  });
});

// Tool management
document.getElementById('manage_tools_link')?.addEventListener('click', (e) => {
  e.preventDefault();

  // Show tools modal
  document.getElementById('tools_modal').style.display = 'block';

  // Load tools
  loadTools().catch(error => {
    console.error('Error loading tools:', error);
    document.getElementById('tools_error').textContent = 'Failed to load tools';
    document.getElementById('tools_error').style.display = 'block';
  });
});

// Add tool button
document.getElementById('add_tool_btn')?.addEventListener('click', async () => {
  // Get form values
  const toolNumber = document.getElementById('tool_number_input').value;
  const serialNumber = document.getElementById('serial_number_input').value;
  const description = document.getElementById('description_input').value;
  const condition = document.getElementById('condition_input').value;
  const location = document.getElementById('location_input').value;

  // Clear previous messages
  document.getElementById('tools_error').style.display = 'none';
  document.getElementById('tools_success').style.display = 'none';

  // Validate required fields
  if (!toolNumber || !serialNumber) {
    document.getElementById('tools_error').textContent = 'Tool number and serial number are required';
    document.getElementById('tools_error').style.display = 'block';
    return;
  }

  try {
    const result = await addTool({
      tool_number: toolNumber,
      serial_number: serialNumber,
      description,
      condition,
      location
    });

    // Show success message
    document.getElementById('tools_success').textContent = `Tool ${result.tool_number} added successfully`;
    document.getElementById('tools_success').style.display = 'block';

    // Clear form
    document.getElementById('tool_number_input').value = '';
    document.getElementById('serial_number_input').value = '';
    document.getElementById('description_input').value = '';
    document.getElementById('condition_input').value = 'New';
    document.getElementById('location_input').value = '';

    // Refresh tools list
    loadTools();
  } catch (error) {
    document.getElementById('tools_error').textContent = error.message;
    document.getElementById('tools_error').style.display = 'block';
  }
});

// Refresh tools button
document.getElementById('refresh_tools_btn')?.addEventListener('click', () => {
  loadTools().catch(error => {
    console.error('Error refreshing tools:', error);
    document.getElementById('tools_error').textContent = 'Failed to refresh tools';
    document.getElementById('tools_error').style.display = 'block';
  });
});

// Tool search functionality
document.getElementById('tool_search')?.addEventListener('input', (e) => {
  const searchTerm = e.target.value.toLowerCase();
  const rows = document.querySelectorAll('#tools_table tbody tr');

  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(searchTerm) ? '' : 'none';
  });
});

// Logout button
logoutBtn.addEventListener('click', logout);

// Save settings button
document.getElementById('save_settings').addEventListener('click', () => {
  // Get values from form
  userSettings.theme = document.querySelector('input[name="theme"]:checked').value;
  userSettings.colorScheme = document.getElementById('color_scheme').value;
  userSettings.autoRefresh = document.getElementById('auto_refresh').checked;
  userSettings.refreshInterval = parseInt(document.getElementById('refresh_interval').value);

  // Save and apply settings
  saveSettings();
  applySettings();

  // Close modal
  modal.style.display = 'none';
});

// Records loading functionality
async function loadRecords() {
  try {
    const res = await fetch('/checkouts');
    const records = await res.json();
    const tbody = document.querySelector('#records tbody');
    tbody.innerHTML = '';
    records.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r.id}</td>
        <td>${r.tool_id}</td>
        <td>${r.user_id}</td>
        <td>${new Date(r.checkout_date).toLocaleString()}</td>
        <td>${r.return_date ? new Date(r.return_date).toLocaleString() : ''}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (error) {
    console.error('Error loading records:', error);
  }
}

// Tool management functions
async function loadTools() {
  try {
    const response = await fetch('/tools');
    if (!response.ok) {
      throw new Error('Failed to load tools');
    }
    const tools = await response.json();

    // Update the tools table
    const tbody = document.querySelector('#tools_table tbody');
    tbody.innerHTML = '';

    tools.forEach(tool => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${tool.id}</td>
        <td>${tool.tool_number}</td>
        <td>${tool.serial_number}</td>
        <td>${tool.description || ''}</td>
        <td>${tool.condition || ''}</td>
        <td>${tool.location || ''}</td>
      `;
      tbody.appendChild(tr);
    });

    return tools;
  } catch (error) {
    console.error('Error loading tools:', error);
    throw error;
  }
}

async function addTool(toolData) {
  try {
    const response = await fetch('/tools', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(toolData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to add tool');
    }

    return await response.json();
  } catch (error) {
    console.error('Error adding tool:', error);
    throw error;
  }
}

// Checkout functionality
document.getElementById('checkout_btn').addEventListener('click', async () => {
  const tool_id = document.getElementById('tool_id').value;
  const user_id = document.getElementById('user_id').value;

  if (!tool_id || !user_id) {
    alert('Enter both Tool ID and User ID.');
    return;
  }

  try {
    const response = await fetch('/checkouts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool_id, user_id })
    });

    const data = await response.json();

    if (!response.ok) {
      alert(data.error || 'Failed to checkout tool');
      return;
    }

    // Success
    alert(data.message || 'Tool checked out successfully');
    document.getElementById('tool_id').value = '';
    document.getElementById('user_id').value = '';
    loadRecords();
  } catch (error) {
    console.error('Error checking out tool:', error);
    alert('Failed to checkout tool. Please try again.');
  }
});

// Return functionality
document.getElementById('return_btn').addEventListener('click', async () => {
  const checkout_id = document.getElementById('checkout_id').value;

  if (!checkout_id) {
    alert('Enter Checkout ID.');
    return;
  }

  try {
    const response = await fetch(`/checkouts/${checkout_id}/return`, {
      method: 'POST'
    });

    const data = await response.json();

    if (!response.ok) {
      alert(data.error || 'Failed to return tool');
      return;
    }

    // Success
    alert(data.message || 'Tool returned successfully');
    document.getElementById('checkout_id').value = '';
    loadRecords();
  } catch (error) {
    console.error('Error returning tool:', error);
    alert('Failed to return tool. Please try again.');
  }
});

// Initialize on page load
window.addEventListener('load', () => {
  loadSettings();
  checkAuthStatus();
  loadRecords();

  // Add keyboard event listener for login form
  document.getElementById('password').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      document.getElementById('login_submit').click();
    }
  });

  // Initialize tool management tabs
  const toolTabButtons = document.querySelectorAll('#tools_modal .tab-button');
  toolTabButtons.forEach(button => {
    button.addEventListener('click', () => {
      // Remove active class from all tabs and content
      document.querySelectorAll('#tools_modal .tab-button').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('#tools_modal .tab-content').forEach(content => content.classList.remove('active'));

      // Add active class to clicked tab and corresponding content
      button.classList.add('active');
      const tabId = button.dataset.tab;
      document.getElementById(tabId).classList.add('active');

      // Load tools if view_tools tab is selected
      if (tabId === 'view_tools') {
        loadTools().catch(error => {
          console.error('Error loading tools:', error);
        });
      }
    });
  });

  // Add close functionality for tools modal
  const toolsModalClose = document.querySelector('#tools_modal .close');
  if (toolsModalClose) {
    toolsModalClose.addEventListener('click', () => {
      document.getElementById('tools_modal').style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
      const toolsModal = document.getElementById('tools_modal');
      if (event.target === toolsModal) {
        toolsModal.style.display = 'none';
      }
    });
  }
});