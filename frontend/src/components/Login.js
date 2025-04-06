import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../context/AuthContext';
import SetVoice from './SetVoice';
import Modal from './Modal';
import theme from '../config/theme';

const LoginContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  box-shadow: ${theme.SHADOWS.LARGE};
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  font-family: ${theme.FONTS.PRIMARY};
`;

const Title = styled.h2`
  color: ${theme.COLORS.TEXT_LIGHT};
  margin-bottom: 2rem;
  text-align: center;
  font-weight: ${theme.FONT_WEIGHTS.MEDIUM};
  letter-spacing: 0.5px;
  font-family: ${theme.FONTS.PRIMARY};
`;

const Description = styled.p`
  color: ${theme.COLORS.TEXT_LIGHT};
  margin-bottom: 2rem;
  text-align: center;
  line-height: 1.6;
  font-family: ${theme.FONTS.PRIMARY};
`;

const ButtonsWrapper = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 300px;
  font-family: ${theme.FONTS.PRIMARY};
`;

const ButtonLabel = styled.p`
  color: ${theme.COLORS.TEXT_LIGHT};
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  text-align: center;
  font-family: ${theme.FONTS.PRIMARY};
`;

const Divider = styled.div`
  width: 100%;
  height: 1px;
  background-color: rgba(255, 255, 255, 0.2);
  margin: 1.5rem 0;
  position: relative;
`;

const DividerText = styled.span`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: ${theme.COLORS.PRIMARY}; /* Updated to match the green theme */
  padding: 0 1rem;
  color: ${theme.COLORS.TEXT_LIGHT};
  font-size: 0.9rem;
  font-family: ${theme.FONTS.PRIMARY};
`;

const UserInfo = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 2rem;
  width: 100%;
  font-family: ${theme.FONTS.PRIMARY};
`;

const UserImage = styled.img`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin-bottom: 1rem;
  border: 3px solid ${theme.COLORS.TEXT_LIGHT};
`;

const UserName = styled.h3`
  color: ${theme.COLORS.TEXT_LIGHT};
  margin-bottom: 0.5rem;
  font-weight: ${theme.FONT_WEIGHTS.MEDIUM};
  font-family: ${theme.FONTS.PRIMARY};
`;

const UserEmail = styled.p`
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 1.5rem;
  font-family: ${theme.FONTS.PRIMARY};
`;

const LogoutButton = styled.button`
  padding: 10px 20px;
  background-color: rgba(255, 255, 255, 0.2);
  color: ${theme.COLORS.TEXT_LIGHT};
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: ${theme.FONT_WEIGHTS.SEMI_BOLD};
  transition: all 0.3s ease;
  font-family: ${theme.FONTS.PRIMARY};

  &:hover {
    background-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
  }
`;

const ErrorMessage = styled.div`
  color: ${theme.COLORS.ACCENT};
  background-color: rgba(255, 255, 255, 0.15);
  padding: 10px 15px;
  border-radius: 5px;
  margin-bottom: 1rem;
  text-align: center;
  width: 100%;
  font-family: ${theme.FONTS.PRIMARY};
`;

const SuccessMessage = styled.div`
  color: ${theme.COLORS.TEXT_LIGHT};
  background-color: rgba(255, 255, 255, 0.15);
  padding: 10px 15px;
  border-radius: 5px;
  margin-top: 1rem;
  text-align: center;
  width: 100%;
  font-family: ${theme.FONTS.PRIMARY};
`;

const NextStepButton = styled.button`
  padding: 10px 20px;
  background-color: rgba(255, 255, 255, 0.2);
  color: ${theme.COLORS.TEXT_LIGHT};
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: ${theme.FONT_WEIGHTS.SEMI_BOLD};
  transition: all 0.3s ease;
  margin-top: 1rem;
  font-family: ${theme.FONTS.PRIMARY};

  &:hover {
    background-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
  }
