import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import App from '../App';
import { ThemeProvider } from '../contexts/ThemeContext';
import { ChatProvider } from '../contexts/ChatContext';

describe('App Component', () => {
  const renderApp = () =>
    render(
      <ThemeProvider>
        <ChatProvider>
          <App />
        </ChatProvider>
      </ThemeProvider>
    );

  test('renders header with title and theme toggle', () => {
    renderApp();
    expect(screen.getByText(/React Chat Application/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /switch to dark theme/i })).toBeInTheDocument();
  });

  test('toggles theme on button click', () => {
    renderApp();
    const toggle = screen.getByRole('button', { name: /switch to dark theme/i });
    fireEvent.click(toggle);
    expect(toggle).toHaveAttribute('aria-pressed', 'true');
    expect(toggle).toHaveAccessibleName('Switch to light theme');
  });

  test('renders skip to input link that focuses input', () => {
    renderApp();
    const skipLink = screen.getByText(/skip to chat input/i);
    expect(skipLink).toBeInTheDocument();
    fireEvent.click(skipLink);
    const input = screen.getByLabelText(/chat message input/i);
    expect(document.activeElement).toBe(input);
  });

  test('loads conversation history placeholder lazily', async () => {
    renderApp();
    expect(await screen.findByText(/future conversation history view/i)).toBeInTheDocument();
  });

  test('matches snapshot', () => {
    const { container } = renderApp();
    expect(container).toMatchSnapshot();
  });
});
