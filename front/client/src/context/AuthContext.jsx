// src/context/AuthContext.jsx

import { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const initAuth = () => {
      const currentUser = authService.getCurrentUser();
      if (currentUser) {
        setUser(currentUser);
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  useEffect(() => {
    const handleLogoutEvent = () => {
      setUser(null);
      navigate('/login');
    };

    window.addEventListener('auth:logout', handleLogoutEvent);

    return () => {
      window.removeEventListener('auth:logout', handleLogoutEvent);
    };
  }, [navigate]);

  const login = async (username, password) => {
    try {
      const userData = await authService.login(username, password);
      setUser(userData);
      navigate('/');
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const register = async (username, email, password) => {
    try {
      const userData = await authService.register(username, email, password);
      setUser(userData);
      navigate('/');
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    navigate('/login');
  };

  const isAdmin = () => {
    return user?.is_admin === true;
  };

  const isAuthenticated = () => {
    return !!user;
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAdmin,
    isAuthenticated,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  
  return context;
};

export default AuthContext;