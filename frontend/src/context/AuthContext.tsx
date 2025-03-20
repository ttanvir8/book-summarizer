import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

// Interface for user data
interface User {
  id: number;
  email: string;
  username: string;
  name?: string;
  picture?: string;
}

// Interface for authentication context
interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (token: string) => Promise<boolean>;
  logout: () => void;
  setAuthToken: (token: string | null) => void;
}

// Create context with default values
const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  isAuthenticated: false,
  loading: true,
  login: () => Promise.resolve(false),
  logout: () => {},
  setAuthToken: () => {},
});

// Hook for using auth context
export const useAuth = () => useContext(AuthContext);

// Provider props interface
interface AuthProviderProps {
  children: ReactNode;
}

// Authentication provider component
export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Set auth token in axios header and local storage
  const setAuthToken = (token: string | null) => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
      localStorage.setItem('token', token);
    } else {
      delete axios.defaults.headers.common['Authorization'];
      localStorage.removeItem('token');
    }
  };

  // Login function
  const login = async (token: string): Promise<boolean> => {
    try {
      setToken(token);
      setAuthToken(token);
      
      // Create a user object - in a real app, you'd likely fetch this from an API
      const userData: User = {
        id: 1,
        email: 'user@example.com',
        username: 'user',
      };
      
      setUser(userData);
      return true;
    } catch (error) {
      console.error('Error during login:', error);
      return false;
    }
  };

  // Logout function
  const logout = () => {
    setUser(null);
    setToken(null);
    setAuthToken(null);
  };

  // Check if user is already logged in on component mount
  useEffect(() => {
    const checkAuth = async () => {
      const storedToken = localStorage.getItem('token');
      
      if (storedToken) {
        try {
          setAuthToken(storedToken);
          setToken(storedToken);
          
          // For a real implementation, you might want to:
          // 1. Verify the token with your backend
          // 2. Fetch the user data
          
          // For this example, we'll create a basic user
          const userData: User = {
            id: 1,
            email: 'user@example.com',
            username: 'user',
          };
          
          setUser(userData);
        } catch (error) {
          console.error('Error loading auth:', error);
          logout();
        }
      }
      
      setLoading(false);
    };
    
    checkAuth();
  }, []);

  // Context value
  const value = {
    user,
    token,
    isAuthenticated: !!user,
    loading,
    login,
    logout,
    setAuthToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext; 