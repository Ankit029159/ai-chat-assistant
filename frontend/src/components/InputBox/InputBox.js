import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import { useChat } from '../../contexts/ChatContext';
import EmojiPicker from './EmojiPicker';
import AttachmentPreview from './AttachmentPreview';
import VoiceInputButton from '../VoiceInput/VoiceInputButton';

const Container = styled.form`
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  background: ${({ theme }) => theme.colors.inputBackground};
  border-radius: 12px;
  gap: 8px;
`;

const TextArea = styled.textarea`
  flex: 1 1 auto;
  border: none;
  background: transparent;
  color: ${({ theme }) => theme.colors.textPrimary};
  font-size: 1rem;
  padding: 8px;
  border-radius: 8px;
  min-height: 36px;
  max-height: 120px;
  resize: none;
  outline: none;

  &::placeholder {
    color: ${({ theme }) => theme.colors.textSecondary};
  }
`;

const Button = styled.button`
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  background: ${({ theme }) => theme.colors.buttonBackground};
  color: ${({ theme }) => theme.colors.buttonText};
  font-size: 18px;

  &:disabled {
    opacity: 0.5;
    cursor: default;
  }
`;

function InputBox() {
  const { sendMessage, addLocalMessage, uploadAttachments } = useChat(); 
  const [text, setText] = useState('');
  const [attachments, setAttachments] = useState([]);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  const handleChange = (e) => setText(e.target.value);

const handleSend = async (e) => {
  e.preventDefault();
  if (!text.trim() && attachments.length === 0) return;

  // Add local message immediately
  const localMessage = {
    id: generateUniqueId(),
    sender: 'user',
    text: text,
    attachments,
    reactions: {},
    timestamp: new Date().toISOString(),
  };
  addLocalMessage(localMessage);

  // Send to backend
  try {
    await sendMessage({ message: text, attachments, conversationHistory: messages });
  } catch (err) {
    addSystemNotice({ type: 'error', message: 'Failed to send message' });
  }

  setText('');
  setAttachments([]);
};

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  const toggleEmojiPicker = () => setShowEmojiPicker((prev) => !prev);

  const onEmojiSelect = (emoji) => {
    const cursorPos = textareaRef.current.selectionStart || 0;
    const newText = text.slice(0, cursorPos) + emoji + text.slice(cursorPos);
    setText(newText);
    setShowEmojiPicker(false);
    setTimeout(() => {
      textareaRef.current.focus();
      textareaRef.current.selectionStart = textareaRef.current.selectionEnd = cursorPos + emoji.length;
    }, 0);
  };

  const onAttachmentChange = async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;
    const uploaded = await uploadAttachments(files);
    setAttachments((prev) => [...prev, ...uploaded]);
    e.target.value = null;
  };

  const removeAttachment = (idx) => setAttachments((prev) => prev.filter((_, i) => i !== idx));

  return (
    <Container onSubmit={handleSend} aria-label="Chat input form">
      <Button type="button" onClick={toggleEmojiPicker} aria-label="Toggle emoji picker">
        😀
      </Button>
      {showEmojiPicker && <EmojiPicker onSelect={onEmojiSelect} />}
      <TextArea
        ref={textareaRef}
        placeholder="Type your message..."
        value={text}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        aria-multiline="true"
      />
      <Button type="button" onClick={() => fileInputRef.current?.click()} aria-label="Attach files">
        📎
      </Button>
      <input type="file" multiple ref={fileInputRef} style={{ display: 'none' }} onChange={onAttachmentChange} />
      <VoiceInputButton onTranscribe={(t) => setText((prev) => prev + t)} />
      <Button type="submit" disabled={!text.trim() && attachments.length === 0} aria-label="Send message">
        ➤
      </Button>
      <AttachmentPreview attachments={attachments} onRemove={removeAttachment} />
    </Container>
  );
}

export default InputBox;
