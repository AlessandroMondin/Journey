import React, { useState, useRef } from 'react';
import styled, { keyframes } from 'styled-components';
import { useAuth } from '../context/AuthContext';
import { useConversation } from '@11labs/react';
import config from '../config/config';

const pulse = keyframes`
  0% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.7);
  }
  70% {
    box-shadow: 0 0 0 15px rgba(255, 255, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0);
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
`;

const WhiteBall = styled.div`
  background-color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
  width: ${props => props.$isActive ? '200px' : '150px'};
  height: ${props => props.$isActive ? '200px' : '150px'};
  animation: ${props => props.$isActive ? 'pulse 1.5s infinite alternate' : 'none'};
  position: relative;
  color: rgba(0, 0, 0, 0.6);
  font-weight: 500;
  font-size: 16px;

  @keyframes pulse {
    0% {
      transform: scale(1);
    }
    100% {
      transform: scale(1.15);
    }
  }

  &:hover {
    transform: ${props => props.$isActive ? 'none' : 'scale(1.05)'};
  }
`;

const StatusText = styled.div`
  font-size: 1.2rem;
  color: white;
  text-align: center;
  margin-top: 10px;
  font-weight: 500;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  font-family: 'Aksara Lafontype', sans-serif;
`;

const InputContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 400px;
  margin-bottom: 20px;
  font-family: 'Aksara Lafontype', sans-serif;
`;

const Label = styled.label`
  font-size: 1rem;
  color: white;
  margin-bottom: 8px;
  font-weight: 500;
  font-family: 'Aksara Lafontype', sans-serif;
