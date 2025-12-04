import React, { useEffect } from 'react';
import styled, { keyframes } from 'styled-components';

const slideIn = keyframes`
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
`;

const slideOut = keyframes`
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
`;

const ToastContainer = styled.div<{ $show: boolean; $type: 'success' | 'error' | 'info' }>`
  position: fixed;
  top: 20px;
  right: 20px;
  background-color: ${props => {
    switch (props.$type) {
      case 'success':
        return '#4caf50';
      case 'error':
        return '#f44336';
      default:
        return '#2196f3';
    }
  }};
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 10000;
  min-width: 300px;
  max-width: 400px;
  animation: ${props => (props.$show ? slideIn : slideOut)} 0.3s ease-out;
  display: ${props => (props.$show ? 'block' : 'none')};
`;

const ToastContent = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
`;

const ToastIcon = styled.span`
  font-size: 1.5rem;
`;

const ToastMessage = styled.div`
  flex: 1;
  font-size: 1rem;
  font-weight: 500;
`;

interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info';
  show: boolean;
  onClose: () => void;
  duration?: number;
}

const Toast: React.FC<ToastProps> = ({ 
  message, 
  type = 'success', 
  show, 
  onClose,
  duration = 3000 
}) => {
  useEffect(() => {
    if (show) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [show, duration, onClose]);

  const icons = {
    success: '✅',
    error: '❌',
    info: 'ℹ️',
  };

  if (!show) return null;

  return (
    <ToastContainer $show={show} $type={type}>
      <ToastContent>
        <ToastIcon>{icons[type]}</ToastIcon>
        <ToastMessage>{message}</ToastMessage>
      </ToastContent>
    </ToastContainer>
  );
};

export default Toast;


