import React, { createContext, useState, useContext, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import {
  registerUser,
  getToken,
  googleRegister,
  googleLogin,
  setAgentVoice,
  getAgentSignedUrl
} from '../services/authService';

// Create the authentication context
const AuthContext = createContext(null);

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [backendToken, setBackendToken] = useState(null);
  const [authError, setAuthError] = useState(null);
  const [voiceStatus, setVoiceStatus] = useState(null);
  const [voiceError, setVoiceError] = useState(null);
  const [hasVoiceSet, setHasVoiceSet] = useState(false);
  const [signedUrl, setSignedUrl] = useState(null);

  // Check for existing user session on component mount
  useEffect(() => {
    const checkExistingSession = async () => {
      const token = localStorage.getItem('googleToken');
      const savedBackendToken = localStorage.getItem('backendToken');

      if (token) {
        try {
          const decodedToken = jwtDecode(token);
          const currentTime = Date.now() / 1000;

          if (decodedToken.exp > currentTime) {
            setUser(decodedToken);

            // If we have a backend token, use it
            if (savedBackendToken) {
              const parsedToken = JSON.parse(savedBackendToken);
              setBackendToken(parsedToken);
              setIsAuthenticated(true);

              // Always get a signed URL regardless of voice status
              try {
                const response = await getAgentSignedUrl(parsedToken);
                setSignedUrl(response.signed_url);

                // Set hasVoiceSet to true to bypass the SetVoice component
                setHasVoiceSet(true);
              } catch (error) {
                console.error('Error getting agent signed URL:', error);
              }
            } else {
              // Clear the session if we don't have a backend token
              logout();
            }
          } else {
            // Token expired
            logout();
          }
        } catch (error) {
          console.error('Error decoding token:', error);
          logout();
        }
      }
      setLoading(false);
    };

    checkExistingSession();
  }, []);

  // Check if the agent has a voice set
  const checkAgentVoiceStatus = async (token) => {
    try {
      const response = await getAgentSignedUrl(token);
      // Always set hasVoiceSet to true to bypass the SetVoice component
      setHasVoiceSet(true);
      setSignedUrl(response.signed_url);
      return response;
    } catch (error) {
      console.error('Error checking agent voice status:', error);
      return { has_voice_set: false, signed_url: null };
    }
  };

  // Handle Google registration
  const handleGoogleRegister = async (credentialResponse) => {
    try {
      const decodedToken = jwtDecode(credentialResponse.credential);
      setUser(decodedToken);
      localStorage.setItem('googleToken', credentialResponse.credential);

      try {
        // Register new user with Google
        const userData = await googleRegister(decodedToken);

        // Save backend token
        setBackendToken(userData.token || userData);
        localStorage.setItem('backendToken', JSON.stringify(userData.token || userData));
        setIsAuthenticated(true);
        setAuthError(null);

        // Always set hasVoiceSet to true to bypass the SetVoice component
        setHasVoiceSet(true);

        // Get the signed URL for the new user
        try {
          const response = await getAgentSignedUrl(userData.token || userData);
          setSignedUrl(response.signed_url);
          
          // Update token with the agent_id if it exists in the response
          if (userData.agent_id) {
            const updatedToken = { 
              ...(userData.token || userData), 
              agent_id: userData.agent_id 
            };
            setBackendToken(updatedToken);
            localStorage.setItem('backendToken', JSON.stringify(updatedToken));
            console.log('Agent ID saved from registration:', userData.agent_id);
          }
        } catch (error) {
          console.error('Error getting agent signed URL for new user:', error);
        }
      } catch (backendError) {
        console.error('Backend registration error:', backendError);
        setAuthError(backendError.message || 'Failed to register with the backend.');

        // Don't clear the session for specific errors like "already registered"
        if (backendError.message && backendError.message.includes('already registered')) {
          // Just propagate the error without logging out
          throw backendError;
        } else {
          // Clear the session for other errors
          logout();
        }

        // Propagate the error to the component
        throw backendError;
      }
    } catch (error) {
      console.error('Error during Google registration:', error);

      // Only set auth error and logout if it's not already a handled backend error
      if (!error.message || !error.message.includes('already registered')) {
        setAuthError('Failed to authenticate with Google. Please try again.');
        logout();
      }

      // Propagate the error to the component
      throw error;
    }
  };

  // Handle Google login
  const handleGoogleLogin = async (credentialResponse) => {
    try {
      const decodedToken = jwtDecode(credentialResponse.credential);
      setUser(decodedToken);
      localStorage.setItem('googleToken', credentialResponse.credential);

      try {
        // Login with Google
        const tokenData = await googleLogin(decodedToken);

        // Ensure agent_id is preserved in the stored token
        let tokenToStore = tokenData;
        if (tokenData.agent_id) {
          console.log('Agent ID received from login:', tokenData.agent_id);
        } else {
          console.warn('No agent_id received in login response');
        }

        // Save backend token
        setBackendToken(tokenToStore);
        localStorage.setItem('backendToken', JSON.stringify(tokenToStore));
        setIsAuthenticated(true);
        setAuthError(null);

        // Always set hasVoiceSet to true and get signed URL
        setHasVoiceSet(true);
        setSignedUrl(tokenData.signed_url);
      } catch (backendError) {
        console.error('Backend login error:', backendError);
        setAuthError(backendError.message || 'Failed to login with the backend.');
        // Clear the session if login fails
        logout();
      }
    } catch (error) {
      console.error('Error during Google login:', error);
      setAuthError('Failed to authenticate with Google. Please try again.');
      logout();
    }
  };

  // Handle logout
  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    setBackendToken(null);
    setAuthError(null);
    setHasVoiceSet(false);
    setSignedUrl(null);
    localStorage.removeItem('googleToken');
    localStorage.removeItem('backendToken');
  };

  // Handle setting agent voice
  const handleSetAgentVoice = async (audioBlob) => {
    setVoiceError(null);
    setVoiceStatus(null);

    try {
      const response = await setAgentVoice(backendToken, audioBlob);
      setVoiceStatus('Voice successfully set for your agent!');
      setHasVoiceSet(true);

      // Update the backend token with the new voice status
      if (backendToken) {
        const updatedToken = { ...backendToken, has_voice_set: true };
        setBackendToken(updatedToken);
        localStorage.setItem('backendToken', JSON.stringify(updatedToken));

        // Fetch the signed URL after setting the voice
        try {
          const signedUrlResponse = await getAgentSignedUrl(backendToken);
          setSignedUrl(signedUrlResponse.signed_url);

          // Update token with signed URL
          const tokenWithSignedUrl = {
            ...updatedToken,
            signed_url: signedUrlResponse.signed_url
          };
          setBackendToken(tokenWithSignedUrl);
          localStorage.setItem('backendToken', JSON.stringify(tokenWithSignedUrl));
        } catch (urlError) {
          console.error('Error fetching signed URL after setting voice:', urlError);
        }
      }

      return response;
    } catch (error) {
      setVoiceError(error.message || 'Failed to set voice for your agent');
      throw error;
    }
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    backendToken,
    authError,
    voiceStatus,
    voiceError,
    hasVoiceSet,
    signedUrl,
    handleGoogleRegister,
    handleGoogleLogin,
    handleSetAgentVoice,
    checkAgentVoiceStatus,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
