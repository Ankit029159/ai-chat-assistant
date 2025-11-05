import React from 'react';
import styled from 'styled-components';
import PropTypes from 'prop-types';

const ToggleWrapper = styled.button`
  background: ${({ theme }) => theme.colors.toggleBackground};
  border: none;
  border-radius: 20px;
  width: 50px;
  height: 26px;
  cursor: pointer;
  position: relative;
  padding: 3px;
  display: flex;
  align-items: center;
  justify-content: ${({ isDark }) => (isDark ? 'flex-end' : 'flex-start')};
  transition: background-color 0.3s ease;
  user-select: none;

  &:focus-visible {
    outline: 2px solid ${({ theme }) => theme.colors.focusOutline};
    outline-offset: 2px;
  }
`;

const Knob = styled.div`
  background: ${({ theme }) => theme.colors.toggleKnob};
  border-radius: 50%;
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: ${({ theme }) => theme.colors.toggleIcon};
`;

function ThemeToggle({ currentTheme, toggleTheme }) {
  const isDark = currentTheme === 'dark';

  return (
    <ToggleWrapper
      onClick={toggleTheme}
      aria-pressed={isDark}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} theme`}
      isDark={isDark}
      type="button"
    >
      <Knob>{isDark ? '🌙' : '☀️'}</Knob>
    </ToggleWrapper>
  );
}

ThemeToggle.propTypes = {
  currentTheme: PropTypes.oneOf(['light', 'dark']).isRequired,
  toggleTheme: PropTypes.func.isRequired,
};

export default ThemeToggle;
