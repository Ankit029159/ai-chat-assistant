import React, { useEffect } from 'react';
import styled, { keyframes } from 'styled-components';
import PropTypes from 'prop-types';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(-12px); }
  to { opacity: 1; transform: translateY(0); }
`;

const NoticeWrapper = styled.div`
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  min-width: 280px;
  background-color: ${({ type, theme }) => {
    switch (type) {
      case 'error':
        return theme.colors.noticeErrorBackground;
      case 'warning':
        return theme.colors.noticeWarningBackground;
      case 'info':
      default:
        return theme.colors.noticeInfoBackground;
    }
  }};
  color: ${({ theme }) => theme.colors.textPrimary};
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  animation: ${fadeIn} 0.3s ease forwards;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.9rem;
  z-index: 1500;
`;

const Message = styled.div`
  flex: 1 1 auto;
  margin-right: 8px;
`;

const DismissButton = styled.button`
  background: transparent;
  border: none;
  color: ${({ theme }) => theme.colors.textPrimary};
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  user-select: none;

  &:hover,
  &:focus {
    color: ${({ theme }) => theme.colors.noticeDismissHover};
    outline: none;
  }
`;

function SystemNotice({ notice, onDismiss }) {
  const { id, type, message } = notice;

  useEffect(() => {
    const timer = setTimeout(() => {
      onDismiss(id);
    }, 8000);

    return () => clearTimeout(timer);
  }, [id, onDismiss]);

  return (
    <NoticeWrapper role="alert" aria-live="assertive" type={type}>
      <Message>{message}</Message>
      <DismissButton aria-label="Dismiss notice" onClick={() => onDismiss(id)}>
        ×
      </DismissButton>
    </NoticeWrapper>
  );
}

SystemNotice.propTypes = {
  notice: PropTypes.shape({
    id: PropTypes.string.isRequired,
    type: PropTypes.oneOf(['info', 'warning', 'error']),
    message: PropTypes.string.isRequired,
  }).isRequired,
  onDismiss: PropTypes.func.isRequired,
};

export default SystemNotice;
