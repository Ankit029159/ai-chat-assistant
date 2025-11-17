from fastapi import FastAPI, Request, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
import os
import medical_rag
import uvicorn
from pdfminer.high_level import extract_text
import tempfile
import json
import logging
from datetime import datetime
from collections import defaultdict
import time

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory rate limiting (IP-based)
request_count = defaultdict(list)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-flash")

app = FastAPI(title="Medical Chat Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Rate Limiting (requests per minute) ---
MAX_REQUESTS_PER_MINUTE = 30


def check_rate_limit(client_ip: str) -> bool:
    now = time.time()
    # Clean old requests (older than 60 seconds)
    request_count[client_ip] = [t for t in request_count[client_ip] if now - t < 60]
    
    if len(request_count[client_ip]) >= MAX_REQUESTS_PER_MINUTE:
        return False
    request_count[client_ip].append(now)
    return True


# --- Audit Logging ---
def log_audit(event_type: str, data: dict):
    """Log important events for audit trail."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "data": data
    }
    logger.info(json.dumps(log_entry))


class ChatRequest(BaseModel):
    message: str


class IngestDoc(BaseModel):
    id: str
    text: str
    meta: dict = {}


# --- Safety rules and symptom checker ---
PROHIBITED_WORDS = [
    "diagnose",
    "diagnosis",
    "prescribe",
    "prescription",
    "dosage",
    "dose",
    "what medicine",
    "what drug",
]

PII_WORDS = ["ssn", "social security", "address", "phone", "dob", "date of birth"]


def safety_check(text: str) -> tuple[bool, str]:
    lower = text.lower()
    for w in PROHIBITED_WORDS:
        if w in lower:
            return False, "I can't provide diagnoses, prescriptions, or exact dosages. Please consult a licensed healthcare professional."
    for p in PII_WORDS:
        if p in lower:
            return False, "I cannot collect or process personal private information. Please avoid sharing PII."
    return True, ""


def symptom_checker(text: str) -> str:
    lower = text.lower()
    # Simple rule-based matches
    if "fever" in lower and ("cough" in lower or "cold" in lower):
        return "Possible causes include common viral infections (flu, common cold) — seek medical care if severe or persistent."
    if "chest pain" in lower or ("pain" in lower and "chest" in lower):
        return "Chest pain can be serious (cardiac, pulmonary). Seek emergency care if severe, sudden, or accompanied by shortness of breath."
    if "stomach pain" in lower or "abdominal pain" in lower:
        return "Common causes include gas, indigestion, gastritis, infection; seek a doctor if pain is severe or persistent."
    if "headache" in lower:
        return "Headaches have many causes: tension, dehydration, migraine, or more serious causes — consult a clinician for recurrent or severe headaches."
    return "If you're experiencing symptoms, these may have many causes. Consult a healthcare professional for personalized advice."


@app.post("/chat")
async def chat(req: ChatRequest, request: Request):
    client_ip = request.client.host
    
    # Rate limiting
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for {client_ip}")
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    
    user_message = req.message
    
    # Log incoming request
    log_audit("chat_request", {"ip": client_ip, "message_length": len(user_message)})
    
    allowed, reason = safety_check(user_message)
    if not allowed:
        log_audit("chat_blocked", {"ip": client_ip, "reason": "safety_filter"})
        raise HTTPException(status_code=400, detail={"reply": reason, "disclaimer": "Not medical advice."})

    # Retrieve relevant medical documents
    try:
        retrieved = medical_rag.retrieve(user_message, n_results=3)
        contexts = "\n\n".join([f"Source: {d.get('meta', {}).get('source','unknown')}\n{d.get('text','')}" for d in retrieved.get('results', [])])
    except Exception as e:
        contexts = ""
        retrieved = {"results": []}
        logger.error(f"RAG retrieval error: {e}")

    # Build prompt with strict system instruction and retrieved context
    system_prompt = (
        "You are a medical information assistant. Provide general medical information only. "
        "Never provide a diagnosis or exact medical dosages. Always suggest consulting a licensed healthcare professional for personalized care. "
        "When answering, prefer information from the provided sources and cite them when relevant."
    )

    symptom_advice = symptom_checker(user_message)

    prompt = f"{system_prompt}\n\nRetrieved sources:\n{contexts}\n\nUser question: {user_message}\n\nGeneral advice (do NOT diagnose): {symptom_advice}\n\nAnswer concisely and include a clear disclaimer: 'This is general information and not a diagnosis. See a medical professional.'"

    # Generate response from Gemini
    response = model.generate_content(prompt)
    reply = getattr(response, "text", None) or (response.candidates[0].content if getattr(response, "candidates", None) else "No response from Gemini.")
    if hasattr(reply, "strip"):
        reply = reply.strip()

    sources = [d.get("meta", {}).get("source") for d in retrieved.get("results", [])]

    # Log successful response
    log_audit("chat_response", {"ip": client_ip, "sources_count": len(sources)})
    
    logger.info(f"🧍 User: {user_message[:100]}")
    logger.info(f"🤖 Bot: {reply[:100]}")

    return {"reply": reply, "sources": sources, "disclaimer": "This is general information and not a diagnosis. Consult a healthcare professional."}


@app.post("/ingest")
async def ingest(docs: list[IngestDoc]):
    if not docs:
        raise HTTPException(status_code=400, detail="No documents provided.")
    # convert Pydantic models to dicts expected by medical_rag
    raw_docs = [{"id": d.id, "text": d.text, "meta": d.meta} for d in docs]
    res = medical_rag.ingest_documents(raw_docs)
    return {"result": res}


@app.post("/ingest-pdf")
async def ingest_pdf(file: UploadFile = File(...), request: Request = None):
    """Upload a PDF file directly, extract text, chunk, and ingest into Chroma."""
    client_ip = request.client.host if request else "unknown"
    
    if not file.filename.lower().endswith(".pdf"):
        log_audit("ingest_rejected", {"ip": client_ip, "reason": "non_pdf_file", "filename": file.filename})
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    log_audit("ingest_started", {"ip": client_ip, "filename": file.filename})
    
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Extract text from PDF
        text = extract_text(tmp_path)
        os.unlink(tmp_path)  # Clean up temp file
        
        if not text.strip():
            log_audit("ingest_failed", {"ip": client_ip, "reason": "no_text_extracted", "filename": file.filename})
            raise HTTPException(status_code=400, detail="No text extracted from PDF.")
        
        # Create document and ingest
        doc = {
            "id": os.path.splitext(file.filename)[0],
            "text": text,
            "meta": {"source": file.filename}
        }
        res = medical_rag.ingest_documents([doc], chunk=True)
        
        log_audit("ingest_success", {"ip": client_ip, "filename": file.filename, "chunks": res.get("chunks", 0)})
        logger.info(f"📥 Ingested: {file.filename} - {res['added']} items, {res.get('chunks', 0)} chunks")
        
        return {"result": res, "filename": file.filename}
    
    except Exception as e:
        logger.error(f"PDF ingest error: {e}")
        log_audit("ingest_error", {"ip": client_ip, "filename": file.filename, "error": str(e)})
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


@app.get("/models")
async def list_models():
    models = [m.name for m in genai.list_models()]
    return models


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
