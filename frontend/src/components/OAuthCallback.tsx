import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const OAuthCallback: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handleAuthentication = () => {
      try {
        // Get token from URL query parameters
        const params = new URLSearchParams(location.search);
        const token = params.get('token');

        if (token) {
          // Login with the token
          console.log('Token received from URL params:', token);
          login(token);
          navigate('/books');
        } else {
          // No token in URL params, try server API as fallback
          getTokenFromServer();
        }
      } catch (err) {
        console.error('Error processing authentication:', err);
        setError('Authentication failed. Please try again.');
      }
    };

    const getTokenFromServer = async () => {
      try {
        // Fallback: try to get token from server
        const response = await axios.post('http://localhost:8000/auth/token/', {}, {
          withCredentials: true
        });

        if (response.data && response.data.key) {
          console.log('Token received from server API');
          login(response.data.key);
          navigate('/books');
        } else {
          setError('Failed to retrieve authentication token.');
        }
      } catch (err) {
        console.error('OAuth server token error:', err);
        setError('Authentication failed. Please try again.');
      }
    };
    
    handleAuthentication();
  }, [login, navigate, location]);

  if (error) {
    return (
      <div className="container mt-5">
        <div className="alert alert-danger">{error}</div>
        <button 
          className="btn btn-primary"
          onClick={() => navigate('/')}
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