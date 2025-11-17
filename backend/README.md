# Medical Chat Assistant - Backend

A safe, RAG-powered medical information chatbot built with **FastAPI**, **Gemini API**, **ChromaDB**, and **LangChain**. This backend provides medical information based on trusted sources while enforcing strict safety guardrails.

---

## ⚠️ Important Disclaimers

🔴 **This chatbot is for informational purposes only. It does NOT:**
- Diagnose diseases
- Prescribe medications or dosages
- Replace professional medical advice
- Constitute medical diagnosis or treatment

✅ **Always consult a licensed healthcare professional for:**
- Diagnosis of symptoms
- Medication prescriptions
- Personalized medical advice
- Urgent or severe health concerns

---

## Architecture

```
User Input
    ↓
Safety Filter (blocks diagnosis/prescription/PII)
    ↓
Symptom Checker (rule-based general causes)
    ↓
RAG Retrieval (ChromaDB + OpenAI embeddings)
    ↓
Gemini LLM (generate safe response)
    ↓
Response + Sources + Disclaimer
```

---

## Setup

### Prerequisites
- Python 3.9+
- API Keys:
  - **Gemini API Key** (Google AI Studio: https://makersuite.google.com/app/apikey)
  - **OpenAI API Key** (for embeddings: https://platform.openai.com/api-keys)

### 1. Install Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example file and fill in your API keys:

```powershell
cp .env.example .env
# Edit .env with your GEMINI_API_KEY and OPENAI_API_KEY
```

Or set them in PowerShell:

```powershell
$env:GEMINI_API_KEY = "your_gemini_api_key"
$env:OPENAI_API_KEY = "your_openai_api_key"
```

### 3. Run the Server

```powershell
# Development mode (with auto-reload)
uvicorn app:app --host 127.0.0.1 --port 8000 --reload

# Or run via Python
python app.py
```

Server will be available at: **http://127.0.0.1:8000**

### 4. Check OpenAPI Docs

Once running, visit:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## API Endpoints

### 1. **POST /chat** - Ask Medical Questions

**Request:**
```json
{
  "message": "I have a fever and cough for two days, what could this be?"
}
```

**Response:**
```json
{
  "reply": "Fever and cough can be caused by viral infections like the common cold or flu. Seek medical attention if symptoms persist or worsen.",
  "sources": ["mayo-clinic-common-cold.pdf"],
  "disclaimer": "This is general information and not a diagnosis. Consult a healthcare professional."
}
```

**cURL Example:**
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"I have fever and cough"}'
```

**Safety Features:**
- Blocks requests mentioning: "diagnose", "prescribe", "dosage", "medication"
- Prevents PII collection: SSN, address, phone, DOB
- Returns disclaimer with every response

---

### 2. **POST /ingest-pdf** - Upload & Index PDFs

Upload a PDF directly. The server will extract text, chunk it, and store it in ChromaDB.

**cURL Example:**
```bash
curl -X POST -F "file=@path/to/medical-document.pdf" \
  http://127.0.0.1:8000/ingest-pdf
```

**Response:**
```json
{
  "result": {
    "added": 8,
    "chunks": 7
  },
  "filename": "medical-document.pdf"
}
```

**Supported Formats:** PDF files only

**Configuration:**
- `CHUNK_SIZE=500` — characters per chunk (default)
- `CHUNK_OVERLAP=50` — overlap between chunks (default)

---

### 3. **POST /ingest** - Index Pre-Extracted Documents

For bulk ingestion of pre-extracted text:

**Request:**
```json
{
  "documents": [
    {
      "id": "who-covid-1",
      "text": "Full text content extracted from document...",
      "meta": {"source": "WHO - COVID Guidelines 2024"}
    }
  ]
}
```

**Response:**
```json
{
  "result": {
    "added": 5,
    "chunks": 4
  }
}
```

**cURL Example:**
```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{
  "documents": [
    {
      "id": "doc1",
      "text": "Sample medical text content...",
      "meta": {"source": "Example Source"}
    }
  ]
}
EOF
```

---

### 4. **GET /models** - List Available Gemini Models

Returns list of available Gemini models.

**Response:**
```json
["models/gemini-2.5-flash", "models/gemini-pro", ...]
```

---

### 5. **GET /health** - Health Check

Simple endpoint to verify server is running.

**Response:**
```json
{"status": "ok"}
```

---

## Ingestion Helper Script

Use `scripts/ingest_pdfs.py` to bulk-ingest PDFs from a folder:

```powershell
# Ingest a single PDF
python scripts/ingest_pdfs.py --file path/to/document.pdf --url http://127.0.0.1:8000/ingest

# Ingest all PDFs from a folder
python scripts/ingest_pdfs.py --dir ./medical_pdfs --url http://127.0.0.1:8000/ingest
```

---

## Safety System

### Prohibited Words (Automatic Block)
- "diagnose", "diagnosis"
- "prescribe", "prescription"
- "dosage", "dose"
- "what medicine", "what drug"

### PII Protection (Automatic Block)
- SSN, Social Security numbers
- Phone numbers
- Addresses
- Date of birth

### Symptom Checker (Rule-Based)
Automatically detects and provides general info for:
- **Fever + Cough** → General viral infection info
- **Chest Pain** → Urgency warning, seek emergency care
- **Stomach Pain** → General digestive causes
- **Headache** → General causes and when to see doctor

### System Prompt (LLM-Level)
Every response enforces:
- "Provide general medical information only"
- "Never provide a diagnosis"
- "Suggest consulting a healthcare professional"
- "Cite sources from retrieval results"

---

## ChromaDB & Vector Store

### Database Location
- Default: `./chroma_db` (relative to backend folder)
- Configurable via `CHROMA_PERSIST_DIR` environment variable

### Embeddings
- Provider: **OpenAI** (requires `OPENAI_API_KEY`)
- Model: text-embedding-3-small (default)
- Automatically generated when indexing documents

### Querying
- Retrieves top 3 most relevant chunks per query
- Returns chunk ID, text, and metadata (source, chunk index)

---

## Example Workflow

### 1. Start Server
```powershell
cd backend
python app.py
# Server running at http://127.0.0.1:8000
```

### 2. Upload Medical Documents
```powershell
# Create a test PDF or use existing one
curl -X POST -F "file=@sample-medical-doc.pdf" \
  http://127.0.0.1:8000/ingest-pdf
```

### 3. Ask Questions
```powershell
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What are common symptoms of diabetes?"}'
```

### 4. Frontend Integration
Frontend calls `POST /chat` and displays:
- Bot response
- Source documents cited
- Medical disclaimer banner

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | Required | Google Gemini API key |
| `OPENAI_API_KEY` | Required | OpenAI API key (for embeddings) |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage location |
| `CHUNK_SIZE` | `500` | Document chunk size (chars) |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks (chars) |
| `PORT` | `8000` | Server port |
| `DEBUG` | `false` | Enable debug logging |
| `LOG_LEVEL` | `INFO` | Logging level |

---

## Troubleshooting

### "Import 'fastapi' could not be resolved"
- Make sure you've installed dependencies: `pip install -r requirements.txt`
- Verify you're using the correct Python environment

### "GEMINI_API_KEY not found"
- Check `.env` file exists and has the key
- Or set in PowerShell: `$env:GEMINI_API_KEY = "your_key"`

### "OPENAI_API_KEY not found"
- Required for embeddings
- Get one from https://platform.openai.com/api-keys

### "No documents in vector store"
- Use `/ingest-pdf` or `/ingest` endpoints to add medical documents
- Verify documents were added: ChromaDB should create `./chroma_db` folder

### Chat returns generic response without sources
- Ensure documents are ingested first
- Check that retrieval is working (check server logs)
- Verify OpenAI embeddings are configured correctly

---

## Performance & Best Practices

### Document Ingestion
- ✅ Prefer PDF uploads via `/ingest-pdf` (automatic extraction)
- ✅ Use consistent source naming in metadata (helps with attribution)
- ✅ Test with small docs first before bulk ingesting

### Query Performance
- Default retrieves top 3 chunks per query
- Adjust `n_results` in `medical_rag.retrieve()` if needed
- Chunk size affects retrieval quality (default 500 chars)

### Safety
- ✅ All responses include medical disclaimer
- ✅ Never share exact dosages or diagnoses
- ✅ Always recommend consulting healthcare professionals
- ⚠️ Rule-based filters are first line of defense; LLM constraints provide secondary safety

---

## Development & Testing

### Test Chat Endpoint
```powershell
# Safe question
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is diabetes?"}'

# Blocked request (contains "diagnose")
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Can you diagnose my condition?"}'
# Response: 400 error with safety message
```

### Test Health
```powershell
curl http://127.0.0.1:8000/health
```

### View Available Models
```powershell
curl http://127.0.0.1:8000/models
```

---

## License & Legal

⚠️ **This tool is provided AS-IS for educational and informational purposes only.**

- Not a substitute for professional medical advice
- Users assume full responsibility for how they use this tool
- Maintain HIPAA compliance if handling patient data
- Always recommend users consult licensed healthcare providers

---

## Next Steps

1. **Add Audit Logging** — Track user queries and bot responses for safety review
2. **Implement Rate Limiting** — Prevent abuse
3. **Enhance Intent Detection** — Use LLM to detect subtle diagnosis requests
4. **Add Frontend Integration** — Connect React frontend to display disclaimers and sources
5. **Deploy to Production** — Use uvicorn + nginx + SSL for production deployment

---

## Support

For issues or questions:
- Check the troubleshooting section above
- Review server logs: `DEBUG=true python app.py`
- Verify API keys are valid (test separately if needed)

