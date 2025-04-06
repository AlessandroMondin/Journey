import React from 'react';
import styled from 'styled-components';
import theme from '../config/theme';

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: ${theme.COLORS.BACKGROUND_LIGHT};
  padding: 2rem;
  border-radius: 10px;
  box-shadow: ${theme.SHADOWS.LARGE};
  max-width: 500px;
  width: 90%;
  text-align: center;
  font-family: ${theme.FONTS.PRIMARY};
  border-left: 4px solid ${theme.COLORS.PRIMARY};
`;

const Title = styled.h3`
  margin-top: 0;
  color: ${theme.COLORS.PRIMARY};
  font-size: 1.5rem;
  font-weight: ${theme.FONT_WEIGHTS.MEDIUM};
  font-family: ${theme.FONTS.PRIMARY};
`;

const Message = styled.div`
  color: ${theme.COLORS.TEXT_DARK};
  margin: 1rem 0;
  line-height: 1.5;
  font-family: ${theme.FONTS.PRIMARY};
`;

const Button = styled.button`
  padding: 10px 20px;
  background-color: ${theme.COLORS.PRIMARY};
  color: ${theme.COLORS.TEXT_LIGHT};
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: ${theme.FONT_WEIGHTS.MEDIUM};
  transition: all 0.3s ease;
  margin-top: 1rem;
  font-family: ${theme.FONTS.PRIMARY};

  &:hover {
    background-color: ${theme.COLORS.PRIMARY_DARK};
    transform: translateY(-2px);
  }
`;

const Modal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={(e) => e.stopPropagation()}>
        <Title>{title}</Title>
        <Message>{children}</Message>
        <Button onClick={onClose}>OK</Button>
      </ModalContent>
    </ModalOverlay>
  );
};

export default Modal;
