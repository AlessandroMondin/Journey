import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { useAuth } from '../context/AuthContext';

const SetVoiceContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  margin: 2rem auto;
`;

const Title = styled.h2`
  color: white;
  margin-bottom: 1.5rem;
  text-align: center;
`;

const Description = styled.p`
  color: white;
  margin-bottom: 2rem;
  text-align: center;
  line-height: 1.6;
`;

const VoiceButton = styled.button`
  padding: 12px 24px;
  background-color: ${props => props.$isRecording ? '#ff4757' : '#7289da'};
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  margin-bottom: 1rem;
  width: 180px;

  &:hover {
    background-color: ${props => props.$isRecording ? '#ff6b81' : '#5e77d4'};
    transform: translateY(-2px);
  }

  &:disabled {
    background-color: #4a5568;
    cursor: not-allowed;
    transform: none;
  }
`;

const ButtonsContainer = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 1rem;
`;

const ControlButton = styled.button`
  padding: 12px 24px;
  background-color: ${props => props.$color || '#7289da'};
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;

  &:hover {
    opacity: 0.9;
    transform: translateY(-2px);
  }

  &:disabled {
    background-color: #4a5568;
    cursor: not-allowed;
    transform: none;
  }
`;

const StatusMessage = styled.div`
  color: ${props => props.$isError ? '#ff4757' : '#2ecc71'};
  background-color: ${props => props.$isError ? 'rgba(255, 71, 87, 0.1)' : 'rgba(46, 204, 113, 0.1)'};
  padding: 10px 15px;
  border-radius: 5px;
  margin-top: 1rem;
  text-align: center;
  width: 100%;
`;

const Timer = styled.div`
  font-size: 1.5rem;
  color: white;
  margin-bottom: 1rem;
  font-weight: bold;
`;

const LogoutButton = styled.button`
  margin-top: 1.5rem;
  padding: 10px 20px;
  background-color: #ff4757;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;

  &:hover {
    background-color: #ff6b81;
    transform: translateY(-2px);
  }
`;

const ConnectionStatus = styled.div`
  color: #2ecc71;
  font-size: 0.9rem;
  margin-top: 0.5rem;
  background-color: rgba(46, 204, 113, 0.1);
  padding: 8px 12px;
  border-radius: 4px;
  text-align: center;
`;

const SetVoice = () => {
  const { handleSetAgentVoice, voiceStatus, voiceError, logout, signedUrl, hasVoiceSet } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [localStatus, setLocalStatus] = useState(null);
  const [localError, setLocalError] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(30);
  const [audioBlob, setAudioBlob] = useState(null);
  const [hasRecording, setHasRecording] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerIntervalRef = useRef(null);
  const streamRef = useRef(null);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      stopRecordingAndCleanup();
    };
  }, []);

  const stopRecordingAndCleanup = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
  };

  const startRecording = async () => {
    try {
      // Reset state
      setIsRecording(true);
      setRecordingTime(30);
      setLocalStatus('Recording your voice...');
      setLocalError(null);
      setHasRecording(false);
      audioChunksRef.current = [];

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Create media recorder
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      // Handle data available event
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Handle recording stop
      mediaRecorderRef.current.onstop = () => {
        // Create audio blob from chunks
        if (audioChunksRef.current.length > 0) {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          setAudioBlob(audioBlob);
          setHasRecording(true);
          setLocalStatus('Recording complete! Ready to submit.');
        }

        // Stop all tracks in the stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
      };

      // Start recording
      mediaRecorderRef.current.start();

      // Set up timer to stop recording after 30 seconds
      timerIntervalRef.current = setInterval(() => {
        setRecordingTime(prevTime => {
          if (prevTime <= 1) {
            clearInterval(timerIntervalRef.current);
            if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
              mediaRecorderRef.current.stop();
            }
            setIsRecording(false);
            return 0;
          }
          return prevTime - 1;
        });
      }, 1000);

    } catch (error) {
      console.error('Error starting recording:', error);
      setLocalError('Could not access microphone. Please check your permissions.');
      setIsRecording(false);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      clearInterval(timerIntervalRef.current);
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setLocalStatus('Recording stopped. You can restart or submit your recording.');
    }
  };

  const restartRecording = () => {
    // Clean up previous recording
    stopRecordingAndCleanup();

    // Reset state
    setHasRecording(false);
    setAudioBlob(null);
    setLocalStatus(null);

    // Start a new recording
    startRecording();
  };

  const submitRecording = async () => {
    if (!audioBlob) {
      setLocalError('No recording available. Please record your voice first.');
      return;
    }

    setIsLoading(true);
    setLocalStatus('Submitting your voice recording...');

    try {
      // Call the handleSetAgentVoice function from the AuthContext
      await handleSetAgentVoice(audioBlob);
      setLocalStatus('Voice successfully set for your agent!');
    } catch (error) {
      setLocalError(error.message || 'Failed to set voice for your agent');
    } finally {
      setIsLoading(false);
    }
  };

  // Use either the context status/error or the local ones
  const displayStatus = voiceStatus || localStatus;
  const displayError = voiceError || localError;

  const handleLogout = () => {
    // Clean up recording resources before logout
    stopRecordingAndCleanup();
    logout();
  };

  return (
    <SetVoiceContainer>
      <Title>Set Your Voice</Title>
      <Description>
        Give your agent your own voice. Record a 30-second sample of your voice.
        Speak clearly and naturally for the best results.
      </Description>

      {isRecording && (
        <Timer>Recording: {recordingTime}s</Timer>
      )}

      {!isRecording && !hasRecording && (
        <VoiceButton
          onClick={startRecording}
          disabled={isLoading}
          $isRecording={false}
        >
          Start Recording
        </VoiceButton>
      )}

      {isRecording && (
        <ButtonsContainer>
          <ControlButton
            onClick={stopRecording}
            $color="#ff4757"
          >
            Stop Recording
          </ControlButton>
        </ButtonsContainer>
      )}

      {!isRecording && hasRecording && (
        <ButtonsContainer>
          <ControlButton
            onClick={restartRecording}
            $color="#f39c12"
            disabled={isLoading}
          >
            Restart Recording
          </ControlButton>
          <ControlButton
            onClick={submitRecording}
            $color="#2ecc71"
            disabled={isLoading}
          >
            {isLoading ? 'Submitting...' : 'Submit Voice'}
          </ControlButton>
        </ButtonsContainer>
      )}

      {displayStatus && <StatusMessage>{displayStatus}</StatusMessage>}
      {displayError && <StatusMessage $isError>{displayError}</StatusMessage>}

      {hasVoiceSet && signedUrl && (
        <ConnectionStatus>
          Connection with AI agent established.
          <br />
          You're ready to start talking to yourself!
        </ConnectionStatus>
      )}

      <LogoutButton onClick={handleLogout}>Logout</LogoutButton>
    </SetVoiceContainer>
  );
};

export default SetVoice;
