// src/contexts/ChatContext.js
import React, { createContext, useContext, useState, useCallback } from 'react';
import { sendMessage, uploadAttachments } from '../utils/api';
import { generateUniqueId } from '../utils/formatters';

const ChatContext = createContext();

export function ChatProvider({ children }) {
  const [messages, setMessages] = useState([]);
  const [botTyping, setBotTyping] = useState(false);

  /**
   * Send a user message and get bot response
   */
  const sendMessageToBot = useCallback(
    async (text, attachments = []) => {
      if (!text && attachments.length === 0) return;

      const userMessage = {
        id: generateUniqueId(),
        sender: 'user',
        text,
        attachments,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setBotTyping(true);

      try {
        const payload = {
          message: text,
          attachments,
          conversationHistory: messages, // optional, if backend needs history
        };

        const botResponse = await sendMessage(payload);

        const botMessage = {
          id: generateUniqueId(),
          sender: 'bot',
          text: botResponse.reply || '', 
          attachments: botResponse.attachments || [],
          sources: botResponse.sources || [], // Add sources from medical backend
          disclaimer: botResponse.disclaimer || '',
          blocked: botResponse.blocked || false, // Flag for safety filter blocks
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, botMessage]);
      } catch (error) {
        console.error('Chat error:', error);
        const errorMessage = {
          id: generateUniqueId(),
          sender: 'bot',
          text: 'Sorry, something went wrong. Please try again.',
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setBotTyping(false);
      }
    },
    [messages]
  );

  /**
   * Upload attachments and return uploaded info
   */
  const uploadFiles = useCallback(async (files) => {
    try {
      const uploaded = await uploadAttachments(files);
      return uploaded; // array of { url, filename, type, id }
    } catch (error) {
      console.error('Upload error:', error);
      return [];
    }
  }, []);

  /**
   * Load older messages (placeholder for now)
   */
  const loadOlderMessages = useCallback(() => {
    console.log('Load older messages...');
  }, []);

  return (
    <ChatContext.Provider
      value={{
        messages,
        botTyping,
        sendMessage: sendMessageToBot,
        uploadAttachments: uploadFiles,
        loadOlderMessages,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

/**
 * Hook to access chat context
 */
export function useChat() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}
