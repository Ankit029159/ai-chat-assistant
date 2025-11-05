import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import MessageBubble from '../components/ChatWindow/MessageBubble';

const baseMessage = {
  id: 'msg1',
  sender: 'user',
  text: 'This is a test message',
  attachments: [],
  reactions: {},
  timestamp: new Date().toISOString(),
  avatarUrl: null,
};

describe('MessageBubble', () => {
  test('renders user message correctly', () => {
    render(<MessageBubble message={baseMessage} />);
    expect(screen.getByRole('article')).toHaveAttribute('aria-label', 'User message');
    expect(screen.getByText(baseMessage.text)).toBeInTheDocument();
  });

  test('renders bot message correctly', () => {
    const msg = { ...baseMessage, sender: 'bot', text: 'Bot reply' };
    render(<MessageBubble message={msg} />);
    expect(screen.getByRole('article')).toHaveAttribute('aria-label', 'Bot message');
    expect(screen.getByText(msg.text)).toBeInTheDocument();
  });

  test('displays timestamp correctly', () => {
    render(<MessageBubble message={baseMessage} />);
    const time = screen.getByText(/\d{1,2}:\d{2}/);
    expect(time).toBeInTheDocument();
  });

  test('shows reactions and toggles on click', () => {
    const msg = {
      ...baseMessage,
      reactions: { '👍': 2 },
    };
    render(<MessageBubble message={msg} />);
    const reactionBtn = screen.getByRole('button', { name: /2 👍 reactions/i });
    expect(reactionBtn).toBeInTheDocument();

    fireEvent.click(reactionBtn);
    expect(reactionBtn).toHaveAttribute('aria-pressed', 'true');

    fireEvent.click(reactionBtn);
    expect(reactionBtn).toHaveAttribute('aria-pressed', 'false');
  });

  test('renders attachments correctly', () => {
    const msg = {
      ...baseMessage,
      attachments: [
        { id: 'a1', url: 'https://picsum.photos/200/100', filename: 'image.jpg', type: 'image/jpeg' },
        { id: 'a2', url: 'https://example.com/file.pdf', filename: 'file.pdf', type: 'application/pdf' },
      ],
    };
    render(<MessageBubble message={msg} />);
    expect(screen.getByAltText('image.jpg')).toBeInTheDocument();
    expect(screen.getByLabelText('Download attachment file.pdf')).toBeInTheDocument();
  });

  test('is keyboard focusable', () => {
    render(<MessageBubble message={baseMessage} />);
    const bubble = screen.getByRole('article');
    bubble.focus();
    expect(bubble).toHaveFocus();
  });
});
