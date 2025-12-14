// src/services/api.js

import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve();
    }
  });
  
  failedQueue = [];
};

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
        .then(() => {
          return api(originalRequest);
        })
        .catch(err => {
          return Promise.reject(err);
        });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      await axios.post(
        '/api/auth/token/refresh/',
        {},
        { 
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true,
        }
      );

      processQueue(null);
      isRefreshing = false;

      return api(originalRequest);

    } catch (refreshError) {
      processQueue(refreshError);
      isRefreshing = false;
      
      window.dispatchEvent(new Event('auth:logout'));
      
      return Promise.reject(refreshError);
    }
  }
);

export default api;