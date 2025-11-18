import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load user from localStorage on mount
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Error loading user from localStorage:', error);
        localStorage.removeItem('currentUser');
      }
    }
    setLoading(false);
  }, []);

  const login = (userData) => {
    setUser(userData);
    localStorage.setItem('currentUser', JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('currentUser');
  };

  const hasPermission = (resource, action) => {
    if (!user || !user.role) return false;

    const permissions = {
      admin: {
        flights: ['read', 'create', 'update', 'delete', 'upload'],
        reservations: ['read', 'create', 'update', 'delete', 'upload'],
        operations: ['read', 'create', 'update', 'delete', 'upload'],
        users: ['read', 'create', 'update', 'delete'],
        logs: ['read'],
        management: ['read']
      },
      flight: {
        flights: ['read', 'create', 'update', 'delete', 'upload'],
        reservations: [],
        operations: [],
        users: [],
        logs: [],
        management: []
      },
      reservation: {
        flights: [],
        reservations: ['read', 'create', 'update', 'delete', 'upload'],
        operations: [],
        users: [],
        logs: [],
        management: []
      },
      operation: {
        flights: [],
        reservations: [],
        operations: ['read', 'create', 'update', 'delete', 'upload'],
        users: [],
        logs: [],
        management: []
      },
      management: {
        flights: ['read'],
        reservations: ['read'],
        operations: ['read'],
        users: [],
        logs: [],
        management: ['read']
      }
    };

    const rolePermissions = permissions[user.role] || {};
    const resourcePermissions = rolePermissions[resource] || [];
    return resourcePermissions.includes(action);
  };

  const canAccessPage = (page) => {
    if (!user || !user.role) return false;

    const pageAccess = {
      admin: {
        dashboard: true,
        flights: true,
        reservations: true,
        operations: true,
        management: true,
        admin: true
      },
      flight: {
        dashboard: true,
        flights: true,
        reservations: false,
        operations: false,
        management: false,
        admin: false
      },
      reservation: {
        dashboard: true,
        flights: false,
        reservations: true,
        operations: false,
        management: false,
        admin: false
      },
      operation: {
        dashboard: true,
        flights: false,
        reservations: false,
        operations: true,
        management: false,
        admin: false
      },
      management: {
        dashboard: true,
        flights: true,
        reservations: true,
        operations: true,
        management: true,
        admin: false
      }
    };

    const roleAccess = pageAccess[user.role] || {};
    return roleAccess[page] || false;
  };

  const value = {
    user,
    loading,
    login,
    logout,
    hasPermission,
    canAccessPage,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
