// src/components/ChatWindow/ChatWindow.js
import React, { useRef, useCallback } from 'react';
import styled from 'styled-components';
import { useChat } from '../../contexts/ChatContext';
import MessageBubble from './MessageBubble';
import BotTypingIndicator from './BotTypingIndicator';
import useAutoscroll from '../../hooks/useAutoscroll';

const Container = styled.div`
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
`;

const MessageListWrapper = styled.div`
  flex: 1 1 auto;
  overflow-y: auto;
  background: ${({ theme }) => theme.colors.chatBackground};
  padding: 1rem;
  scrollbar-width: thin;
  scrollbar-color: ${({ theme }) => theme.colors.scrollbarThumb} ${({ theme }) => theme.colors.scrollbarTrack};

  &::-webkit-scrollbar {
    width: 8px;
  }
  &::-webkit-scrollbar-track {
    background: ${({ theme }) => theme.colors.scrollbarTrack};
  }
  &::-webkit-scrollbar-thumb {
    background-color: ${({ theme }) => theme.colors.scrollbarThumb};
    border-radius: 10px;
    border: 2px solid ${({ theme }) => theme.colors.scrollbarTrack};
  }
`;

const BotTypingWrapper = styled.div`
  padding: 0 1rem 1rem 1rem;
  background: ${({ theme }) => theme.colors.chatBackground};
`;

const InputWrapper = styled.div`
  padding: 0.5rem 1rem;
  background: ${({ theme }) => theme.colors.footerBackground};
  display: flex;
  gap: 0.5rem;
  border-top: 1px solid ${({ theme }) => theme.colors.footerShadow};
`;

const Input = styled.input`
  flex: 1;
  border-radius: 12px;
  border: 1px solid ${({ theme }) => theme.colors.inputBorder};
  padding: 8px 12px;
  font-size: 1rem;
  background: ${({ theme }) => theme.colors.inputBg};
  color: ${({ theme }) => theme.colors.textPrimary};

  &:focus {
    outline: 2px solid ${({ theme }) => theme.colors.focusOutline};
  }
`;

const SendButton = styled.button`
  padding: 8px 16px;
  background: ${({ theme }) => theme.colors.primary};
  color: #fff;
  font-weight: 600;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: ${({ theme }) => theme.colors.primaryHover};
  }
`;

function ChatWindow() {
  const { messages, botTyping, sendMessage } = useChat();
  const containerRef = useRef(null);
  const inputRef = useRef(null);

  useAutoscroll(containerRef, messages);

  const handleSend = useCallback(() => {
    const text = inputRef.current.value.trim();
    if (!text) return;
    sendMessage(text);
    inputRef.current.value = '';
  }, [sendMessage]);

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  return (
    <Container>
      <MessageListWrapper ref={containerRef} role="log" aria-live="polite" aria-relevant="additions">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {botTyping && (
          <BotTypingWrapper aria-live="assertive" aria-atomic="true" aria-label="Bot is typing">
            <BotTypingIndicator />
          </BotTypingWrapper>
        )}
      </MessageListWrapper>

      <InputWrapper>
        <Input
          ref={inputRef}
          id="chat-input-field"
          placeholder="Type a message..."
          onKeyDown={handleKeyDown}
          aria-label="Type your message"
        />
        <SendButton onClick={handleSend}>Send</SendButton>
      </InputWrapper>
    </Container>
  );
}

export default ChatWindow;
