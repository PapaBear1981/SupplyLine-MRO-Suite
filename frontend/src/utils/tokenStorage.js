/**
 * JWT Token Storage Utility
 * 
 * Handles secure storage and management of JWT tokens in localStorage
 * with proper error handling and token validation.
 */

const TOKEN_KEYS = {
  ACCESS_TOKEN: 'supplyline_access_token',
  REFRESH_TOKEN: 'supplyline_refresh_token',
  TOKEN_EXPIRY: 'supplyline_token_expiry',
  USER_DATA: 'supplyline_user_data'
};

class TokenStorage {
  /**
   * Store JWT tokens and user data after successful login
   * @param {Object} loginResponse - Response from login API
   */
  static storeTokens(loginResponse) {
    try {
      console.log('Storing tokens from login response:', loginResponse);
      const { access_token, refresh_token, expires_in, user } = loginResponse;

      if (!access_token || !refresh_token) {
        console.error('Invalid login response: missing tokens', { access_token: !!access_token, refresh_token: !!refresh_token });
        return false;
      }

      // Calculate expiry time (current time + expires_in seconds)
      const expiryTime = Date.now() + (expires_in * 1000);

      // Store tokens and user data
      localStorage.setItem(TOKEN_KEYS.ACCESS_TOKEN, access_token);
      localStorage.setItem(TOKEN_KEYS.REFRESH_TOKEN, refresh_token);
      localStorage.setItem(TOKEN_KEYS.TOKEN_EXPIRY, expiryTime.toString());
      localStorage.setItem(TOKEN_KEYS.USER_DATA, JSON.stringify(user));

      console.log('JWT tokens stored successfully', {
        access_token_length: access_token.length,
        refresh_token_length: refresh_token.length,
        expires_in,
        user_id: user?.id
      });
      return true;
    } catch (error) {
      console.error('Error storing tokens:', error);
      return false;
    }
  }

  /**
   * Get the current access token
   * @returns {string|null} Access token or null if not found/expired
   */
  static getAccessToken() {
    try {
      const token = localStorage.getItem(TOKEN_KEYS.ACCESS_TOKEN);
      const expiry = localStorage.getItem(TOKEN_KEYS.TOKEN_EXPIRY);

      if (!token || !expiry) {
        return null;
      }

      // Check if token is expired
      if (Date.now() >= parseInt(expiry)) {
        console.log('Access token expired');
        return null;
      }

      return token;
    } catch (error) {
      console.error('Error getting access token:', error);
      return null;
    }
  }

  /**
   * Get the refresh token
   * @returns {string|null} Refresh token or null if not found
   */
  static getRefreshToken() {
    try {
      return localStorage.getItem(TOKEN_KEYS.REFRESH_TOKEN);
    } catch (error) {
      console.error('Error getting refresh token:', error);
      return null;
    }
  }

  /**
   * Get stored user data
   * @returns {Object|null} User data or null if not found
   */
  static getUserData() {
    try {
      const userData = localStorage.getItem(TOKEN_KEYS.USER_DATA);
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error getting user data:', error);
      return null;
    }
  }

  /**
   * Update stored tokens after refresh
   * @param {Object} refreshResponse - Response from token refresh API
   */
  static updateTokens(refreshResponse) {
    try {
      const { access_token, refresh_token, expires_in } = refreshResponse;
      
      if (!access_token) {
        console.error('Invalid refresh response: missing access token');
        return false;
      }

      // Calculate new expiry time
      const expiryTime = Date.now() + (expires_in * 1000);

      // Update tokens
      localStorage.setItem(TOKEN_KEYS.ACCESS_TOKEN, access_token);
      localStorage.setItem(TOKEN_KEYS.TOKEN_EXPIRY, expiryTime.toString());
      
      // Update refresh token if provided
      if (refresh_token) {
        localStorage.setItem(TOKEN_KEYS.REFRESH_TOKEN, refresh_token);
      }

      console.log('JWT tokens updated successfully');
      return true;
    } catch (error) {
      console.error('Error updating tokens:', error);
      return false;
    }
  }

  /**
   * Check if user is authenticated (has valid tokens)
   * @returns {boolean} True if authenticated, false otherwise
   */
  static isAuthenticated() {
    const accessToken = this.getAccessToken();
    const refreshToken = this.getRefreshToken();
    
    // User is authenticated if they have either a valid access token or a refresh token
    return !!(accessToken || refreshToken);
  }

  /**
   * Check if access token is expired but refresh token exists
   * @returns {boolean} True if token needs refresh, false otherwise
   */
  static needsTokenRefresh() {
    const accessToken = this.getAccessToken();
    const refreshToken = this.getRefreshToken();
    
    // Need refresh if no access token but have refresh token
    return !accessToken && !!refreshToken;
  }

  /**
   * Clear all stored tokens and user data (logout)
   */
  static clearTokens() {
    try {
      localStorage.removeItem(TOKEN_KEYS.ACCESS_TOKEN);
      localStorage.removeItem(TOKEN_KEYS.REFRESH_TOKEN);
      localStorage.removeItem(TOKEN_KEYS.TOKEN_EXPIRY);
      localStorage.removeItem(TOKEN_KEYS.USER_DATA);
      
      console.log('JWT tokens cleared successfully');
    } catch (error) {
      console.error('Error clearing tokens:', error);
    }
  }

  /**
   * Get Authorization header value for API requests
   * @returns {string|null} Authorization header value or null
   */
  static getAuthHeader() {
    const token = this.getAccessToken();
    const result = token ? `Bearer ${token}` : null;
    console.log('getAuthHeader called:', { hasToken: !!token, tokenLength: token?.length });
    return result;
  }

  /**
   * Debug method to log current token status
   */
  static debugTokenStatus() {
    console.log('=== Token Storage Debug ===');
    console.log('Access Token:', this.getAccessToken() ? 'Present' : 'Missing');
    console.log('Refresh Token:', this.getRefreshToken() ? 'Present' : 'Missing');
    console.log('User Data:', this.getUserData() ? 'Present' : 'Missing');
    console.log('Is Authenticated:', this.isAuthenticated());
    console.log('Needs Refresh:', this.needsTokenRefresh());
    console.log('========================');
  }
}

export default TokenStorage;
