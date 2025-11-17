import React from 'react';
import styled from 'styled-components';

const DisclaimerBanner = styled.div`
  background: #fff3cd;
  border-left: 4px solid #ffc107;
  padding: 1rem;
  margin: 1rem 1rem 0 1rem;
  border-radius: 4px;
  font-size: 0.875rem;
  color: #856404;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;

  @media (prefers-color-scheme: dark) {
    background: #332701;
    border-left-color: #ffc107;
    color: #ffecb5;
  }
`;

const WarningIcon = styled.span`
  font-size: 1.25rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
`;

const Content = styled.div`
  flex: 1;
  line-height: 1.5;

  strong {
    display: block;
    margin-bottom: 0.5rem;
    color: #d39e00;

    @media (prefers-color-scheme: dark) {
      color: #ffc107;
    }
  }

  p {
    margin: 0.5rem 0;
    
    &:first-child {
      margin-top: 0;
    }
  }
`;

function MedicalDisclaimer() {
  return (
    <DisclaimerBanner role="alert" aria-label="Medical disclaimer">
      <WarningIcon>⚠️</WarningIcon>
      <Content>
        <strong>Medical Information Disclaimer</strong>
        <p>
          This chatbot provides general medical information only and is <strong>NOT a substitute for professional medical advice, diagnosis, or treatment</strong>.
        </p>
        <p style={{ fontSize: '0.8rem', opacity: 0.9 }}>
          • Do not use for self-diagnosis • Always consult a licensed healthcare professional • Seek emergency care for severe symptoms
        </p>
      </Content>
    </DisclaimerBanner>
  );
}

export default MedicalDisclaimer;
