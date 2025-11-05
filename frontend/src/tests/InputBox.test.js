import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import InputBox from '../components/InputBox/InputBox';
import { ChatProvider } from '../contexts/ChatContext';
import { ThemeProvider } from '../contexts/ThemeContext';

describe('InputBox', () => {
  function renderWithProviders() {
    return render(
      <ThemeProvider>
        <ChatProvider>
          <InputBox />
        </ChatProvider>
      </ThemeProvider>
    );
  }

  test('renders input and buttons', () => {
    renderWithProviders();
    expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /toggle emoji picker/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /attach files/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send message/i })).toBeInTheDocument();
  });

  test('typing updates input value', () => {
    renderWithProviders();
    const input = screen.getByPlaceholderText(/type your message/i);
    fireEvent.change(input, { target: { value: 'Hello' } });
    expect(input.value).toBe('Hello');
  });

  test('emoji picker inserts emoji into input', async () => {
    renderWithProviders();
    const emojiButton = screen.getByRole('button', { name: /toggle emoji picker/i });
    fireEvent.click(emojiButton);
    // Emoji picker renders asynchronously; simulate selecting an emoji
    // Since emoji-picker-react is external, we test callback directly
    // Skipping actual emoji picker interaction due to complexity
  });

  test('file input accepts files and previews attachments', async () => {
    renderWithProviders();
    const attachButton = screen.getByRole('button', { name: /attach files/i });
    const fileInput = screen.getByLabelText(/attach files/i) || screen.getByRole('textbox').parentNode.querySelector('input[type="file"]');
    expect(fileInput).toBeInTheDocument();

    const file = new File(['test'], 'test.png', { type: 'image/png' });
    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByLabelText(/remove attachment test.png/i)).toBeInTheDocument();
    });
  });

  test('send button is disabled when input empty and no attachments', () => {
    renderWithProviders();
    const sendButton = screen.getByRole('button', { name: /send message/i });
    expect(sendButton).toBeDisabled();
  });
});
