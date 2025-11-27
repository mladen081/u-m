// src/services/api.js

import axios from 'axios';
import TokenManager from '../utils/tokenManager';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

api.interceptors.request.use(
  (config) => {
    const token = TokenManager.getAccessToken();
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (!error.response || error.response.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        })
        .catch(err => {
          return Promise.reject(err);
        });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    const refreshToken = TokenManager.getRefreshToken();

    if (!refreshToken) {
      TokenManager.clearTokens();
      isRefreshing = false;
      
      window.dispatchEvent(new Event('auth:logout'));
      
      return Promise.reject(error);
    }

    try {
      const response = await axios.post(
        '/api/auth/token/refresh/',
        { refresh: refreshToken },
        { headers: { 'Content-Type': 'application/json' } }
      );

      const { access, refresh: newRefresh } = response.data.data;

      if (newRefresh) {
        TokenManager.setTokens(access, newRefresh);
      } else {
        TokenManager.updateAccessToken(access);
      }

      api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      originalRequest.headers.Authorization = `Bearer ${access}`;

      processQueue(null, access);
      isRefreshing = false;

      return api(originalRequest);

    } catch (refreshError) {
      processQueue(refreshError, null);
      isRefreshing = false;
      
      TokenManager.clearTokens();
      
      window.dispatchEvent(new Event('auth:logout'));
      
      return Promise.reject(refreshError);
    }
  }
);

export default api;