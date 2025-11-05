import React from 'react';
import styled, { keyframes } from 'styled-components';

const bounce = keyframes`
  0%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-8px);
  }
`;

const DotsWrapper = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  height: 24px;
`;

const Dot = styled.div`
  width: 8px;
  height: 8px;
  background-color: ${({ theme }) => theme.colors.typingIndicator};
  border-radius: 50%;
  animation: ${bounce} 1.4s infinite ease-in-out;
  animation-delay: ${({ delay }) => delay};
`;

function BotTypingIndicator() {
  return (
    <DotsWrapper aria-label="Bot is typing" role="status">
      <Dot delay="0s" />
      <Dot delay="0.2s" />
      <Dot delay="0.4s" />
    </DotsWrapper>
  );
}

export default BotTypingIndicator;
