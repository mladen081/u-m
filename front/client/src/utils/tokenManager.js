// src/utils/tokenManager.js

class TokenManager {
  static STORAGE_KEYS = {
    ACCESS: 'enc_access_token',
    REFRESH: 'enc_refresh_token',
    USER: 'user_data',
  };

  static setTokens(access, refresh, user = null) {
    localStorage.setItem(this.STORAGE_KEYS.ACCESS, access);
    localStorage.setItem(this.STORAGE_KEYS.REFRESH, refresh);
    
    if (user) {
      localStorage.setItem(this.STORAGE_KEYS.USER, JSON.stringify(user));
    }
  }

  static getAccessToken() {
    return localStorage.getItem(this.STORAGE_KEYS.ACCESS);
  }

  static getRefreshToken() {
    return localStorage.getItem(this.STORAGE_KEYS.REFRESH);
  }

  static getUser() {
    const userData = localStorage.getItem(this.STORAGE_KEYS.USER);
    return userData ? JSON.parse(userData) : null;
  }

  static updateAccessToken(access) {
    localStorage.setItem(this.STORAGE_KEYS.ACCESS, access);
  }

  static clearTokens() {
    localStorage.removeItem(this.STORAGE_KEYS.ACCESS);
    localStorage.removeItem(this.STORAGE_KEYS.REFRESH);
    localStorage.removeItem(this.STORAGE_KEYS.USER);
  }

  static isAuthenticated() {
    return !!this.getAccessToken() && !!this.getRefreshToken();
  }

  static isAdmin() {
    const user = this.getUser();
    return user?.is_admin === true;
  }
}

export default TokenManager;