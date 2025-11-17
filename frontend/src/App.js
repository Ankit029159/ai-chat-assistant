import React, { useRef, useCallback, Suspense, lazy } from 'react';
import styled from 'styled-components';
import { useTheme } from './contexts/ThemeContext';
import { useChat } from './contexts/ChatContext';
import ThemeToggle from './components/ThemeToggle/ThemeToggle';
import ChatWindow from './components/ChatWindow/ChatWindow';
import SystemNotice from './components/SystemNotice/SystemNotice';
import MedicalDisclaimer from './components/MedicalDisclaimer/MedicalDisclaimer';

const LazyHistoryPlaceholder = lazy(() =>
  import('./components/ConversationHistory/HistoryPlaceholder').then((mod) => ({ default: mod.HistoryPlaceholder }))
);

const Container = styled.div`
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: ${({ theme }) => theme.colors.background};
  color: ${({ theme }) => theme.colors.textPrimary};
  font-family: ${({ theme }) => theme.fonts.primary};
  transition: background-color 0.3s ease, color 0.3s ease;
`;

const Header = styled.header`
  padding: 1rem 1.5rem;
  background: ${({ theme }) => theme.colors.headerBackground};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h1`
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
`;

const Main = styled.main`
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const Footer = styled.footer`
  padding: 0.5rem 1rem;
  background: ${({ theme }) => theme.colors.footerBackground};
`;

const SkipToInputLink = styled.a`
  position: absolute;
  left: -9999px;
  top: auto;
  width: 1px;
  height: 1px;
  overflow: hidden;

  &:focus {
    position: static;
    width: auto;
    height: auto;
    margin: 8px;
    padding: 8px;
    background-color: ${({ theme }) => theme.colors.focusBackground};
    color: ${({ theme }) => theme.colors.focusText};
    border-radius: 4px;
    text-decoration: none;
    outline: 2px solid ${({ theme }) => theme.colors.focusOutline};
    outline-offset: 2px;
    z-index: 1000;
  }
`;

function App() {
  const { currentTheme, toggleTheme } = useTheme();
  const { notices = [], clearNotices } = useChat();
  const mainRef = useRef(null);

  const handleSkipToInput = useCallback((e) => {
    e.preventDefault();
    const input = document.getElementById('chat-input-field');
    if (input) input.focus();
  }, []);

  return (
    <Container role="application" aria-live="polite" aria-relevant="additions removals">
      <SkipToInputLink href="#chat-input-field" onClick={handleSkipToInput}>
        Skip to chat input
      </SkipToInputLink>

      {/* Medical Disclaimer Banner */}
      <MedicalDisclaimer />

      <Header>
        <Title>Medical Chat Assistant</Title>
        <ThemeToggle currentTheme={currentTheme} toggleTheme={toggleTheme} />
      </Header>

      <Main ref={mainRef}>
        <ChatWindow />
        <Suspense fallback={<div aria-live="polite">Loading conversation history...</div>}>
          <LazyHistoryPlaceholder messages={[]} /> {/* safe empty array */}
        </Suspense>
      </Main>

      <Footer>{/* InputBox if needed */}</Footer>

      {(notices || []).length > 0 &&
        (notices || []).map((notice) => (
          <SystemNotice key={notice.id} notice={notice} onDismiss={() => clearNotices(notice.id)} />
        ))}
    </Container>
  );
}

export default App;
