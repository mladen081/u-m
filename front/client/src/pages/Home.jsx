// src/pages/Home.jsx

import { useState, useEffect } from 'react';
import useWebSocket from '../hooks/useWebSocket';

function Home() {
  const [onlineUsers, setOnlineUsers] = useState([]);

  const handleNewMessage = () => {};
  const handleClearAll = () => {};
  const handleUserListUpdate = (users) => {
    setOnlineUsers(users);
  };

  useWebSocket(handleNewMessage, handleClearAll, handleUserListUpdate);

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Home</h1>
      </div>
      <p>Hello</p>
      <p>Online users: {onlineUsers.join(', ') || 'pending...'}</p>
    </div>
  );
}

export default Home;