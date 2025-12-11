// src/services/chatService.js

import api from './api';

const chatService = {
  async getMessages(limit = 50) {
    try {
      const response = await api.get(`/chat/messages/?limit=${limit}`);
      return response.data.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch messages');
    }
  },
};

export default chatService;