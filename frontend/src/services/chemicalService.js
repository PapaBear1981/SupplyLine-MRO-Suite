import { supabase, formatSupabaseResponse } from './supabase';

const ChemicalService = {
  // Get all chemicals
  getAllChemicals: async () => {
    try {
      const { data, error } = await supabase
        .from('chemicals')
        .select('*')
        .eq('is_archived', false)
        .order('part_number', { ascending: true });

      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error('Supabase Error [GET] chemicals:', error);
      throw error;
    }
  },

  // Get chemical by ID
  getChemicalById: async (id) => {
    try {
      const { data, error } = await supabase
        .from('chemicals')
        .select('*')
        .eq('id', id)
        .single();

      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error(`Supabase Error [GET] chemical ${id}:`, error);
      throw error;
    }
  },

  // Create new chemical
  createChemical: async (chemicalData) => {
    try {
      const { data, error } = await supabase
        .from('chemicals')
        .insert([{
          ...chemicalData,
          created_at: new Date().toISOString(),
          is_archived: false
        }])
        .select()
        .single();

      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error('Supabase Error [POST] chemicals:', error);
      throw error;
    }
  },

  // Update chemical
  updateChemical: async (id, chemicalData) => {
    try {
      const { data, error } = await supabase
        .from('chemicals')
        .update({
          ...chemicalData,
          updated_at: new Date().toISOString()
        })
        .eq('id', id)
        .select()
        .single();

      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error(`Supabase Error [PUT] chemical ${id}:`, error);
      throw error;
    }
  },

  // Delete chemical
  deleteChemical: async (id) => {
    try {
      const { data, error } = await supabase
        .from('chemicals')
        .delete()
        .eq('id', id)
        .select()
        .single();

      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error(`Supabase Error [DELETE] chemical ${id}:`, error);
      throw error;
    }
  },

  // Search chemicals
  searchChemicals: async (query) => {
    try {
      const { data, error } = await supabase
        .from('chemicals')
        .select('*')
        .eq('is_archived', false)
        .or(`part_number.ilike.%${query}%,description.ilike.%${query}%,manufacturer.ilike.%${query}%,lot_number.ilike.%${query}%`)
        .order('part_number', { ascending: true });

      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error(`Supabase Error [GET] chemicals search ${query}:`, error);
      throw error;
    }
  },

  // Issue chemical
  issueChemical: async (id, data) => {
    try {
      // First, create the issuance record
      const { data: issuanceData, error: issuanceError } = await supabase
        .from('chemical_issuances')
        .insert([{
          chemical_id: id,
          user_id: data.user_id,
          quantity_issued: data.quantity_issued,
          issued_date: new Date().toISOString(),
          purpose: data.purpose || null,
          notes: data.notes || null
        }])
        .select()
        .single();

      if (issuanceError) throw issuanceError;

      // Then update the chemical quantity
      const { data: chemicalData, error: chemicalError } = await supabase
        .from('chemicals')
        .update({
          current_quantity: data.new_quantity,
          updated_at: new Date().toISOString()
        })
        .eq('id', id)
        .select()
        .single();

      return formatSupabaseResponse(chemicalData, chemicalError);
    } catch (error) {
      console.error(`Supabase Error [POST] chemical ${id} issue:`, error);
      throw error;
    }
  },

  // Get chemical issuances
  getChemicalIssuances: async (id) => {
    try {
      const { data, error } = await supabase
        .from('chemical_issuances')
        .select(`
          *,
          users:user_id (
            employee_number,
            first_name,
            last_name,
            department
          )
        `)
        .eq('chemical_id', id)
        .order('issued_date', { ascending: false });

      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error(`Supabase Error [GET] chemical ${id} issuances:`, error);
      throw error;
    }
  },

  // Get all issuances
  getAllIssuances: async (filters = {}) => {
    try {
      let query = supabase
        .from('chemical_issuances')
        .select(`
          *,
          chemicals:chemical_id (
            part_number,
            description,
            manufacturer
          ),
          users:user_id (
            employee_number,
            first_name,
            last_name,
            department
          )
        `)
        .order('issued_date', { ascending: false });

      // Apply filters if provided
      if (filters.start_date) {
        query = query.gte('issued_date', filters.start_date);
      }
      if (filters.end_date) {
        query = query.lte('issued_date', filters.end_date);
      }
      if (filters.user_id) {
        query = query.eq('user_id', filters.user_id);
      }
      if (filters.chemical_id) {
        query = query.eq('chemical_id', filters.chemical_id);
      }

      const { data, error } = await query;
      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error('Supabase Error [GET] all issuances:', error);
      throw error;
    }
  },

  // Archive a chemical
  archiveChemical: async (id, reason) => {
    try {
      const { data, error } = await supabase
        .from('chemicals')
        .update({
          is_archived: true,
          archive_reason: reason,
          archived_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .eq('id', id)
        .select()
        .single();

      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error(`Supabase Error [POST] chemical ${id} archive:`, error);
      throw error;
    }
  },

  // Unarchive a chemical
  unarchiveChemical: async (id) => {
    try {
      const { data, error } = await supabase
        .from('chemicals')
        .update({
          is_archived: false,
          archive_reason: null,
          archived_at: null,
          updated_at: new Date().toISOString()
        })
        .eq('id', id)
        .select()
        .single();

      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error(`Supabase Error [POST] chemical ${id} unarchive:`, error);
      throw error;
    }
  },

  // Get archived chemicals
  getArchivedChemicals: async (filters = {}) => {
    try {
      let query = supabase
        .from('chemicals')
        .select('*')
        .eq('is_archived', true)
        .order('archived_at', { ascending: false });

      // Apply filters if provided
      if (filters.part_number) {
        query = query.ilike('part_number', `%${filters.part_number}%`);
      }
      if (filters.manufacturer) {
        query = query.ilike('manufacturer', `%${filters.manufacturer}%`);
      }

      const { data, error } = await query;
      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error('Supabase Error [GET] archived chemicals:', error);
      throw error;
    }
  },

  // Get waste analytics
  getWasteAnalytics: async (timeframe = 'month', part_number = null) => {
    try {
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

      let query = supabase
        .from('chemical_issuances')
        .select(`
          *,
          chemicals:chemical_id (
            part_number,
            description,
            manufacturer
          )
        `)
        .gte('issued_date', startDate.toISOString())
        .lte('issued_date', endDate.toISOString());

      if (part_number) {
        query = query.eq('chemicals.part_number', part_number);
      }

      const { data, error } = await query;
      return formatSupabaseResponse(data, error);
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

      const { data, error } = await supabase
        .from('chemical_issuances')
        .select(`
          *,
          chemicals!inner (
            part_number,
            description,
            manufacturer
          )
        `)
        .eq('chemicals.part_number', part_number)
        .gte('issued_date', startDate.toISOString())
        .lte('issued_date', endDate.toISOString())
        .order('issued_date', { ascending: false });

      return formatSupabaseResponse(data, error);
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

      // Get all chemicals with this part number
      const { data: chemicals, error: chemicalsError } = await supabase
        .from('chemicals')
        .select('*')
        .eq('part_number', part_number);

      if (chemicalsError) throw chemicalsError;

      // Get all issuances for this part number
      const { data: issuances, error: issuancesError } = await supabase
        .from('chemical_issuances')
        .select(`
          *,
          chemicals!inner (
            part_number,
            description,
            manufacturer
          )
        `)
        .eq('chemicals.part_number', part_number)
        .order('issued_date', { ascending: false });

      if (issuancesError) throw issuancesError;

      return {
        chemicals,
        issuances,
        total_chemicals: chemicals.length,
        total_issuances: issuances.length,
        total_quantity_issued: issuances.reduce((sum, issuance) => sum + (issuance.quantity_issued || 0), 0)
      };
    } catch (error) {
      console.error('Supabase Error [GET] part number analytics:', error);
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
      const { data, error } = await supabase
        .from('chemicals')
        .select('*')
        .eq('is_archived', false)
        .or('reorder_status.eq.needed,reorder_status.eq.urgent')
        .order('part_number', { ascending: true });

      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error('Supabase Error [GET] chemicals needing reorder:', error);
      throw error;
    }
  },

  // Get chemicals that are on order
  getChemicalsOnOrder: async () => {
    try {
      const { data, error } = await supabase
        .from('chemicals')
        .select('*')
        .eq('is_archived', false)
        .eq('reorder_status', 'ordered')
        .order('expected_delivery_date', { ascending: true });

      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error('Supabase Error [GET] chemicals on order:', error);
      throw error;
    }
  },

  // Get chemicals that are expiring soon
  getChemicalsExpiringSoon: async (days = 30) => {
    try {
      const futureDate = new Date();
      futureDate.setDate(futureDate.getDate() + days);

      const { data, error } = await supabase
        .from('chemicals')
        .select('*')
        .eq('is_archived', false)
        .not('expiration_date', 'is', null)
        .lte('expiration_date', futureDate.toISOString())
        .order('expiration_date', { ascending: true });

      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error('Supabase Error [GET] chemicals expiring soon:', error);
      throw error;
    }
  },

  // Mark a chemical as ordered
  markChemicalAsOrdered: async (id, expectedDeliveryDate) => {
    try {
      const { data, error } = await supabase
        .from('chemicals')
        .update({
          reorder_status: 'ordered',
          expected_delivery_date: expectedDeliveryDate,
          order_date: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .eq('id', id)
        .select()
        .single();

      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error(`Supabase Error [POST] chemical ${id} mark ordered:`, error);
      throw error;
    }
  },

  // Mark a chemical as delivered
  markChemicalAsDelivered: async (id, receivedQuantity = null) => {
    try {
      const updateData = {
        reorder_status: 'in_stock',
        delivery_date: new Date().toISOString(),
        expected_delivery_date: null,
        updated_at: new Date().toISOString()
      };

      // Add received quantity if provided
      if (receivedQuantity !== null) {
        updateData.current_quantity = receivedQuantity;
      }

      const { data, error } = await supabase
        .from('chemicals')
        .update(updateData)
        .eq('id', id)
        .select()
        .single();

      return formatSupabaseResponse(data, error);
    } catch (error) {
      console.error(`Supabase Error [POST] chemical ${id} mark delivered:`, error);
      throw error;
    }
  }
};

export default ChemicalService;
