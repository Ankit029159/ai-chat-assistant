# Medical Chat Assistant - Complete Setup Guide

A full-stack medical information chatbot with **RAG retrieval**, **safety guardrails**, and **source attribution**.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                         │
│  - Chat UI with messages & sources                           │
│  - Medical disclaimer banner                                 │
│  - Theme toggle (dark/light)                                │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   BACKEND (FastAPI)                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ POST /chat                                             │ │
│  │ ├─ Safety Filter (blocks diagnosis/prescription/PII) │ │
│  │ ├─ RAG Retrieval (ChromaDB + OpenAI embeddings)      │ │
│  │ ├─ Symptom Checker (rule-based)                      │ │
│  │ ├─ LLM Response (Gemini API)                         │ │
│  │ └─ Returns: reply + sources + disclaimer              │ │
│  │                                                        │ │
│  │ POST /ingest-pdf                                      │ │
│  │ ├─ Extract text from PDF                             │ │
│  │ ├─ Auto-chunk documents                              │ │
│  │ └─ Store in ChromaDB vector DB                       │ │
│  │                                                        │ │
│  │ Other: /ingest, /models, /health                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ChromaDB (Vector Store)                                │ │
│  │ - Stores chunked medical documents                     │ │
│  │ - OpenAI embeddings for semantic search                │ │
│  │ - Persistent local storage                            │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start (5 minutes)

### Backend Setup

```powershell
# 1. Navigate to backend
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
$env:GEMINI_API_KEY = "your_gemini_key"
$env:OPENAI_API_KEY = "your_openai_key"

# 4. Run server
python app.py
# Server: http://127.0.0.1:8000
```

### Frontend Setup

```powershell
# In another terminal:

# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start dev server
npm start
# Opens: http://localhost:3000
```

### Test the Setup

```bash
# Test backend is running
curl http://127.0.0.1:8000/health

# Try a chat
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is diabetes?"}'

# Upload a PDF (if you have one)
curl -X POST -F "file=@sample.pdf" http://127.0.0.1:8000/ingest-pdf
```

---

## 🔑 API Keys Required

### 1. Gemini API Key
- Get from: https://makersuite.google.com/app/apikey
- Set env var: `GEMINI_API_KEY`
- Used for: LLM response generation

### 2. OpenAI API Key
- Get from: https://platform.openai.com/api-keys
- Set env var: `OPENAI_API_KEY`
- Used for: Document embeddings (semantic search)

Both are **required** for the system to work.

---

## 📋 Backend Features

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat` | POST | Ask medical questions (with safety checks) |
| `/ingest-pdf` | POST | Upload & index PDF files |
| `/ingest` | POST | Bulk ingest pre-extracted text |
| `/models` | GET | List available Gemini models |
| `/health` | GET | Health check |

### Safety System

**3 Layers of Safety:**

1. **Rule-Based Filter** — Blocks keywords (diagnose, prescribe, dosage, PII)
2. **Symptom Checker** — Provides general info (not diagnosis)
3. **LLM Constraints** — System prompt enforces safe responses

**Result:** All responses include medical disclaimer.

### RAG (Retrieval-Augmented Generation)

1. User asks question
2. Query vector created (OpenAI embeddings)
3. ChromaDB finds top 3 matching chunks
4. Gemini uses these + system prompt to generate response
5. Response includes source citations

---

## 🎨 Frontend Features

### Components

- **ChatWindow** — Main message interface
- **MessageBubble** — Individual message display with sources
- **MedicalDisclaimer** — Always-visible warning banner
- **SourcesDisplay** — Attribution for retrieved documents
- **ThemeToggle** — Dark/Light mode

### Styling

- styled-components for CSS-in-JS
- Responsive design
- Accessible (ARIA labels, keyboard nav)
- Dark mode support

---

## 🚀 Advanced Usage

### Upload Medical Documents

```powershell
# Single PDF
curl -X POST -F "file=@mayo-clinic-diabetes.pdf" \
  http://127.0.0.1:8000/ingest-pdf

# Multiple PDFs via script
cd backend
python scripts/ingest_pdfs.py --dir ./medical_pdfs \
  --url http://127.0.0.1:8000/ingest
```

### Configure Document Chunking

Edit env vars:
```env
CHUNK_SIZE=500      # Characters per chunk
CHUNK_OVERLAP=50    # Overlap between chunks
```

Larger chunks = better for long docs, worse for specific queries.

### View Logs

Backend logs all requests:
```
2025-11-17 10:30:45,123 - INFO - {"timestamp": "...", "event_type": "chat_request", "data": {...}}
```

---

## 🛡️ Safety Guardrails

### Blocked Patterns

```
❌ "Can you diagnose me?"
❌ "What medicine should I take?"
❌ "Give me a dosage"
❌ Request with SSN/phone/DOB (PII)

