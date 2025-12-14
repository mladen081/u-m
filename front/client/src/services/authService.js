// src/services/authService.js

import api from './api';

const authService = {
  async login(username, password) {
    try {
      const response = await api.post('/auth/login/', {
        username,
        password,
      });

      const { user } = response.data.data;
      localStorage.setItem('user', JSON.stringify(user));

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

      const { user } = response.data.data;
      localStorage.setItem('user', JSON.stringify(user));

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

  async logout() {
    try {
      await api.post('/auth/logout/');
      localStorage.removeItem('user');
    } catch (error) {
      localStorage.removeItem('user');
    }
  },

  getCurrentUser() {
    const userData = localStorage.getItem('user');
    return userData ? JSON.parse(userData) : null;
  },

  isAuthenticated() {
    return !!this.getCurrentUser();
  },

  isAdmin() {
    const user = this.getCurrentUser();
    return user?.is_admin === true;
  },
};

export default authService;