import React, { useState, useEffect, useRef } from 'react';
import styled, { keyframes, css } from 'styled-components';
import PropTypes from 'prop-types';

const MicIcon = styled.svg`
  width: 24px;
  height: 24px;
  fill: ${({ theme, active }) => (active ? theme.colors.voiceActive : theme.colors.voiceInactive)};
  cursor: pointer;
  transition: fill 0.3s ease;
`;

const pulse = keyframes`
  0% {
    transform: scale(1);
    opacity: 0.7;
  }
  50% {
    transform: scale(1.2);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 0.7;
  }
`;

const RecordingIndicator = styled.div`
  position: absolute;
  top: -6px;
  right: -6px;
  width: 12px;
  height: 12px;
  background-color: ${({ theme }) => theme.colors.voiceActive};
  border-radius: 50%;
  animation: ${pulse} 1.2s infinite ease-in-out;
`;

const Wrapper = styled.div`
  position: relative;
  display: inline-block;
`;

function VoiceInputButton({ onTranscribe }) {
  const [isRecording, setIsRecording] = useState(false);
  const recognitionRef = useRef(null);
  const isSupported = typeof window !== 'undefined' && !!(window.SpeechRecognition || window.webkitSpeechRecognition);

  useEffect(() => {
    if (!isSupported) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = false;
    recognitionRef.current.interimResults = false;
    recognitionRef.current.lang = 'en-US';

    recognitionRef.current.onresult = (event) => {
      if (event.results.length > 0) {
        const transcript = event.results[0][0].transcript.trim();
        if (typeof onTranscribe === 'function' && transcript.length > 0) {
          onTranscribe(transcript + ' ');
        }
      }
      setIsRecording(false);
    };

    recognitionRef.current.onerror = (event) => {
      // Handle errors gracefully
      setIsRecording(false);
    };

    recognitionRef.current.onend = () => {
      setIsRecording(false);
    };

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [isSupported, onTranscribe]);

  const toggleRecording = () => {
    if (!isSupported) return;
    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsRecording(true);
      } catch {
        setIsRecording(false);
      }
    }
  };

  if (!isSupported) return null;

  return (
    <Wrapper>
      <MicIcon
        role="button"
        tabIndex={0}
        onClick={toggleRecording}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggleRecording();
          }
        }}
        aria-pressed={isRecording}
        aria-label={isRecording ? 'Stop voice input' : 'Start voice input'}
        active={isRecording}
        viewBox="0 0 24 24"
      >
        <path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3z" />
        <path d="M19 10v1a7 7 0 0 1-14 0v-1" />
        <path d="M12 19v4" />
        <path d="M8 23h8" />
      </MicIcon>
      {isRecording && <RecordingIndicator aria-hidden="true" />}
    </Wrapper>
  );
}

VoiceInputButton.propTypes = {
  onTranscribe: PropTypes.func.isRequired,
};

export default VoiceInputButton;