✅ "What is diabetes?"
✅ "What are COVID symptoms?"
✅ "How does the immune system work?"
```

### Rate Limiting

- **30 requests per minute** per IP
- Returns: 429 error with "Too many requests"

### Audit Logging

All events logged:
- Chat requests
- Blocked requests
- PDF ingestion
- Errors

Check logs in console output.

---

## 📁 Directory Structure

```
ai-assistant/
├── backend/
│   ├── app.py                    # FastAPI app
│   ├── medical_rag.py            # RAG logic
│   ├── requirements.txt          # Dependencies
│   ├── .env.example              # Environment template
│   ├── scripts/
│   │   └── ingest_pdfs.py        # PDF ingestion helper
│   ├── chroma_db/                # Vector DB (auto-created)
│   └── README.md                 # Backend docs
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow/
│   │   │   ├── MedicalDisclaimer/      # NEW
│   │   │   ├── SourcesDisplay/         # NEW
│   │   │   └── ...
│   │   ├── contexts/
│   │   │   └── ChatContext.js          # UPDATED
│   │   ├── utils/
│   │   │   └── api.js                  # UPDATED
│   │   └── App.js                      # UPDATED
│   ├── package.json
│   └── README.md                 # Frontend docs
│
└── SETUP.md                      # This file
```

---

## ⚙️ Configuration Reference

### Backend .env

```env
# Required API Keys
GEMINI_API_KEY=sk-...
OPENAI_API_KEY=sk-...

# Optional
CHROMA_PERSIST_DIR=./chroma_db
CHUNK_SIZE=500
CHUNK_OVERLAP=50
PORT=8000
DEBUG=true
LOG_LEVEL=INFO
```

### Frontend .env

```env
# Backend URL (optional, defaults to same origin)
REACT_APP_BACKEND_URL=http://127.0.0.1:8000
```

---

## 🧪 Testing

### Manual Testing (cURL)

```bash
# Health check
curl http://127.0.0.1:8000/health

# Safe question
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is diabetes?"}'

# Blocked request (diagnose)
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Can you diagnose my symptoms?"}'
# Returns 400 with safety message

# Symptom check (fever+cough)
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"I have fever and cough"}'
```

### Browser DevTools

1. Open http://localhost:3000
2. Open DevTools (F12)
3. Go to Network tab
4. Send messages
5. Inspect `/chat` request/response

---

## 🐛 Troubleshooting

### Backend Won't Start

```
Error: "GEMINI_API_KEY not found"
→ Set env: $env:GEMINI_API_KEY = "your_key"

Error: "Import 'fastapi' could not be resolved"
→ Run: pip install -r requirements.txt

Error: "Address already in use :8000"
→ Kill existing process or change PORT
```

### Frontend Can't Connect to Backend

```
Network Error in browser console
→ Verify backend is running: curl http://127.0.0.1:8000/health
→ Check REACT_APP_BACKEND_URL env var
→ Verify CORS is enabled (it is in the FastAPI app)
```

### No Sources Shown in Response

```
→ Upload medical documents first using /ingest-pdf
→ Check ChromaDB folder exists: ./chroma_db/
→ Verify OpenAI embeddings are working
```

---

## 📈 Performance Tips

1. **Document Chunking** — Test different CHUNK_SIZE values
2. **Rate Limiting** — Adjust MAX_REQUESTS_PER_MINUTE if needed
3. **Caching** — Frontend browser cache helps repeated queries
4. **Embeddings** — OpenAI embeddings cached after first use

---

## 🔐 Security Considerations

**Production Deployment:**

- ✅ Use environment variables for API keys (never hardcode)
- ✅ Use HTTPS for all traffic
- ✅ Implement proper CORS restrictions
- ✅ Add authentication/authorization
- ✅ Enable rate limiting (already in place)
- ✅ Log and monitor for abuse
- ✅ Regular security audits
- ✅ Keep dependencies updated

---

## 📚 Documentation

- **Backend Detailed Docs:** See `backend/README.md`
- **Frontend Component Guide:** See `frontend/README.md`
- **API Specs:** Swagger UI at http://127.0.0.1:8000/docs (when backend running)

---

## ✨ What's Included

### Backend (FastAPI + Gemini + ChromaDB)
- ✅ RAG retrieval with semantic search
- ✅ Document chunking (auto-configured)
- ✅ Safety filtering (rule-based + LLM)
- ✅ Audit logging
- ✅ Rate limiting
- ✅ PDF ingestion
- ✅ Swagger API docs

### Frontend (React)
- ✅ Beautiful chat UI
- ✅ Medical disclaimer banner
- ✅ Source attribution display
- ✅ Dark/Light theme
- ✅ Responsive design
- ✅ Accessibility (ARIA, keyboard nav)
- ✅ Error handling

---

## 🚀 Next Steps

1. **[x]** Set up backend (FastAPI + Gemini + ChromaDB)
2. **[x]** Set up frontend (React)
3. **[x]** Add safety system (rules + LLM)
4. **[x]** Add RAG retrieval (semantic search)
5. **[x]** Add PDF ingestion
6. **[x]** Add logging & rate limiting
7. **[x]** Integrate frontend with backend
8. **[ ]** Add sample medical documents
9. **[ ]** Deploy to production
10. **[ ]** Monitor and iterate

---

## 📞 Support

For issues:
1. Check **backend/README.md** for backend-specific help
2. Check **frontend/README.md** for frontend-specific help
3. Review **Troubleshooting** section above
4. Check browser console (frontend) or server logs (backend)

---

## ⚠️ Legal Disclaimer

🔴 **This is a demo for educational purposes only.**

- **NOT a substitute** for professional medical advice
- **NOT a diagnostic tool** — never use for diagnosis
- **Always consult** a licensed healthcare provider
- **Use only** for learning and research

---

## 📄 License

MIT License - Feel free to use and modify.

---

## 🎉 You're All Set!

Your medical chat assistant is ready. Start the backend and frontend, ask a question, and see the RAG-powered medical chatbot in action!

```powershell
# Backend (Terminal 1)
cd backend; python app.py

# Frontend (Terminal 2)
cd frontend; npm start
```

Questions? Check the README files in each directory.
