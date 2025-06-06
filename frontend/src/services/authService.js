import supabaseService from './supabase';

const AuthService = {
  // Initialize Supabase if not already done
  async ensureSupabaseInitialized() {
    if (!supabaseService.isReady()) {
      // Use the provided credentials
      const configured = await supabaseService.configure(
        'https://illoycgawzqyvcsvdtoc.supabase.co',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlsbG95Y2dhd3pxeXZjc3ZkdG9jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg4MDU2MzMsImV4cCI6MjA2NDM4MTYzM30.rHfX3kgxc7cw2Yy3soChlqjVJ1zYfImsRweYVNKpFrY'
      );
      if (!configured) {
        throw new Error('Failed to configure Supabase');
      }
    }
  },

  // Login user using employee_number - we'll create a Supabase Auth user for them
  login: async (employeeNumber, password) => {
    try {
      await AuthService.ensureSupabaseInitialized();

      // First, get the user from our users table to validate they exist and are active
      const { data: users, error: userError } = await supabaseService.select(
        'users',
        '*',
        { employee_number: employeeNumber, is_active: true }
      );

      if (userError) {
        throw new Error('Database error: ' + userError.message);
      }

      if (!users || users.length === 0) {
        throw new Error('Invalid employee number or password');
      }

      const user = users[0];

      // Check if account is locked
      if (user.locked_until && new Date(user.locked_until) > new Date()) {
        throw new Error('Account is temporarily locked. Please try again later.');
      }

      // Create email from employee number for Supabase Auth (using a valid domain)
      const email = `${employeeNumber.toLowerCase()}@supplyline.app`;

      // Try to sign in with Supabase Auth
      const { data: authData, error: authError } = await supabaseService.signIn(email, password);

      if (authError) {
        // If user doesn't exist in Supabase Auth, create them
        if (authError.message.includes('Invalid login credentials')) {
          // For first-time login, create the Supabase Auth user
          const { data: signUpData, error: signUpError } = await supabaseService.signUp(
            email,
            password,
            {
              employee_number: employeeNumber,
              name: user.name,
              department: user.department,
              user_id: user.id
            }
          );

          if (signUpError) {
            throw new Error('Authentication setup failed: ' + signUpError.message);
          }

          // Now try to sign in again
          const { data: retryAuthData, error: retryAuthError } = await supabaseService.signIn(email, password);
          if (retryAuthError) {
            throw new Error('Login failed: ' + retryAuthError.message);
          }

          // Update last login
          await supabaseService.update('users', user.id, {
            failed_login_attempts: 0,
            locked_until: null,
            last_login: new Date().toISOString()
          });

          return {
            success: true,
            user: {
              id: user.id,
              employee_number: user.employee_number,
              name: user.name,
              is_admin: user.is_admin,
              department: user.department,
              auth_user: retryAuthData.user
            }
          };
        } else {
          // Increment failed login attempts
          const failedAttempts = (user.failed_login_attempts || 0) + 1;
          const updateData = { failed_login_attempts: failedAttempts };

          // Lock account after 5 failed attempts for 30 minutes
          if (failedAttempts >= 5) {
            updateData.locked_until = new Date(Date.now() + 30 * 60 * 1000).toISOString();
          }

          await supabaseService.update('users', user.id, updateData);
          throw new Error('Invalid employee number or password');
        }
      }

      // Successful login - reset failed attempts and update last login
      await supabaseService.update('users', user.id, {
        failed_login_attempts: 0,
        locked_until: null,
        last_login: new Date().toISOString()
      });

      return {
        success: true,
        user: {
          id: user.id,
          employee_number: user.employee_number,
          name: user.name,
          is_admin: user.is_admin,
          department: user.department,
          auth_user: authData.user
        }
      };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  // Register new user
  register: async (userData) => {
    try {
      await AuthService.ensureSupabaseInitialized();

      // Create email from employee number (using a valid domain)
      const email = `${userData.employee_number.toLowerCase()}@supplyline.app`;

      // Create user in Supabase Auth first
      const { data: authData, error: authError } = await supabaseService.signUp(
        email,
        userData.password,
        {
          employee_number: userData.employee_number,
          name: userData.name,
          department: userData.department
        }
      );

      if (authError) {
        throw new Error('Authentication setup failed: ' + authError.message);
      }

      // Create user in our users table
      const newUser = {
        employee_number: userData.employee_number,
        name: userData.name,
        department: userData.department,
        is_admin: userData.is_admin || false,
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      const { data, error } = await supabaseService.insert('users', newUser);

      if (error) {
        throw new Error('Registration failed: ' + error.message);
      }

      return {
        success: true,
        user: data[0],
        auth_user: authData.user
      };
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  },

  // Logout user
  logout: async () => {
    try {
      await AuthService.ensureSupabaseInitialized();

      // Sign out from Supabase Auth
      const { error } = await supabaseService.signOut();

      if (error) {
        console.error('Supabase logout error:', error);
      }

      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  },

  // Get current user info
  getCurrentUser: async () => {
    try {
      await AuthService.ensureSupabaseInitialized();

      // Get current user from Supabase Auth
      const { user: authUser, error: authError } = await supabaseService.getUser();

      if (authError || !authUser) {
        return null;
      }

      // Get user details from our users table
      const employeeNumber = authUser.user_metadata?.employee_number;
      if (!employeeNumber) {
        return null;
      }

      const { data: users, error } = await supabaseService.select(
        'users',
        '*',
        { employee_number: employeeNumber, is_active: true }
      );

      if (error || !users || users.length === 0) {
        return null;
      }

      return {
        ...users[0],
        auth_user: authUser
      };
    } catch (error) {
      console.error('Get current user error:', error);
      return null;
    }
  },

  // Check if user is authenticated
  isAuthenticated: async () => {
    try {
      await AuthService.ensureSupabaseInitialized();

      // Check Supabase Auth session
      const { user, error } = await supabaseService.getUser();

      return !error && user !== null;
    } catch (error) {
      console.error('Authentication check error:', error);
      return false;
    }
  }
};

export default AuthService;
