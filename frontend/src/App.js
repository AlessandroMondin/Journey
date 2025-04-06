import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { GoogleOAuthProvider } from '@react-oauth/google';
import TalkButton from './components/TalkButton';
import Login from './components/Login';
import Loading from './components/Loading';
import SetVoice from './components/SetVoice';
import Calendar from './components/Calendar';
import { AuthProvider, useAuth } from './context/AuthContext';
import theme from './config/theme';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
  background: ${theme.COLORS.PRIMARY}; /* Solid green background matching the logo */
  font-family: ${theme.FONTS.PRIMARY};
`;

const TitleContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  color: ${theme.COLORS.TEXT_LIGHT};
  margin-bottom: 0;
  text-align: center;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  font-weight: ${theme.FONT_WEIGHTS.MEDIUM};
  letter-spacing: 0.5px;
  line-height: 1.2;
`;

const Subtitle = styled.h2`
  font-size: 1.8rem;
  color: ${theme.COLORS.TEXT_LIGHT};
  text-align: center;
  font-weight: ${theme.FONT_WEIGHTS.LIGHT};
  letter-spacing: 0.5px;
  margin-top: 0.2rem;
  opacity: 0.85;
`;

// Replace with your Google Client ID
const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || "YOUR_GOOGLE_CLIENT_ID";

const AppContent = () => {
  const { isAuthenticated, loading } = useAuth();
  const [forceUpdate, setForceUpdate] = useState(0);

  // When authentication state changes, force a re-render
  useEffect(() => {
    // Listen for authentication status changes
    const handleAuthStatusChange = () => {
      console.log('Auth status change detected in AppContent');
      setForceUpdate(prev => prev + 1); // Force re-render
    };

    window.addEventListener('auth_status_changed', handleAuthStatusChange);

    return () => {
      window.removeEventListener('auth_status_changed', handleAuthStatusChange);
    };
  }, []);

  if (loading) {
    return (
      <AppContainer>
        <Calendar />
        <Loading />
      </AppContainer>
    );
  }

  // Determine which component to render
  const renderContent = () => {
    if (!isAuthenticated) {
      return <Login />;
    }

    return <TalkButton />;
  };

  // The key prop on Calendar forces it to re-mount when forceUpdate changes
  return (
    <AppContainer>
      <Calendar key={`calendar-${isAuthenticated}-${forceUpdate}`} />
      <TitleContainer>
        <Title>Journey</Title>
        <Subtitle>Your AI Diary</Subtitle>
      </TitleContainer>
      {renderContent()}
    </AppContainer>
  );
};

function App() {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}

export default App;
