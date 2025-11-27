// src/components/Navbar.jsx

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const { user, logout, isAuthenticated } = useAuth();

  useEffect(() => {
    const handleEsc = (event) => {
      if (event.key === 'Escape') setIsOpen(false);
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, []);

  const handleLogout = () => {
    setIsOpen(false);
    logout();
  };

  return (
    <>
      <nav className="navbar">
        <div
          className={`menu-toggle ${isOpen ? 'open' : ''}`}
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle menu"
          aria-expanded={isOpen}
        >
          <span></span>
          <span></span>
          <span></span>
        </div>

        <ul className={`nav-links ${isOpen ? 'open' : ''}`}>
          {isAuthenticated() ? (
            <>
              <li className="user-info">
                <span className="username">{user?.username}</span>
                {user?.is_admin && <span className="badge-admin">Admin</span>}
              </li>
              <li>
                <Link to="/" onClick={() => setIsOpen(false)}>Home</Link>
              </li>
              {user?.is_admin && (
                <li>
                  <Link to="/specials" onClick={() => setIsOpen(false)}>Specials</Link>
                </li>
              )}
              <li>
                <button onClick={handleLogout} className="logout-btn">
                  Logout
                </button>
              </li>
            </>
          ) : (
            <>
              <li>
                <Link to="/login" onClick={() => setIsOpen(false)}>Login</Link>
              </li>
              <li>
                <Link to="/register" onClick={() => setIsOpen(false)}>Register</Link>
              </li>
            </>
          )}
        </ul>
      </nav>

      <div
        className={`overlay ${isOpen ? 'active' : ''}`}
        onClick={() => setIsOpen(false)}
      ></div>
    </>
  );
}

export default Navbar;