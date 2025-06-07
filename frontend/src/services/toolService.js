import supabaseService from './supabase';

const ToolService = {
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

  // Get all tools
  getAllTools: async () => {
    try {
      await ToolService.ensureSupabaseInitialized();
      const { data, error } = await supabaseService.select('tools', '*', { is_active: true });
      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Supabase Error [GET] tools:', error);
      throw error;
    }
  },

  // Get tool by ID
  getToolById: async (id) => {
    try {
      await ToolService.ensureSupabaseInitialized();
      // Ensure id is a number
      const toolId = typeof id === 'string' ? parseInt(id, 10) : id;
      const { data, error } = await supabaseService.select('tools', '*', { id: toolId, is_active: true });
      if (error) throw error;
      return data && data.length > 0 ? data[0] : null;
    } catch (error) {
      console.error(`Supabase Error [GET] tool ${id}:`, error);
      throw error;
    }
  },

  // Create new tool
  createTool: async (toolData) => {
    try {
      await ToolService.ensureSupabaseInitialized();
      console.log('Creating new tool with data:', toolData);

      const newTool = {
        ...toolData,
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      const { data, error } = await supabaseService.insert('tools', newTool);
      if (error) throw error;

      const result = data && data.length > 0 ? data[0] : null;
      console.log('Tool creation response:', result);
      return result;
    } catch (error) {
      console.error('Supabase Error [POST] tools:', error);
      throw error;
    }
  },

  // Update tool
  updateTool: async (id, toolData) => {
    try {
      await ToolService.ensureSupabaseInitialized();
      console.log('Sending tool update request:', { id, toolData });

      const updateData = {
        ...toolData,
        updated_at: new Date().toISOString()
      };

      const { data, error } = await supabaseService.update('tools', id, updateData);
      if (error) throw error;

      const result = data && data.length > 0 ? data[0] : null;
      console.log('Tool update response:', result);
      return result;
    } catch (error) {
      console.error('Supabase Error [PUT] tool:', error);
      throw error;
    }
  },

  // Delete tool (soft delete)
  deleteTool: async (id) => {
    try {
      await ToolService.ensureSupabaseInitialized();
      const { data, error } = await supabaseService.update('tools', id, {
        is_active: false,
        updated_at: new Date().toISOString()
      });
      if (error) throw error;
      return data && data.length > 0 ? data[0] : null;
    } catch (error) {
      console.error(`Supabase Error [DELETE] tool ${id}:`, error);
      throw error;
    }
  },

  // Search tools
  searchTools: async (query) => {
    try {
      await ToolService.ensureSupabaseInitialized();

      // Search by tool_number
      const { data: toolNumberData, error: toolNumberError } = await supabaseService.select('tools', '*', {
        is_active: true,
        tool_number: { operator: 'ilike', value: `%${query}%` }
      });
      if (toolNumberError) throw toolNumberError;

      // Search by description
      const { data: descData, error: descError } = await supabaseService.select('tools', '*', {
        is_active: true,
        description: { operator: 'ilike', value: `%${query}%` }
      });
      if (descError) throw descError;

      // Search by serial_number
      const { data: serialData, error: serialError } = await supabaseService.select('tools', '*', {
        is_active: true,
        serial_number: { operator: 'ilike', value: `%${query}%` }
      });
      if (serialError) throw serialError;

      // Combine and deduplicate results
      const allResults = [...(toolNumberData || []), ...(descData || []), ...(serialData || [])];
      const uniqueResults = allResults.filter((tool, index, self) =>
        index === self.findIndex(t => t.id === tool.id)
      );

      return uniqueResults;
    } catch (error) {
      console.error(`Supabase Error [GET] tools search ${query}:`, error);
      throw error;
    }
  },

  // Remove tool from service (temporarily or permanently)
  removeFromService: async (id, data) => {
    try {
      await ToolService.ensureSupabaseInitialized();

      // Create service history record
      const serviceRecord = {
        tool_id: id,
        action: 'removed',
        reason: data.reason,
        removed_by: data.removed_by,
        expected_return_date: data.expected_return_date,
        notes: data.notes,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      const { data: historyData, error: historyError } = await supabaseService.insert('tool_service_history', serviceRecord);
      if (historyError) throw historyError;

      // Update tool status
      const { data: toolData, error: toolError } = await supabaseService.update('tools', id, {
        status: 'out_of_service',
        updated_at: new Date().toISOString()
      });
      if (toolError) throw toolError;

      return {
        tool: toolData && toolData.length > 0 ? toolData[0] : null,
        service_record: historyData && historyData.length > 0 ? historyData[0] : null
      };
    } catch (error) {
      console.error(`Supabase Error [POST] tool ${id} remove from service:`, error);
      throw error;
    }
  },

  // Return tool to service
  returnToService: async (id, data) => {
    try {
      await ToolService.ensureSupabaseInitialized();

      // Create service history record
      const serviceRecord = {
        tool_id: id,
        action: 'returned',
        notes: data.notes,
        returned_by: data.returned_by,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      const { data: historyData, error: historyError } = await supabaseService.insert('tool_service_history', serviceRecord);
      if (historyError) throw historyError;

      // Update tool status
      const { data: toolData, error: toolError } = await supabaseService.update('tools', id, {
        status: 'available',
        updated_at: new Date().toISOString()
      });
      if (toolError) throw toolError;

      return {
        tool: toolData && toolData.length > 0 ? toolData[0] : null,
        service_record: historyData && historyData.length > 0 ? historyData[0] : null
      };
    } catch (error) {
      console.error(`Supabase Error [POST] tool ${id} return to service:`, error);
      throw error;
    }
  },

  // Get tool service history
  getServiceHistory: async (id, page = 1, limit = 20) => {
    try {
      await ToolService.ensureSupabaseInitialized();

      // Calculate offset for pagination
      const offset = (page - 1) * limit;

      const { data, error } = await supabaseService.select('tool_service_history', '*', { tool_id: id });
      if (error) throw error;

      // Sort by created_at descending and apply pagination
      const sortedData = (data || []).sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      const paginatedData = sortedData.slice(offset, offset + limit);

      return {
        data: paginatedData,
        total: sortedData.length,
        page,
        limit,
        total_pages: Math.ceil(sortedData.length / limit)
      };
    } catch (error) {
      console.error(`Supabase Error [GET] tool ${id} service history:`, error);
      throw error;
    }
  }
};

export default ToolService;
