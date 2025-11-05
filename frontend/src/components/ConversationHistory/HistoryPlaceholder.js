// src/components/ConversationHistory/HistoryPlaceholder.js
import React from 'react';
import styled from 'styled-components';

const PlaceholderWrapper = styled.div`
  margin: 1rem auto;
  padding: 2rem;
  max-width: 600px;
  border: 2px dashed ${({ theme }) => theme.colors.placeholderBorder};
  border-radius: 16px;
  text-align: center;
  color: ${({ theme }) => theme.colors.placeholderText};
  font-family: ${({ theme }) => theme.fonts.primary};
  font-size: 1.25rem;
  user-select: none;
`;

export function HistoryPlaceholder() {
  return (
    <PlaceholderWrapper role="region" aria-live="polite" aria-label="Conversation history placeholder">
      Future Conversation History View (Coming Soon)
    </PlaceholderWrapper>
  );
}
