# Medical Chat Assistant - Frontend

A React-based medical information chatbot UI that integrates with a FastAPI backend offering RAG-powered medical knowledge retrieval, safety constraints, and source attribution.

---

## Features

✅ **Medical-Safe Chat Interface**
- Real-time messaging with bot typing indicator
- Medical disclaimer banner (always visible)
- Source attribution for retrieved documents
- Automatic safety filtering (diagnoses/prescriptions blocked)

✅ **Theme Support**
- Dark/Light mode toggle
- Persistent theme preference

✅ **Accessibility**
- ARIA labels and live regions
- Keyboard navigation support
- Skip-to-input link
- Semantic HTML structure

✅ **Responsive Design**
- Mobile-friendly layout
- Responsive chat bubbles
- Flexible sidebar for conversation history

---

## Quick Start

### Prerequisites
- Node.js 14+
- Backend running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
npm start
```

Opens http://localhost:3000 automatically.

### Configure Backend

Create `.env` in frontend root:
```env
REACT_APP_BACKEND_URL=http://127.0.0.1:8000
```

---

## Project Structure

```
frontend/src/
├── components/
│   ├── ChatWindow/          # Main chat UI
│   ├── MedicalDisclaimer/   # Warning banner (NEW)
│   ├── SourcesDisplay/      # Source attribution (NEW)
│   └── ...
├── contexts/
│   ├── ChatContext.js       # State (UPDATED)
│   └── ThemeContext.js
├── utils/
│   ├── api.js               # Backend client (UPDATED)
│   └── ...
└── App.js                   # Root (UPDATED)
```

---

## Key Components (New/Updated)

### MedicalDisclaimer
- Yellow warning banner at top
- Informs users of limitations
- Always visible

### SourcesDisplay
- Shows retrieved document sources
- Appears below bot messages
- 📄 Icons for document attribution

### Updated: ChatContext
- Now handles `sources` and `disclaimer` from backend
- `blocked` flag for safety filter
- Enhanced error handling

### Updated: api.js
- `sendMessage()` handles medical responses
- New `uploadMedicalPDF()` for PDF ingestion
- Safety filter block handling (400 status)
- Rate limit handling (429 status)

---

## Usage Example

```javascript
// Automatic via UI:
1. Type: "What is diabetes?"
2. Press Enter
3. Receive response + sources + disclaimer

// Safety filter (automatic block):
1. Type: "Can you diagnose me?"
2. Response: "This type of request cannot be processed..."
```

---

## API Response Format

Backend `/chat` returns:
```json
{
  "reply": "Diabetes is a metabolic disorder...",
  "sources": ["mayo-clinic-diabetes.pdf"],
  "disclaimer": "This is general information..."
}
```

Frontend displays:
- 💬 Message bubble with reply
- 📚 Sources list
- ⚠️ Disclaimer
- ✅ All safety-filtered

---

## Accessibility

- ARIA labels & live regions
- Keyboard navigation (Tab, Enter)
- Semantic HTML
- Skip-to-input link
- High contrast ready

---

## Building for Production

```bash
npm run build
```

Creates optimized build in `build/` folder.

---

## Troubleshooting

### "API error" or "Failed to fetch"
- Check backend is running: `curl http://127.0.0.1:8000/health`
- Verify `REACT_APP_BACKEND_URL` is correct
- Check CORS is enabled on backend

### Messages not appearing
- Check browser console for errors
- Verify backend response format
- Test backend directly with cURL

### Styling broken
- Clear cache & restart: `npm start`
- Check for CSS conflicts

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `REACT_APP_BACKEND_URL` | `` | Backend API URL |

---

## Tech Stack

- **React 18** — UI framework
- **styled-components** — CSS-in-JS styling
- **React Context** — State management
- **Hooks** — useCallback, useRef, useContext

---

## Future Enhancements

- PDF upload widget in UI
- Conversation history persistence
- Export chat as PDF
- Multi-language support (i18n)
- Voice input/output
- Advanced source filtering

---

## Legal Disclaimer

⚠️ **This is a demo for educational purposes only.**

- NOT a substitute for professional medical advice
- Always consult licensed healthcare providers
- Use only for learning/research

---

## Support

See **backend/README.md** for API details and troubleshooting guide.


### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify) -->
# React Chat Application

A modern React-based chat frontend application featuring:

- Light and dark theme toggling with smooth animated transitions.
- Scrollable, virtualized chat window for high performance.
- User and bot message bubbles with glass/blur styling and animations.
- Message reactions with emojis and count.
- Attachments preview and upload support.
- Voice input using the Web Speech API.
- Emoji picker integration for easy emoji insertion.
- System notices with auto-dismiss and manual dismiss.
- Export and clear conversation functionality.
- Accessibility features including keyboard navigation and screen reader support.
- Backend integration for chat messages at `/chat` API endpoint.

---

## Prerequisites

- **Node.js**: Version 18.x or higher recommended.
- **npm**: Version 9.x or higher.
- A backend chat server accessible at the URL specified in environment variables.

---

## Installation

1. Clone the repository or copy the project files.

2. Navigate to the project directory:

    