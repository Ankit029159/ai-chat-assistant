import { createGlobalStyle } from 'styled-components';

const GlobalStyles = createGlobalStyle`
  /* Reset and base */
  *, *::before, *::after {
    box-sizing: border-box;
  }

  html, body, #root {
    height: 100%;
    margin: 0;
    padding: 0;
    background-color: ${({ theme }) => theme.colors.background};
    color: ${({ theme }) => theme.colors.textPrimary};
    font-family: ${({ theme }) => theme.fonts.primary};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  body {
    overflow: hidden;
  }

  /* Scrollbar */
  ::-webkit-scrollbar {
    width: 10px;
    height: 10px;
  }

  ::-webkit-scrollbar-track {
    background: ${({ theme }) => theme.colors.scrollbarTrack};
  }

  ::-webkit-scrollbar-thumb {
    background-color: ${({ theme }) => theme.colors.scrollbarThumb};
    border-radius: 10px;
    border: 2px solid ${({ theme }) => theme.colors.scrollbarTrack};
  }

  /* Focus outlines for accessibility */
  :focus-visible {
    outline: 2px solid ${({ theme }) => theme.colors.focusOutline};
    outline-offset: 2px;
  }

  a {
    color: ${({ theme }) => theme.colors.linkColor};
    text-decoration: none;
  }

  a:hover,
  a:focus {
    text-decoration: underline;
  }

  button {
    font-family: ${({ theme }) => theme.fonts.primary};
  }

  /* Utility */
  .sr-only {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    padding: 0 !important;
    margin: -1px !important;
    overflow: hidden !important;
    clip: rect(0, 0, 0, 0) !important;
    border: 0 !important;
  }
`;

export default GlobalStyles;
