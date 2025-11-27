// src/services/authService.js

import api from './api';
import TokenManager from '../utils/tokenManager';

const authService = {
  async login(username, password) {
    try {
      const response = await api.post('/auth/login/', {
        username,
        password,
      });

      const { access, refresh, user } = response.data.data;

      TokenManager.setTokens(access, refresh, user);

      return user;
    } catch (error) {
      const message = error.response?.data?.message || 'Login failed';
      throw new Error(message);
    }
  },

  async register(username, email, password) {
    try {
      const response = await api.post('/auth/register/', {
        username,
        email,
        password,
      });

      const { access, refresh, user } = response.data.data;

      TokenManager.setTokens(access, refresh, user);

      return user;
    } catch (error) {
      const data = error.response?.data;
      
      if (data?.errors) {
        const errors = Object.entries(data.errors)
          .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
          .join('\n');
        throw new Error(errors || data.message);
      }
      
      const message = data?.message || 'Registration failed';
      throw new Error(message);
    }
  },

  logout() {
    TokenManager.clearTokens();
  },

  isAuthenticated() {
    return TokenManager.isAuthenticated();
  },

  getCurrentUser() {
    return TokenManager.getUser();
  },

  isAdmin() {
    return TokenManager.isAdmin();
  },
};

export default authService;