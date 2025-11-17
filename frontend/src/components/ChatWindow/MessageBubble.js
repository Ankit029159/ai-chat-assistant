import React, { useState, useCallback } from 'react';
import styled from 'styled-components';
import PropTypes from 'prop-types';
import { formatTimestamp } from '../../utils/formatters';
import SourcesDisplay from '../SourcesDisplay/SourcesDisplay';

const Wrapper = styled.div`
  display: flex;
  flex-direction: ${({ isUser }) => (isUser ? 'row-reverse' : 'row')};
  align-items: flex-start;
  margin-bottom: 12px;
`;

const Avatar = styled.div`
  background-color: ${({ bg }) => bg};
  border-radius: 50%;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  margin: ${({ isUser }) => (isUser ? '0 0 0 12px' : '0 12px 0 0')};
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
  font-weight: 700;
`;

const Bubble = styled.div`
  max-width: 75%;
  background: ${({ bg }) => bg};
  color: ${({ color }) => color};
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 1rem;
  line-height: 1.4;
  display: flex;
  flex-direction: column;
  word-break: break-word;
`;

const Text = styled.div`
  white-space: pre-wrap;
`;

const Timestamp = styled.time`
  font-size: 0.7rem;
  color: ${({ theme }) => theme.colors.textSecondary};
  align-self: flex-end;
  margin-top: 4px;
`;

const bubbleColors = {
  user: { background: '#4a90e2', color: '#fff', avatarBg: '#357ABD' },
  bot: { background: '#f0f0f0', color: '#222', avatarBg: '#bbb' },
};

function MessageBubble({ message }) {
  const isUser = message.sender === 'user';

  return (
    <Wrapper isUser={isUser} role="article" aria-label={`${isUser ? 'User' : 'Bot'} message`} tabIndex={0}>
      <Avatar isUser={isUser} bg={isUser ? bubbleColors.user.avatarBg : bubbleColors.bot.avatarBg}>
        {!message.avatarUrl && (isUser ? 'U' : 'B')}
      </Avatar>

      <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
        <Bubble bg={isUser ? bubbleColors.user.background : bubbleColors.bot.background} color={isUser ? bubbleColors.user.color : bubbleColors.bot.color}>
          <Text>{message.text}</Text>
          {message.timestamp && <Timestamp dateTime={message.timestamp}>{formatTimestamp(message.timestamp)}</Timestamp>}
        </Bubble>
        
        {/* Display sources for bot messages */}
        {!isUser && message.sources && <SourcesDisplay sources={message.sources} />}
      </div>
    </Wrapper>
  );
}

MessageBubble.propTypes = {
  message: PropTypes.shape({
    sender: PropTypes.oneOf(['user', 'bot']).isRequired,
    text: PropTypes.string.isRequired,
    timestamp: PropTypes.string,
    avatarUrl: PropTypes.string,
    sources: PropTypes.arrayOf(PropTypes.string),
  }).isRequired,
};

export default MessageBubble;
