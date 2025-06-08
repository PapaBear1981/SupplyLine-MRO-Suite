import { createClient } from '@supabase/supabase-js'

// Supabase configuration
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://illoycgawzqyvcsvdtoc.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlsbG95Y2dhd3pxeXZjc3ZkdG9jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg4MDU2MzMsImV4cCI6MjA2NDM4MTYzM30.rHfX3kgxc7cw2Yy3soChlqjVJ1zYfImsRweYVNKpFrY'

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  }
})

// Helper function to handle Supabase errors
export const handleSupabaseError = (error) => {
  console.error('Supabase Error:', error)
  
  if (error?.message) {
    throw new Error(error.message)
  }
  
  if (error?.error_description) {
    throw new Error(error.error_description)
  }
  
  throw new Error('An unexpected error occurred')
}

// Helper function to format Supabase response
export const formatSupabaseResponse = (data, error) => {
  if (error) {
    handleSupabaseError(error)
  }
  
  return data
}

export default supabase
