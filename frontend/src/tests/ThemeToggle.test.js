import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ThemeToggle from '../components/ThemeToggle/ThemeToggle';
import { ThemeProvider } from '../contexts/ThemeContext';

describe('ThemeToggle', () => {
  test('renders toggle button with light theme', () => {
    render(
      <ThemeProvider>
        <ThemeToggle currentTheme="light" toggleTheme={() => {}} />
      </ThemeProvider>
    );
    const button = screen.getByRole('button');
    expect(button).toHaveAccessibleName(/switch to dark theme/i);
  });

  test('renders toggle button with dark theme', () => {
    render(
      <ThemeProvider>
        <ThemeToggle currentTheme="dark" toggleTheme={() => {}} />
      </ThemeProvider>
    );
    const button = screen.getByRole('button');
    expect(button).toHaveAccessibleName(/switch to light theme/i);
  });

  test('calls toggleTheme on click', () => {
    const toggleThemeMock = jest.fn();
    render(
      <ThemeProvider>
        <ThemeToggle currentTheme="light" toggleTheme={toggleThemeMock} />
      </ThemeProvider>
    );
    const button = screen.getByRole('button');
    fireEvent.click(button);
    expect(toggleThemeMock).toHaveBeenCalledTimes(1);
  });
});
