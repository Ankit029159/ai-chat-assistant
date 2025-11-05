import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { ChatProvider } from './contexts/ChatContext';
import { ThemeProvider as CustomThemeProvider, useTheme } from './contexts/ThemeContext';
import GlobalStyles from './styles/globalStyles';

// This wrapper reads the theme from your CustomThemeProvider
function AppThemeProvider({ children }) {
  const { currentThemeObject } = useTheme();
  return <StyledThemeProvider theme={currentThemeObject}>{children}</StyledThemeProvider>;
}

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Root element with id "root" not found in the DOM.');
}

const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    {/* Provides currentTheme and toggleTheme */}
    <CustomThemeProvider>
      {/* Reads the currentThemeObject from context and passes to styled-components */}
      <AppThemeProvider>
        {/* Provides chat state */}
        <ChatProvider>
          {/* Global CSS using theme */}
          <GlobalStyles />
          <App />
        </ChatProvider>
      </AppThemeProvider>
    </CustomThemeProvider>
  </React.StrictMode>
);
