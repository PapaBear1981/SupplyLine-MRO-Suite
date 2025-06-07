import supabaseService from './supabase';

const ChemicalService = {
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

  // Get all chemicals
  getAllChemicals: async () => {
    try {
      await ChemicalService.ensureSupabaseInitialized();
      const { data, error } = await supabaseService.select('chemicals', '*', { is_active: true });
      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Supabase Error [GET] chemicals:', error);
      throw error;
    }
  },

  // Get chemical by ID
  getChemicalById: async (id) => {
    try {
      await ChemicalService.ensureSupabaseInitialized();
      const { data, error } = await supabaseService.select('chemicals', '*', { id, is_active: true });
      if (error) throw error;
      return data && data.length > 0 ? data[0] : null;
    } catch (error) {
      console.error(`Supabase Error [GET] chemical ${id}:`, error);
      throw error;
    }
  },

  // Create new chemical
  createChemical: async (chemicalData) => {
    try {
      await ChemicalService.ensureSupabaseInitialized();
      const newChemical = {
        ...chemicalData,
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      const { data, error } = await supabaseService.insert('chemicals', newChemical);
      if (error) throw error;
      return data && data.length > 0 ? data[0] : null;
    } catch (error) {
      console.error('Supabase Error [POST] chemicals:', error);
      throw error;
    }
  },

  // Update chemical
  updateChemical: async (id, chemicalData) => {
    try {
      await ChemicalService.ensureSupabaseInitialized();
      const updateData = {
        ...chemicalData,
        updated_at: new Date().toISOString()
      };
      const { data, error } = await supabaseService.update('chemicals', id, updateData);
      if (error) throw error;
      return data && data.length > 0 ? data[0] : null;
    } catch (error) {
      console.error(`Supabase Error [PUT] chemical ${id}:`, error);
      throw error;
    }
  },

  // Delete chemical (soft delete)
  deleteChemical: async (id) => {
    try {
      await ChemicalService.ensureSupabaseInitialized();
      const { data, error } = await supabaseService.update('chemicals', id, {
        is_active: false,
        updated_at: new Date().toISOString()
      });
      if (error) throw error;
      return data && data.length > 0 ? data[0] : null;
    } catch (error) {
      console.error(`Supabase Error [DELETE] chemical ${id}:`, error);
      throw error;
    }
  },

  // Search chemicals
  searchChemicals: async (query) => {
    try {
      await ChemicalService.ensureSupabaseInitialized();
      const { data, error } = await supabaseService.select('chemicals', '*', {
        is_active: true,
        part_number: { operator: 'ilike', value: `%${query}%` }
      });
      if (error) throw error;

      // Also search by description and lot_number
      const { data: descData, error: descError } = await supabaseService.select('chemicals', '*', {
        is_active: true,
        description: { operator: 'ilike', value: `%${query}%` }
      });
      if (descError) throw descError;

      const { data: lotData, error: lotError } = await supabaseService.select('chemicals', '*', {
        is_active: true,
        lot_number: { operator: 'ilike', value: `%${query}%` }
      });
      if (lotError) throw lotError;

      // Combine and deduplicate results
      const allResults = [...(data || []), ...(descData || []), ...(lotData || [])];
      const uniqueResults = allResults.filter((chemical, index, self) =>
        index === self.findIndex(c => c.id === chemical.id)
      );

      return uniqueResults;
    } catch (error) {
      console.error(`Supabase Error [GET] chemicals search ${query}:`, error);
      throw error;
    }
  },

  // Issue chemical
  issueChemical: async (id, data) => {
    try {
      await ChemicalService.ensureSupabaseInitialized();

      // Create issuance record
      const issuanceData = {
        chemical_id: id,
        issued_to: data.issued_to,
        quantity_issued: data.quantity_issued,
        purpose: data.purpose,
        issued_by: data.issued_by,
        issued_at: new Date().toISOString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      const { data: issuance, error: issuanceError } = await supabaseService.insert('chemical_issuances', issuanceData);
      if (issuanceError) throw issuanceError;

      // Update chemical quantity
      const chemical = await ChemicalService.getChemicalById(id);
      if (chemical) {
        const newQuantity = (chemical.current_quantity || 0) - (data.quantity_issued || 0);
        await ChemicalService.updateChemical(id, { current_quantity: newQuantity });
      }

      return issuance && issuance.length > 0 ? issuance[0] : null;
    } catch (error) {
      console.error(`Supabase Error [POST] chemical ${id} issue:`, error);
      throw error;
    }
  },

  // Get chemical issuances
  getChemicalIssuances: async (id) => {
    try {
      await ChemicalService.ensureSupabaseInitialized();
      const { data, error } = await supabaseService.select('chemical_issuances', '*', { chemical_id: id });
      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error(`Supabase Error [GET] chemical ${id} issuances:`, error);
      throw error;
    }
  },

  // Get all issuances
  getAllIssuances: async (filters = {}) => {
    try {
      await ChemicalService.ensureSupabaseInitialized();
      const { data, error } = await supabaseService.select('chemical_issuances', '*', filters);
      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Supabase Error [GET] issuances:', error);
      throw error;
    }
  },

  // Archive a chemical
  archiveChemical: async (id, reason) => {
    try {
      await ChemicalService.ensureSupabaseInitialized();
      const { data, error } = await supabaseService.update('chemicals', id, {
        is_archived: true,
        archive_reason: reason,
        archived_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      });
      if (error) throw error;
      return data && data.length > 0 ? data[0] : null;
    } catch (error) {
      console.error(`Supabase Error [POST] chemical ${id} archive:`, error);
      throw error;
    }
  },

  // Unarchive a chemical
  unarchiveChemical: async (id) => {
    try {
      await ChemicalService.ensureSupabaseInitialized();
      const { data, error } = await supabaseService.update('chemicals', id, {
        is_archived: false,
        archive_reason: null,
        archived_at: null,
        updated_at: new Date().toISOString()
      });
      if (error) throw error;
      return data && data.length > 0 ? data[0] : null;
    } catch (error) {
      console.error(`Supabase Error [POST] chemical ${id} unarchive:`, error);
      throw error;
    }
  },

  // Get archived chemicals
  getArchivedChemicals: async (filters = {}) => {
    try {
      await ChemicalService.ensureSupabaseInitialized();
      const archiveFilters = { ...filters, is_archived: true };
      const { data, error } = await supabaseService.select('chemicals', '*', archiveFilters);
      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Supabase Error [GET] archived chemicals:', error);
      throw error;
    }
  },

  // Get waste analytics
  getWasteAnalytics: async (timeframe = 'month', part_number = null) => {
    try {
      await ChemicalService.ensureSupabaseInitialized();

      // Calculate date range based on timeframe
      const endDate = new Date();
      const startDate = new Date();

      switch (timeframe) {
        case 'week':
          startDate.setDate(endDate.getDate() - 7);
          break;
        case 'month':
          startDate.setMonth(endDate.getMonth() - 1);
          break;
        case 'quarter':
          startDate.setMonth(endDate.getMonth() - 3);
          break;
        case 'year':
          startDate.setFullYear(endDate.getFullYear() - 1);
          break;
        default:
          startDate.setMonth(endDate.getMonth() - 1);
      }

      // Get issuances within timeframe
      const filters = {
        issued_at: { operator: 'gte', value: startDate.toISOString() }
      };

      if (part_number) {
        // Get chemicals with this part number first
        const { data: chemicals, error: chemError } = await supabaseService.select('chemicals', 'id', { part_number });
        if (chemError) throw chemError;

        if (chemicals && chemicals.length > 0) {
          filters.chemical_id = chemicals.map(c => c.id);
        }
      }

      const { data, error } = await supabaseService.select('chemical_issuances', '*', filters);
      if (error) throw error;

      // Calculate waste analytics from issuances
      const analytics = {
        total_waste: data?.reduce((sum, issuance) => sum + (issuance.quantity_issued || 0), 0) || 0,
        waste_by_part: {},
        waste_by_date: {}
      };

      return analytics;
    } catch (error) {
      console.error('Supabase Error [GET] waste analytics:', error);
      throw error;
    }
  },

  // Get usage analytics
  getUsageAnalytics: async (part_number, timeframe = 'month') => {
    try {
      if (!part_number) {
        throw new Error('Part number is required');
      }

      await ChemicalService.ensureSupabaseInitialized();

      // Get chemicals with this part number
      const { data: chemicals, error: chemError } = await supabaseService.select('chemicals', '*', { part_number });
      if (chemError) throw chemError;

      if (!chemicals || chemicals.length === 0) {
        return { usage: 0, chemicals: [] };
      }

      // Calculate date range
      const endDate = new Date();
      const startDate = new Date();

      switch (timeframe) {
        case 'week':
          startDate.setDate(endDate.getDate() - 7);
          break;
        case 'month':
          startDate.setMonth(endDate.getMonth() - 1);
          break;
        case 'quarter':
          startDate.setMonth(endDate.getMonth() - 3);
          break;
        case 'year':
          startDate.setFullYear(endDate.getFullYear() - 1);
          break;
        default:
          startDate.setMonth(endDate.getMonth() - 1);
      }

      // Get issuances for these chemicals
      const chemicalIds = chemicals.map(c => c.id);
      const { data: issuances, error: issuanceError } = await supabaseService.select('chemical_issuances', '*', {
        chemical_id: chemicalIds,
        issued_at: { operator: 'gte', value: startDate.toISOString() }
      });
      if (issuanceError) throw issuanceError;

      const totalUsage = issuances?.reduce((sum, issuance) => sum + (issuance.quantity_issued || 0), 0) || 0;

      return {
        usage: totalUsage,
        chemicals: chemicals,
        issuances: issuances || []
      };
    } catch (error) {
      console.error('Supabase Error [GET] usage analytics:', error);
      throw error;
    }
  },

  // Get part number analytics
  getPartNumberAnalytics: async (part_number) => {
    try {
      if (!part_number) {
        throw new Error('Part number is required');
      }

      await ChemicalService.ensureSupabaseInitialized();

      // Get all chemicals with this part number
      const { data: chemicals, error } = await supabaseService.select('chemicals', '*', { part_number });
      if (error) throw error;

      if (!chemicals || chemicals.length === 0) {
        return { chemicals: [], total_quantity: 0, total_value: 0 };
      }

      const totalQuantity = chemicals.reduce((sum, chem) => sum + (chem.current_quantity || 0), 0);
      const totalValue = chemicals.reduce((sum, chem) => sum + ((chem.current_quantity || 0) * (chem.unit_cost || 0)), 0);

      return {
        chemicals,
        total_quantity: totalQuantity,
        total_value: totalValue,
        count: chemicals.length
      };
    } catch (error) {
      console.error('Supabase Error [GET] part analytics:', error);
      throw error;
    }
  },

  // Get all unique part numbers
  getUniquePartNumbers: async () => {
    try {
      // Get all chemicals and extract unique part numbers
      const chemicals = await ChemicalService.getAllChemicals();
      const partNumbers = [...new Set(chemicals.map(c => c.part_number))];
      return partNumbers.sort();
    } catch (error) {
      throw error;
    }
  },

  // Get chemicals that need to be reordered
  getChemicalsNeedingReorder: async () => {
    try {
      await ChemicalService.ensureSupabaseInitialized();

      // Get all active chemicals
      const { data: chemicals, error } = await supabaseService.select('chemicals', '*', { is_active: true });
      if (error) throw error;

      // Filter chemicals that need reordering (current_quantity <= reorder_point)
      const needingReorder = (chemicals || []).filter(chemical => {
        const currentQty = chemical.current_quantity || 0;
        const reorderPoint = chemical.reorder_point || 0;
        return currentQty <= reorderPoint && chemical.reorder_status !== 'ordered';
      });

      return needingReorder;
    } catch (error) {
      console.error('Supabase Error [GET] chemicals needing reorder:', error);
      throw error;
    }
  },

  // Get chemicals that are on order
  getChemicalsOnOrder: async () => {
    try {
      await ChemicalService.ensureSupabaseInitialized();
      const { data, error } = await supabaseService.select('chemicals', '*', {
        is_active: true,
        reorder_status: 'ordered'
      });
      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Supabase Error [GET] chemicals on order:', error);
      throw error;
    }
  },

  // Get chemicals that are expiring soon
  getChemicalsExpiringSoon: async (days = 30) => {
    try {
      await ChemicalService.ensureSupabaseInitialized();

      // Calculate the cutoff date
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() + days);

      const { data, error } = await supabaseService.select('chemicals', '*', {
        is_active: true,
        expiration_date: { operator: 'lte', value: cutoffDate.toISOString() }
      });
      if (error) throw error;

      // Filter out already expired chemicals and sort by expiration date
      const expiringSoon = (data || []).filter(chemical => {
        const expirationDate = new Date(chemical.expiration_date);
        return expirationDate > new Date(); // Not yet expired
      }).sort((a, b) => new Date(a.expiration_date) - new Date(b.expiration_date));

      return expiringSoon;
    } catch (error) {
      console.error('Supabase Error [GET] chemicals expiring soon:', error);
      throw error;
    }
  },

  // Mark a chemical as ordered
  markChemicalAsOrdered: async (id, expectedDeliveryDate) => {
    try {
      await ChemicalService.ensureSupabaseInitialized();
      const { data, error } = await supabaseService.update('chemicals', id, {
        reorder_status: 'ordered',
        expected_delivery_date: expectedDeliveryDate,
        ordered_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      });
      if (error) throw error;
      return data && data.length > 0 ? data[0] : null;
    } catch (error) {
      console.error(`Supabase Error [POST] chemical ${id} mark ordered:`, error);
      throw error;
    }
  },

  // Mark a chemical as delivered
  markChemicalAsDelivered: async (id, receivedQuantity = null) => {
    try {
      await ChemicalService.ensureSupabaseInitialized();

      const updateData = {
        reorder_status: 'delivered',
        delivered_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      // Add received quantity if provided
      if (receivedQuantity !== null) {
        updateData.received_quantity = receivedQuantity;
        // Update current quantity if received quantity is provided
        const chemical = await ChemicalService.getChemicalById(id);
        if (chemical) {
          updateData.current_quantity = (chemical.current_quantity || 0) + receivedQuantity;
        }
      }

      const { data, error } = await supabaseService.update('chemicals', id, updateData);
      if (error) throw error;
      return data && data.length > 0 ? data[0] : null;
    } catch (error) {
      console.error(`Supabase Error [POST] chemical ${id} mark delivered:`, error);
      throw error;
    }
  }
};

export default ChemicalService;