`;

const Input = styled.input`
  padding: 12px 16px;
  font-size: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  transition: all 0.3s ease;
  font-family: 'Aksara Lafontype', sans-serif;

  &:focus {
    outline: none;
    border-color: rgba(255, 255, 255, 0.5);
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
`;

const UserGreeting = styled.p`
  font-size: 1.5rem;
  color: white;
  text-align: center;
  margin-bottom: 20px;
  font-weight: 500;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  font-family: 'Aksara Lafontype', sans-serif;
`;

const LogoutButton = styled.button`
  padding: 10px 20px;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  margin-top: 20px;
  transition: all 0.3s ease;
  font-family: 'Aksara Lafontype', sans-serif;

  &:hover {
    background-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
  }
`;

const ErrorMessage = styled.div`
  color: #ff4757;
  background-color: rgba(255, 255, 255, 0.15);
  padding: 10px 15px;
  border-radius: 5px;
  margin-top: 1rem;
  text-align: center;
  width: 100%;
  max-width: 400px;
  font-weight: 500;
  font-family: 'Aksara Lafontype', sans-serif;
`;

const TalkButton = () => {
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState(null);

  // Get user data and token from auth context
  const { user, backendToken, signedUrl, logout } = useAuth();

  // Use the ElevenLabs React SDK hook with improved error handling
  const conversation = useConversation({
    onConnect: () => {
      console.log('Conversation connected successfully');
    },
    onDisconnect: () => {
      console.log('Conversation disconnected');
      setIsActive(false);
    },
    onMessage: (message) => {
      console.log('Received message:', message);
    },
    onError: (error) => {
      console.error('Conversation error:', error);
      setIsActive(false);
    }
  });

  // Extract status information from the hook
  const { status, isSpeaking } = conversation;

  // Helper function to extract agent ID from signed URL
  const extractAgentIdFromUrl = (url) => {
    if (!url) return null;
    try {
      // Extract agent_id from URL query parameters
      const urlObj = new URL(url);

      // Check if it's in the query parameters
      const queryAgentId = urlObj.searchParams.get('agent_id');
      if (queryAgentId) {
        return queryAgentId;
      }

      // Check if it's in the URL path
      // Example: "wss://api.elevenlabs.io/v1/convai/conversation/agent_123abc"
      const pathParts = urlObj.pathname.split('/');
      const lastPathPart = pathParts[pathParts.length - 1];

      // If the last part looks like an agent ID (not a generic endpoint)
      if (lastPathPart && !lastPathPart.includes('.') && !['conversation', 'convai', 'v1'].includes(lastPathPart)) {
        return lastPathPart;
      }

      console.warn('Could not find agent ID in URL:', url);
      return null;
    } catch (error) {
      console.error('Error extracting agent ID from URL:', error);
      return null;
    }
  };

  // Handle start/stop of the conversation with better error handling
  const handleClick = async () => {
    // Clear any previous errors
    setError(null);

    if (!isActive) {
      try {
        console.log('Auth context data:', {
          hasUser: !!user,
          hasBackendToken: !!backendToken,
          hasSignedUrl: !!signedUrl,
          backendTokenFields: backendToken ? Object.keys(backendToken) : []
        });

        // Request microphone permission if not already granted
        await navigator.mediaDevices.getUserMedia({ audio: true });

        // Get the agent ID from backendToken or signedUrl
        let agentId = null;

        // First try to get it from backendToken
        if (backendToken && backendToken.elevenlabs_agent_id) {
          agentId = backendToken.elevenlabs_agent_id;
          console.log('Using agent ID from backendToken:', agentId);
        }
        // Then try to extract it from signedUrl
        else if (signedUrl) {
          agentId = extractAgentIdFromUrl(signedUrl);
          console.log('Extracted agent ID from signedUrl:', agentId);
        }

        // Check if agent ID is available - throw error if not
        if (!agentId) {
          console.error('Agent ID not available');
          console.log('backendToken:', backendToken);
          console.log('signedUrl:', signedUrl);

          // Provide a clear error message about the missing voice setup
          const errorMessage = 'No agent ID found. This is likely because the voice setup step was skipped. Please set up your voice profile or contact support.';
          setError(errorMessage);
          throw new Error(errorMessage);
        }

        console.log('Starting conversation with agent ID:', agentId);

        // Start the conversation session with the extracted agent ID
        const conversationId = await conversation.startSession({
          agentId: agentId,
        });

        console.log('Conversation started with ID:', conversationId);
        setIsActive(true);
      } catch (error) {
        console.error('Error starting conversation:', error);

        // More detailed error logging
        if (error instanceof CloseEvent) {
          console.log('WebSocket close event details:', {
            code: error.code,
            reason: error.reason,
            wasClean: error.wasClean
          });
        }

        // Show more specific error message to the user
        let errorMessage = 'Failed to start conversation.';

        if (error instanceof DOMException && error.name === 'NotAllowedError') {
          errorMessage = 'Microphone access was denied. Please allow microphone access to use this feature.';
        } else if (error instanceof CloseEvent) {
          errorMessage = `Connection closed unexpectedly (code: ${error.code}). Please check your agent ID and try again.`;
        } else if (error.message && error.message.includes('agent ID')) {
          // Use the error message we created above
          errorMessage = error.message;
        }

        // Set the error state to display to the user
        if (!error.message || !error.message.includes('agent ID')) {
          setError(errorMessage);
        }

        setIsActive(false);
      }
    } else {
      // End the conversation session
      try {
        await conversation.endSession();
      } catch (error) {
        console.error('Error ending conversation:', error);
      }
      setIsActive(false);
    }
  };

  return (
    <ButtonContainer>
      {/* {user && (
        <UserGreeting>Hello, {user.name}!</UserGreeting>
      )} */}
      <WhiteBall
        onClick={handleClick}
        $isActive={isActive}
      >
        {isActive ? 'stop' : 'tap to talk'}
      </WhiteBall>
      <StatusText>
        {isActive
          ? isSpeaking
            ? ''
            : status === 'connected'
              ? ''
              : 'Connecting...'
          : ''}
      </StatusText>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      <LogoutButton onClick={logout}>
        Sign Out
      </LogoutButton>
    </ButtonContainer>
  );
};

export default TalkButton;
