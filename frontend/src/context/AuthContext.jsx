import React, { createContext, useState, useEffect, useContext } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('token'));

  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user');
    try {
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  });


  const login = async (email, password) => {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    const result = await res.json();

    if (res.ok && result.token) {
      localStorage.setItem('token', result.token);
      localStorage.setItem('user', JSON.stringify(result));
      setToken(result.token);
      setUser(result);
      return { success: true };
    } else {
      return { success: false, message: result.message || 'Credenciales incorrectas.' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  // Custom authenticated fetch wrapper that handles tokens and automatic 401/403 session expirations
  const authFetch = async (url, options = {}) => {
    const headers = {
      ...options.headers,
    };

    // Only set Content-Type to JSON if body is NOT FormData (to let browser manage multipart boundaries)
    if (options.body && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const res = await fetch(url, { ...options, headers });

      // Auto logout on unauthorized response
      if ((res.status === 401 || res.status === 403) && !url.includes('/api/login')) {
        logout();
      }
      return res;
    } catch (error) {
      console.error('API Fetch Error:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout, authFetch }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
