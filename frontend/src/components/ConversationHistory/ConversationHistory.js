// src/components/ConversationHistory/ConversationHistory.js
import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import MessageBubble from '../ChatWindow/MessageBubble';

const List = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

function ConversationHistory({ messages }) {
  if (!messages || messages.length === 0) {
    return <div style={{ color: '#888', fontStyle: 'italic' }}>No messages yet.</div>;
  }

  return (
    <List role="list" aria-label="Chat messages">
      {messages.map((msg, idx) => (
        <MessageBubble key={idx} message={msg} />
      ))}
    </List>
  );
}

ConversationHistory.propTypes = {
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      sender: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired,
      attachments: PropTypes.array,
      timestamp: PropTypes.string,
    })
  ),
};

export default ConversationHistory;
