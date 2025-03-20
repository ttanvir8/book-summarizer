import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Simple component that extracts token from URL and redirects
const OAuthCallback: React.FC = () => {
  const [processing, setProcessing] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const location = useLocation();
  const { login } = useAuth();
  
  useEffect(() => {
    const handleToken = async () => {
      try {
        console.log('OAuthCallback: Handling authentication');
        const params = new URLSearchParams(location.search);
        const token = params.get('token');
        
        if (!token) {
          console.error('No token found in URL');
          setError('Authentication failed: No token received');
          setProcessing(false);
          return;
        }
        
        // Set token directly in localStorage
        console.log('Setting token:', token);
        localStorage.setItem('token', token);
        
        // Also call login for state management
        await login(token);
        
        // Instead of using React Router, use direct location change
        // This ensures a complete page reload
        window.location.replace('/books');
      } catch (err) {
        console.error('Error in handleToken:', err);
        setError('Authentication failed. Please try again.');
        setProcessing(false);
      }
    };
    
    // Reset any cached state
    sessionStorage.removeItem('auth_processing');
    
    // Add a small delay to ensure state is cleared
    setTimeout(() => {
      handleToken();
    }, 100);
    
    // Clean up on unmount
    return () => {
      sessionStorage.removeItem('auth_processing');
    };
  }, [location.search, login]);
  
  if (error) {
    return (
      <div className="container mt-5">
        <div className="alert alert-danger">{error}</div>
        <button 
          className="btn btn-primary"
          onClick={() => window.location.href = '/'}
        >
          Return to Home
        </button>
      </div>
    );
  }
  
  return (
    <div className="container mt-5 text-center">
      <div className="spinner-border" role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
      <p className="mt-3">Completing authentication, please wait...</p>
    </div>
  );
};

export default OAuthCallback;