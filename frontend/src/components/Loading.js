import React from 'react';
import styled, { keyframes } from 'styled-components';
import theme from '../config/theme';

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: ${theme.COLORS.PRIMARY}; /* Matching the green color from the logo */
  font-family: ${theme.FONTS.PRIMARY};
`;

const Spinner = styled.div`
  width: 50px;
  height: 50px;
  border: 5px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: ${theme.COLORS.TEXT_LIGHT};
  animation: ${spin} 1s ease-in-out infinite;
  margin-bottom: 20px;
`;

const LoadingText = styled.p`
  color: ${theme.COLORS.TEXT_LIGHT};
  font-size: 1.2rem;
  font-weight: ${theme.FONT_WEIGHTS.MEDIUM};
  letter-spacing: 0.5px;
  font-family: ${theme.FONTS.PRIMARY};
`;

const Loading = () => {
  return (
    <LoadingContainer>
      <Spinner />
      <LoadingText>Loading Journey...</LoadingText>
    </LoadingContainer>
  );
};

export default Loading;
