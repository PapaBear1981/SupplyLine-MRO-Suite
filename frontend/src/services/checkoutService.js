import supabaseService from './supabase';

const CheckoutService = {
  // Ensure Supabase is initialized
  async ensureSupabaseInitialized() {
    if (!supabaseService.isReady()) {
      const configured = await supabaseService.configure(
        'https://illoycgawzqyvcsvdtoc.supabase.co',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlsbG95Y2dhd3pxeXZjc3ZkdG9jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg4MDU2MzMsImV4cCI6MjA2NDM4MTYzM30.rHfX3kgxc7cw2Yy3soChlqjVJ1zYfImsRweYVNKpFrY'
      );
      if (!configured) {
        throw new Error('Failed to configure Supabase');
      }
    }
  },

  // Get all checkouts
  getAllCheckouts: async () => {
    try {
      await CheckoutService.ensureSupabaseInitialized();
      const { data, error } = await supabaseService.select('checkouts', '*');
      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Supabase Error [GET] checkouts:', error);
      throw error;
    }
  },

  // Get checkout by ID
  getCheckoutById: async (id) => {
    try {
      await CheckoutService.ensureSupabaseInitialized();
      const { data, error } = await supabaseService.select('checkouts', '*', { id });
      if (error) throw error;
      return data && data.length > 0 ? data[0] : null;
    } catch (error) {
      console.error(`Supabase Error [GET] checkout ${id}:`, error);
      throw error;
    }
  },

  // Get user's checkouts
  getUserCheckouts: async () => {
    try {
      await CheckoutService.ensureSupabaseInitialized();

      // Get current user from Supabase auth
      const { data: { user } } = await supabaseService.client.auth.getUser();
      if (!user) {
        throw new Error('User not authenticated');
      }

      // Get user's checkouts that are not returned
      const { data, error } = await supabaseService.select('checkouts', '*', {
        user_id: user.id,
        returned_at: null
      });
      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Supabase Error [GET] user checkouts:', error);
      throw error;
    }
  },

  // Checkout a tool for the current user
  checkoutTool: async (toolId, expectedReturnDate) => {
    try {
      await CheckoutService.ensureSupabaseInitialized();
      console.log('Checking out tool:', { toolId, expectedReturnDate });

      // Get current user from Supabase auth
      const { data: { user } } = await supabaseService.client.auth.getUser();
      if (!user) {
        throw new Error('User not authenticated');
      }

      const requestData = {
        tool_id: toolId,
        user_id: user.id,
        expected_return_date: expectedReturnDate,
        checked_out_at: new Date().toISOString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      console.log('Sending checkout request with data:', requestData);

      const { data, error } = await supabaseService.insert('checkouts', requestData);
      if (error) throw error;

      // Update tool status to checked_out
      await supabaseService.update('tools', toolId, {
        status: 'checked_out',
        updated_at: new Date().toISOString()
      });

      const result = data && data.length > 0 ? data[0] : null;
      console.log('Checkout response:', result);
      return result;
    } catch (error) {
      console.error('Supabase Error [POST] checkout:', error);
      throw error;
    }
  },

  // Checkout a tool to another user
  checkoutToolToUser: async (toolId, userId, expectedReturnDate) => {
    try {
      await CheckoutService.ensureSupabaseInitialized();

      const requestData = {
        tool_id: toolId,
        user_id: userId,
        expected_return_date: expectedReturnDate,
        checked_out_at: new Date().toISOString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      const { data, error } = await supabaseService.insert('checkouts', requestData);
      if (error) throw error;

      // Update tool status to checked_out
      await supabaseService.update('tools', toolId, {
        status: 'checked_out',
        updated_at: new Date().toISOString()
      });

      return data && data.length > 0 ? data[0] : null;
    } catch (error) {
      console.error('Supabase Error [POST] checkout to user:', error);
      throw error;
    }
  },

  // Return a tool
  returnTool: async (returnData) => {
    try {
      await CheckoutService.ensureSupabaseInitialized();
      const { checkoutId, condition, returned_by, found, notes } = returnData;

      // Update checkout record with return information
      const updateData = {
        returned_at: new Date().toISOString(),
        return_condition: condition,
        returned_by: returned_by,
        found: found,
        return_notes: notes,
        updated_at: new Date().toISOString()
      };

      const { data: checkoutData, error: checkoutError } = await supabaseService.update('checkouts', checkoutId, updateData);
      if (checkoutError) throw checkoutError;

      // Get the checkout to find the tool_id
      const checkout = checkoutData && checkoutData.length > 0 ? checkoutData[0] : null;
      if (checkout && checkout.tool_id) {
        // Update tool status back to available
        await supabaseService.update('tools', checkout.tool_id, {
          status: 'available',
          updated_at: new Date().toISOString()
        });
      }

      return checkout;
    } catch (error) {
      console.error('Supabase Error [PUT] return tool:', error);
      throw error;
    }
  },

  // Get checkout history for a tool
  getToolCheckoutHistory: async (toolId) => {
    try {
      await CheckoutService.ensureSupabaseInitialized();
      const { data, error } = await supabaseService.select('checkouts', '*', { tool_id: toolId });
      if (error) throw error;

      // Sort by checkout date descending
      const sortedData = (data || []).sort((a, b) => new Date(b.checked_out_at) - new Date(a.checked_out_at));
      return sortedData;
    } catch (error) {
      console.error(`Supabase Error [GET] tool ${toolId} checkout history:`, error);
      throw error;
    }
  }
};

export default CheckoutService;
