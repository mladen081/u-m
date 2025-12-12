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

  async deleteAllMessages() {
    try {
      const response = await api.delete('/chat/messages/delete-all/');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to delete messages');
    }
  },
};

export default chatService;