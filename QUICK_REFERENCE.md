# Quick Reference Card

## 🚀 Start Backend
```powershell
cd backend
$env:GEMINI_API_KEY = "your_key"
$env:OPENAI_API_KEY = "your_key"
python app.py
# http://127.0.0.1:8000
```

## 🎨 Start Frontend
```powershell
cd frontend
npm install  # first time only
npm start
# http://localhost:3000
```

## 📚 API Endpoints

### Chat (Medical-Safe)
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is diabetes?"}'
```
**Response:** `{reply, sources, disclaimer}`

### Upload PDF
```bash
curl -X POST -F "file=@document.pdf" \
  http://127.0.0.1:8000/ingest-pdf
```
**Response:** `{result: {added, chunks}, filename}`

### Health Check
```bash
curl http://127.0.0.1:8000/health
```

### List Models
```bash
curl http://127.0.0.1:8000/models
```

## ✅ Safety Features

| Feature | How It Works |
|---------|-------------|
| **Rule Filter** | Blocks: diagnose, prescribe, dosage, PII |
| **Symptom Checker** | Fever+cough, chest pain, stomach pain → general info |
| **LLM Prompt** | Enforces safe responses via system message |
| **Disclaimer** | Included in every response |
| **Rate Limiting** | 30 requests/min per IP |

## 🗂️ Key Files

| File | Purpose |
|------|---------|
| `backend/app.py` | FastAPI application |
| `backend/medical_rag.py` | RAG retrieval logic |
| `frontend/src/App.js` | Main React component |
| `frontend/src/utils/api.js` | Backend API client |
| `SETUP.md` | Complete setup guide |
| `IMPLEMENTATION_SUMMARY.md` | What was built |

## 🔑 Required API Keys

- **GEMINI_API_KEY** → https://makersuite.google.com/app/apikey
- **OPENAI_API_KEY** → https://platform.openai.com/api-keys

## 📋 Environment Variables

```env
# Backend (.env in backend/)
GEMINI_API_KEY=sk-...
OPENAI_API_KEY=sk-...
CHROMA_PERSIST_DIR=./chroma_db
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Frontend (.env in frontend/)
REACT_APP_BACKEND_URL=http://127.0.0.1:8000
```

## 🧪 Test Safety Filter

```bash
# Safe question ✅
curl -X POST http://127.0.0.1:8000/chat \
  -d '{"message":"What is diabetes?"}'

# Blocked: Contains "diagnose" ❌
curl -X POST http://127.0.0.1:8000/chat \
  -d '{"message":"Can you diagnose me?"}'
# Returns: 400 with safety message

# Blocked: Contains "prescribe" ❌
curl -X POST http://127.0.0.1:8000/chat \
  -d '{"message":"What medicine should I take?"}'
# Returns: 400 with safety message
```

## 📊 Response Format

```json
{
  "reply": "Diabetes is a metabolic disorder...",
  "sources": ["mayo-clinic-diabetes.pdf"],
  "disclaimer": "This is general information...",
  "blocked": false
}
```

## 🔄 PDF Ingestion

### Direct Upload
```bash
curl -X POST -F "file=@myfile.pdf" \
  http://127.0.0.1:8000/ingest-pdf
```

### Bulk Upload (Script)
```bash
cd backend
python scripts/ingest_pdfs.py --dir ./pdfs \
  --url http://127.0.0.1:8000/ingest
```

## 🎯 Frontend Features

- 💬 Chat interface with messages
- 📚 Source attribution (shows which docs were used)
- ⚠️ Medical disclaimer banner (always visible)
- 🌙 Dark/Light theme toggle
- 📱 Responsive design
- ♿ Accessible (ARIA labels, keyboard nav)

## 🛠️ Tech Stack

**Backend:** FastAPI, Gemini API, ChromaDB, LangChain, OpenAI Embeddings
**Frontend:** React, styled-components, Hooks
**Database:** ChromaDB (vector DB)
**Search:** Semantic search with OpenAI embeddings

## 📖 Documentation

- **Full Setup:** `SETUP.md`
- **Backend Docs:** `backend/README.md`
- **Frontend Docs:** `frontend/README.md`
- **What Was Built:** `IMPLEMENTATION_SUMMARY.md`
- **API Swagger UI:** http://127.0.0.1:8000/docs (when backend running)

## ⚠️ Important Notes

- **Not for Diagnosis** — System blocks diagnostic requests
- **Always Consult Doctors** — All responses include medical disclaimer
- **Educational Use** — Demo implementation, not production-ready for healthcare
- **HIPAA** — Not HIPAA-compliant yet

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API error" / "Failed to fetch" | Ensure backend running + check REACT_APP_BACKEND_URL |
| "Import fastapi not resolved" | Run `pip install -r requirements.txt` |
| "GEMINI_API_KEY not found" | Set env: `$env:GEMINI_API_KEY = "key"` |
| Messages not appearing | Check browser console + verify backend response |
| No sources shown | Upload documents first using `/ingest-pdf` |

## ⚡ Performance Tips

- Test with `CHUNK_SIZE=500` (adjust if needed)
- Rate limit: 30 req/min (adjust MAX_REQUESTS_PER_MINUTE if needed)
- OpenAI embeddings cached after first use
- Frontend caching helps repeated queries

## 🎓 Example Workflow

1. **Start backend:** `python app.py`
2. **Start frontend:** `npm start`
3. **Upload PDF:** `curl -F "file=@doc.pdf" http://127.0.0.1:8000/ingest-pdf`
4. **Ask question:** Type in chat or use curl
5. **See response:** Reply + sources + disclaimer
6. **Review logs:** Check backend console for audit trail

## 📞 Next Steps

1. Read `SETUP.md` for detailed guide
2. Test backend endpoints with cURL
3. Upload sample medical documents
4. Test frontend UI with messages
5. Check audit logs in backend console
6. Customize for your use case

---

**Everything is ready to go! 🚀**

Questions? Check `SETUP.md` or the detailed README files.
