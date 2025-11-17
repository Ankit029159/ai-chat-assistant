import React from 'react';
import styled from 'styled-components';

const SourcesWrapper = styled.div`
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: ${({ theme }) => theme.colors.inputBg || '#f5f5f5'};
  border-radius: 8px;
  border-left: 3px solid ${({ theme }) => theme.colors.primary || '#007bff'};
`;

const SourcesLabel = styled.p`
  margin: 0 0 0.5rem 0;
  font-weight: 600;
  font-size: 0.85rem;
  color: ${({ theme }) => theme.colors.textSecondary || '#666'};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const SourcesList = styled.ul`
  list-style: none;
  margin: 0;
  padding: 0;
`;

const SourceItem = styled.li`
  margin: 0.4rem 0;
  padding: 0.4rem 0 0.4rem 1.25rem;
  position: relative;
  font-size: 0.85rem;
  color: ${({ theme }) => theme.colors.textPrimary || '#333'};
  line-height: 1.4;

  &:before {
    content: '📄';
    position: absolute;
    left: 0;
  }

  @media (prefers-color-scheme: dark) {
    color: #e0e0e0;
  }
`;

function SourcesDisplay({ sources }) {
  if (!sources || sources.length === 0) {
    return null;
  }

  // Filter out null/undefined sources
  const validSources = sources.filter((s) => s && s.trim());

  if (validSources.length === 0) {
    return null;
  }

  return (
    <SourcesWrapper>
      <SourcesLabel>📚 Sources</SourcesLabel>
      <SourcesList>
        {validSources.map((source, idx) => (
          <SourceItem key={idx}>{source}</SourceItem>
        ))}
      </SourcesList>
    </SourcesWrapper>
  );
}

export default SourcesDisplay;
