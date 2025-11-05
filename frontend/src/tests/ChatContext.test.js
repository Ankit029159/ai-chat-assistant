import React from 'react';
import { renderHook, act } from '@testing-library/react';
import { ChatProvider, useChat } from '../contexts/ChatContext';

jest.mock('../utils/api', () => ({
  sendMessage: jest.fn(() => Promise.resolve({ reply: 'Hello from bot', attachments: [] })),
}));

describe('ChatContext', () => {
  const wrapper = ({ children }) => <ChatProvider>{children}</ChatProvider>;

  test('initial state is correct', () => {
    const { result } = renderHook(() => useChat(), { wrapper });
    expect(result.current.messages).toEqual([]);
    expect(result.current.connectionStatus).toBe('disconnected');
    expect(typeof result.current.sendMessage).toBe('function');
  });

  test('sendMessage adds user and bot messages', async () => {
    const { result, waitForNextUpdate } = renderHook(() => useChat(), { wrapper });
    // Wait for connecting -> connected transition
    await new Promise((r) => setTimeout(r, 1000));
    act(() => {
      result.current.sendMessage('Test message');
    });
    expect(result.current.messages.length).toBe(1);
    // Wait for bot response to arrive asynchronously
    await new Promise((r) => setTimeout(r, 1000));
    expect(result.current.messages.length).toBeGreaterThanOrEqual(2);
  });

  test('addReaction updates message reactions', async () => {
    const { result } = renderHook(() => useChat(), { wrapper });
    act(() => {
      result.current.sendMessage('Hello');
    });
    await new Promise((r) => setTimeout(r, 1000));
    const messageId = result.current.messages[0]?.id;
    act(() => {
      result.current.addReaction(messageId, '👍');
    });
    const reactedMessage = result.current.messages.find((m) => m.id === messageId);
    expect(reactedMessage.reactions['👍']).toBe(1);
  });

  test('clearConversation empties messages and adds notice', () => {
    const { result } = renderHook(() => useChat(), { wrapper });
    act(() => {
      result.current.clearConversation();
    });
    expect(result.current.messages.length).toBe(0);
    expect(result.current.notices.some((n) => n.message.includes('cleared'))).toBe(true);
  });

  test('exportConversation returns a URL string', () => {
    const { result } = renderHook(() => useChat(), { wrapper });
    let url;
    act(() => {
      url = result.current.exportConversation();
    });
    expect(typeof url).toBe('string');
    expect(url.startsWith('blob:')).toBe(true);
  });
});