`;

const Login = () => {
  const { isAuthenticated, user, handleGoogleRegister, handleGoogleLogin, logout, authError, signedUrl } = useAuth();
  const [loginError, setLoginError] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMessage, setModalMessage] = useState('');
  const [modalTitle, setModalTitle] = useState('');
  const [authInProgress, setAuthInProgress] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      localStorage.setItem('auth_timestamp', Date.now().toString());

      const event = new CustomEvent('auth_status_changed', { detail: { isAuthenticated } });
      window.dispatchEvent(event);
    }
  }, [isAuthenticated]);

  const handleGoogleError = (error) => {
    console.log('Google Login Failed:', error);
    setLoginError('Failed to authenticate with Google. Please check your browser settings and try again.');
    setAuthInProgress(false);
  };

  const showModal = (title, message) => {
    setModalTitle(title);
    setModalMessage(message);
    setModalOpen(true);
  };

  const handleRegistration = async (credentialResponse) => {
    try {
      setAuthInProgress(true);
      await handleGoogleRegister(credentialResponse);
    } catch (error) {
      console.error('Registration error:', error);
      setAuthInProgress(false);

      if (error.message && error.message.includes('already registered')) {
        showModal('Already Registered', 'You are already registered, you need to just login.');
      }
    }
  };

  const handleLogin = async (credentialResponse) => {
    try {
      setAuthInProgress(true);
      console.log('Starting Google login process...');

      // Add a try/catch block specifically for the handleGoogleLogin call
      try {
        await handleGoogleLogin(credentialResponse);
        console.log('Login successful, authentication complete');
      } catch (authError) {
        console.error('Authentication error in login handler:', authError);
        setLoginError(`Authentication error: ${authError.message}`);
        setAuthInProgress(false);
        return;
      }

      // Check if we're authenticated after the login attempt
      console.log('Authentication status after login:', isAuthenticated);

      if (window.forceRefreshCalendar) {
        window.forceRefreshCalendar();
      }

      // If we got here but aren't authenticated, show a warning
      if (!isAuthenticated) {
        console.warn('Login completed but isAuthenticated is still false');
        setLoginError('Login completed but session was not established. Please try again.');
      } else {
        console.log('Authentication successful, user is now logged in');
      }

      setAuthInProgress(false);
    } catch (error) {
      console.error('Login error:', error);
      setLoginError(`Login failed: ${error.message}`);
      setAuthInProgress(false);
    }
  };

  return (
    <>
      <LoginContainer>
        {isAuthenticated || authInProgress ? (
          <>
            {isAuthenticated && (
              <UserInfo>
                <UserImage src={user.picture} alt={user.name} />
                <UserName>{user.name}</UserName>
                <UserEmail>{user.email}</UserEmail>
                {authError && <ErrorMessage>{authError}</ErrorMessage>}

                <SuccessMessage>
                  You're ready to talk to your AI diary!
                  {signedUrl && <p>Connection with AI diary is established.</p>}
                </SuccessMessage>

                <LogoutButton onClick={logout}>Logout</LogoutButton>
              </UserInfo>
            )}

            {authInProgress && !isAuthenticated && (
              <SuccessMessage>Authenticating... Please wait.</SuccessMessage>
            )}
          </>
        ) : (
          <>
            <Description>
              Talk to your diary. Reflect on your day, process your thoughts, or simply document your life's journey.
            </Description>
            {authError && <ErrorMessage>{authError}</ErrorMessage>}
            {loginError && <ErrorMessage>{loginError}</ErrorMessage>}

            <ButtonsWrapper>
              <ButtonLabel>New user? Register:</ButtonLabel>
              <GoogleLogin
                onSuccess={handleRegistration}
                onError={handleGoogleError}
                text="register_with"
                shape="pill"
              />

              <Divider>
                <DividerText>OR</DividerText>
              </Divider>

              <ButtonLabel>Login:</ButtonLabel>
              <GoogleLogin
                onSuccess={handleLogin}
                onError={handleGoogleError}
                text="signin_with"
                shape="pill"
              />
            </ButtonsWrapper>
          </>
        )}
      </LoginContainer>

      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={modalTitle}
      >
        {modalMessage}
      </Modal>
    </>
  );
};

export default Login;
