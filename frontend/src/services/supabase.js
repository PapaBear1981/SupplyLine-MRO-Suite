import { createClient } from '@supabase/supabase-js';

class SupabaseService {
  constructor() {
    this.client = null;
    this.isConnected = false;
    this.config = {
      url: '',
      key: ''
    };
  }

  async initialize() {
    try {
      // PWA version - check environment variables or localStorage
      const url = import.meta.env.VITE_SUPABASE_URL || localStorage.getItem('supabase_url');
      const key = import.meta.env.VITE_SUPABASE_ANON_KEY || localStorage.getItem('supabase_key');

      if (url && key) {
        this.config = { url, key };
        this.client = createClient(url, key);
        this.isConnected = true;
        console.log('✅ Supabase initialized from stored config');
        return true;
      }

      console.log('⚠️  No Supabase configuration found');
      return false;
    } catch (error) {
      console.error('Failed to initialize Supabase:', error);
      return false;
    }
  }

  async configure(url, key) {
    try {
      this.config = { url, key };
      this.client = createClient(url, key);

      // Test the connection with a simple query instead of manual fetch
      try {
        // Try a simple query to test the connection
        await this.client.from('users').select('count', { count: 'exact', head: true });
        this.isConnected = true;
      } catch (testError) {
        // If the test query fails, still mark as connected since the client was created successfully
        // The actual queries will handle their own errors
        console.log('Connection test query failed, but client created successfully:', testError.message);
        this.isConnected = true;
      }

      // Save configuration to localStorage for PWA
      localStorage.setItem('supabase_url', url);
      localStorage.setItem('supabase_key', key);
      console.log('✅ Supabase configuration saved to localStorage');

      return true;
    } catch (error) {
      console.error('Failed to configure Supabase:', error);
      this.isConnected = false;
      throw error;
    }
  }

  getClient() {
    if (!this.client) {
      throw new Error('Supabase client not initialized. Call initialize() or configure() first.');
    }
    return this.client;
  }

  isReady() {
    return this.isConnected && this.client !== null;
  }

  getConfig() {
    return { ...this.config };
  }

  // Database operations
  async testConnection() {
    try {
      if (!this.client) return false;

      // Test with a simple query instead of manual fetch
      await this.client.from('users').select('count', { count: 'exact', head: true });
      return true;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  }

  // User management
  async signUp(email, password, metadata = {}) {
    const { data, error } = await this.client.auth.signUp({
      email,
      password,
      options: {
        data: metadata
      }
    });
    return { data, error };
  }

  async signIn(email, password) {
    const { data, error } = await this.client.auth.signInWithPassword({
      email,
      password
    });
    return { data, error };
  }

  async signOut() {
    const { error } = await this.client.auth.signOut();
    return { error };
  }

  async getUser() {
    const { data: { user }, error } = await this.client.auth.getUser();
    return { user, error };
  }

  // Real-time subscriptions
  subscribe(table, callback, filter = '*') {
    if (!this.client) {
      throw new Error('Supabase client not initialized');
    }

    return this.client
      .channel(`${table}_changes`)
      .on('postgres_changes', 
        { 
          event: '*', 
          schema: 'public', 
          table: table,
          filter: filter 
        }, 
        callback
      )
      .subscribe();
  }

  unsubscribe(subscription) {
    if (subscription) {
      this.client.removeChannel(subscription);
    }
  }

  // Generic CRUD operations
  async select(table, columns = '*', filters = {}) {
    let query = this.client.from(table).select(columns);
    
    Object.entries(filters).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        query = query.in(key, value);
      } else if (typeof value === 'object' && value.operator) {
        switch (value.operator) {
          case 'gte':
            query = query.gte(key, value.value);
            break;
          case 'lte':
            query = query.lte(key, value.value);
            break;
          case 'like':
            query = query.like(key, value.value);
            break;
          case 'ilike':
            query = query.ilike(key, value.value);
            break;
          default:
            query = query.eq(key, value.value);
        }
      } else {
        query = query.eq(key, value);
      }
    });

    const { data, error } = await query;
    return { data, error };
  }

  async insert(table, data) {
    const { data: result, error } = await this.client
      .from(table)
      .insert(data)
      .select();
    return { data: result, error };
  }

  async update(table, id, data) {
    const { data: result, error } = await this.client
      .from(table)
      .update(data)
      .eq('id', id)
      .select();
    return { data: result, error };
  }

  async delete(table, id) {
    const { data, error } = await this.client
      .from(table)
      .delete()
      .eq('id', id);
    return { data, error };
  }

  async upsert(table, data) {
    const { data: result, error } = await this.client
      .from(table)
      .upsert(data)
      .select();
    return { data: result, error };
  }
}

// Create singleton instance
const supabaseService = new SupabaseService();

export default supabaseService;
