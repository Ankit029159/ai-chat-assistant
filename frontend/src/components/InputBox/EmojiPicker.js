import React, { useEffect, useRef } from 'react';
import styled from 'styled-components';
import Picker from 'emoji-picker-react';
import PropTypes from 'prop-types';

const PickerWrapper = styled.div`
  position: absolute;
  bottom: 56px;
  left: 8px;
  z-index: 1000;
  box-shadow: 0 4px 10px rgba(0,0,0,0.15);
  border-radius: 12px;
  background: ${({ theme }) => theme.colors.popupBackground};
`;

function EmojiPicker({ onSelect }) {
  const pickerRef = useRef(null);

  // Close picker on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (pickerRef.current && !pickerRef.current.contains(event.target)) {
        if (typeof onSelect === 'function') {
          onSelect(null);
        }
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [onSelect]);

  const onEmojiClick = (event, emojiObject) => {
    if (emojiObject && emojiObject.emoji) {
      onSelect(emojiObject.emoji);
    }
  };

  return (
    <PickerWrapper ref={pickerRef}>
      <Picker onEmojiClick={onEmojiClick} disableSearchBar native />
    </PickerWrapper>
  );
}

EmojiPicker.propTypes = {
  onSelect: PropTypes.func.isRequired,
};

export default EmojiPicker;
