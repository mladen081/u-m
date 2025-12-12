// src/pages/Chat.jsx

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import useWebSocket from '../hooks/useWebSocket';
import chatService from '../services/chatService';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef(null);
  const { user } = useAuth();

  const handleNewMessage = (data) => {
    setMessages(prev => [...prev, data]);
  };

  const handleClearAll = () => {
    setMessages([]);
  };

  const { isConnected, sendMessage } = useWebSocket(handleNewMessage, handleClearAll);

  useEffect(() => {
    const loadMessages = async () => {
      try {
        const data = await chatService.getMessages(50);
        setMessages(data);
      } catch (error) {
        console.error('Failed to load messages:', error);
      } finally {
        setLoading(false);
      }
    };

    loadMessages();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = inputMessage.trim();
    
    if (!trimmed || !isConnected) return;
    
    sendMessage(trimmed);
    setInputMessage('');
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const groupMessagesByDate = (messages) => {
    const groups = {};
    messages.forEach(msg => {
      const date = formatDate(msg.timestamp);
      if (!groups[date]) {
        groups[date] = [];
      }
      groups[date].push(msg);
    });
    return groups;
  };

  if (loading) {
    return (
      <div className="loading-container">
        <p>Loading chat...</p>
      </div>
    );
  }

  const groupedMessages = groupMessagesByDate(messages);

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>Global Chat</h1>
        <span className={`status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '● Connected' : '○ Disconnected'}
        </span>
      </div>

      <div className="messages-container">
        {Object.entries(groupedMessages).map(([date, msgs]) => (
          <div key={date}>
            <div className="date-separator">{date}</div>
            {msgs.map((msg) => (
              <div
                key={msg.message_id || msg.id}
                className={`message-wrapper ${msg.user_id === user?.id ? 'own' : 'other'}`}
              >
                <div className="message">
                  <span className="message-username">{msg.username}</span>
                  <p className="message-content">{msg.message}</p>
                  <span className="message-time">{formatTime(msg.timestamp)}</span>
                </div>
              </div>
            ))}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="message-form">
        <label htmlFor="message-input">Type your message</label>
        <input
          id="message-input"
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type a message..."
          maxLength={1000}
          disabled={!isConnected}
        />
        <button type="submit" disabled={!isConnected || !inputMessage.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

export default Chat;