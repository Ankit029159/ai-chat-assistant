import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { lightTheme, darkTheme } from '../styles/theme';

const ThemeContext = createContext({
  currentTheme: 'light',
  currentThemeObject: lightTheme,
  toggleTheme: () => {},
});

const STORAGE_KEY = 'react-chat-app-theme';

export function ThemeProvider({ children }) {
  const [currentTheme, setCurrentTheme] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored === 'light' || stored === 'dark') return stored;
    } catch {
      // ignore localStorage errors
    }
    const envDefault = process.env.REACT_APP_DEFAULT_THEME;
    return envDefault === 'dark' ? 'dark' : 'light';
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, currentTheme);
    } catch {
      // ignore
    }
  }, [currentTheme]);

  const toggleTheme = () => {
    setCurrentTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const currentThemeObject = useMemo(() => (currentTheme === 'light' ? lightTheme : darkTheme), [currentTheme]);

  return (
    <ThemeContext.Provider value={{ currentTheme, currentThemeObject, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
