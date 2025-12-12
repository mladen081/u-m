// src/hooks/useWebSocket.js

import { useEffect, useRef, useState, useCallback } from 'react';
import TokenManager from '../utils/tokenManager';

const useWebSocket = (onMessage, onClearAll) => {
  const ws = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const reconnectTimeout = useRef(null);
  const reconnectAttempts = useRef(0);
  const shouldReconnect = useRef(true);

  const connect = useCallback(() => {
    if (!shouldReconnect.current) return;
    
    const token = TokenManager.getAccessToken();
    if (!token) return;

    if (ws.current?.readyState === WebSocket.OPEN || ws.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = import.meta.env.DEV ? 'localhost:8000' : window.location.host;
    const wsUrl = `${protocol}//${host}/ws/chat/?token=${encodeURIComponent(token)}`;

    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      setIsConnected(true);
      reconnectAttempts.current = 0;
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.action === 'clear_all') {
        onClearAll();
      } else if (data.action === 'new_message') {
        onMessage(data);
      }
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      
      if (shouldReconnect.current && reconnectAttempts.current < 5) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
        reconnectTimeout.current = setTimeout(() => {
          reconnectAttempts.current += 1;
          connect();
        }, delay);
      }
    };

    ws.current.onerror = () => {
      ws.current?.close();
    };
  }, [onMessage, onClearAll]);

  const disconnect = useCallback(() => {
    shouldReconnect.current = false;
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
  }, []);

  const sendMessage = useCallback((message) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ message }));
    }
  }, []);

  useEffect(() => {
    shouldReconnect.current = true;
    connect();
    
    return () => {
      disconnect();
    };
  }, []);

  return { isConnected, sendMessage };
};

export default useWebSocket;