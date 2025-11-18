"""
Medical Chat Assistant API.

FastAPI-based REST API for medical information retrieval with RAG (Retrieval-Augmented Generation),
safety filters, and local demonstration mode with fallback support.

Key Features:
  - Chat endpoint with medical context awareness
  - PDF document ingestion with automatic chunking
  - Safety filters for diagnosis/prescription prevention
  - Rule-based symptom checker
  - Rate limiting (30 requests/minute per IP)
  - Comprehensive audit logging
  - Graceful fallback when Gemini API unavailable
  - CORS-enabled for frontend integration
"""

from typing import List, Dict, Any, Tuple, Optional
from fastapi import FastAPI, Request, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# === Custom Exceptions ===

class MedicalAssistantException(Exception):
    """Base exception for medical assistant errors."""
    pass


class GeminiInitializationError(MedicalAssistantException):
    """Raised when Gemini API initialization fails."""
    pass


class SafetyFilterException(MedicalAssistantException):
    """Raised when message violates safety policy."""
    pass


class RAGRetrievalError(MedicalAssistantException):
    """Raised when document retrieval fails."""
    pass


class PDFProcessingError(MedicalAssistantException):
    """Raised when PDF extraction/processing fails."""
    pass

# In-memory rate limiting (IP-based request tracking)
request_count: Dict[str, List[float]] = defaultdict(list)

# Configuration constants
MAX_REQUESTS_PER_MINUTE: int = 30
RATE_LIMIT_WINDOW_SECS: int = 60
GEMINI_MODEL_NAME: str = "models/gemini-2.5-flash"

# Safety filter keywords
PROHIBITED_WORDS: List[str] = [
    "diagnose",
    "diagnosis",
    "prescribe",
    "prescription",
    "dosage",
    "dose",
    "what medicine",
    "what drug",
]

PII_WORDS: List[str] = [
    "ssn",
    "social security",
    "address",
    "phone",
    "dob",
    "date of birth"
]

MEDICAL_DISCLAIMER: str = (
    "This is general medical information and not a diagnosis or treatment recommendation. "
    "Always consult a licensed healthcare professional for personalized medical advice."
)

# Medical severity levels and triage guidelines
SEVERITY_LEVELS: Dict[str, Dict[str, Any]] = {
    "critical": {
        "level": 3,
        "indicator": "🚨 URGENT - SEEK EMERGENCY CARE",
        "guidance": "Seek immediate emergency care (call 911 or go to ER)"
    },
    "high": {
        "level": 2,
        "indicator": "⚠️ IMPORTANT - CONSULT HEALTHCARE PROVIDER TODAY",
        "guidance": "Contact a healthcare provider today or visit urgent care"
    },
    "moderate": {
        "level": 1,
        "indicator": "ℹ️ MONITOR - See doctor if symptoms persist",
        "guidance": "Consult a healthcare provider if symptoms worsen or persist >3 days"
    },
    "low": {
        "level": 0,
        "indicator": "ℹ️ General Information",
        "guidance": "Monitor at home; consult if symptoms develop or worsen"
    }
}

# Symptom patterns for differential diagnosis
SYMPTOM_PATTERNS: Dict[str, Dict[str, Any]] = {
    "chest_pain": {
        "keywords": ["chest pain", "chest discomfort", "pressure in chest"],
        "severity": "critical",
        "differential": [
            "Acute coronary syndrome (ACS) / Heart attack",
            "Pulmonary embolism (PE)",
            "Aortic dissection",
            "Pneumothorax (collapsed lung)",
            "Severe gastroesophageal reflux disease (GERD)",
            "Costochondritis (chest wall inflammation)"
        ],
        "red_flags": [
            "Severe intensity",
            "Sudden onset",
            "Associated shortness of breath",
            "Dizziness or syncope",
            "Sweating or pale appearance"
        ]
    },
    "severe_headache": {
        "keywords": ["severe headache", "worst headache", "thunderclap headache"],
        "severity": "critical",
        "differential": [
            "Subarachnoid hemorrhage (SAH)",
            "Meningitis",
            "Stroke",
            "Temporal arteritis",
            "Severe migraine",
            "Acute glaucoma"
        ],
        "red_flags": [
            "Sudden onset (thunderclap)",
            "High fever",
            "Neck stiffness",
            "Vision changes",
            "Focal neurological deficits"
        ]
    },
    "severe_abdominal_pain": {
        "keywords": ["severe abdominal pain", "severe stomach pain", "acute abdomen"],
        "severity": "critical",
        "differential": [
            "Appendicitis",
            "Acute pancreatitis",
            "Bowel obstruction",
            "Perforated viscus",
            "Acute cholecystitis (gallbladder)",
            "Ectopic pregnancy (if female)"
        ],
        "red_flags": [
            "Severe intensity",
            "Fever (>101°F)",
            "Vomiting/retching",
            "Blood in stool/vomit",
            "Distended abdomen"
        ]
    },
    "fever_with_rash": {
        "keywords": ["fever", "rash", "spots", "meningitis"],
        "severity": "critical",
        "differential": [
            "Meningitis",
            "Measles",
            "Scarlet fever",
            "Rocky Mountain spotted fever",
            "Viral exanthem"
        ],
        "red_flags": [
            "Non-blanching petechial rash",
            "Neck stiffness",
            "Altered mental status",
            "High fever"
        ]
    },
    "difficulty_breathing": {
        "keywords": ["shortness of breath", "trouble breathing", "can't breathe", "dyspnea"],
        "severity": "critical",
        "differential": [
            "Acute coronary syndrome",
            "Pulmonary embolism",
            "Asthma/COPD exacerbation",
            "Pneumonia",
            "Anaphylaxis",
            "Pneumothorax"
        ],
        "red_flags": [
            "At rest or minimal exertion",
            "Associated chest pain",
            "Wheezing or stridor",
            "Cyanosis",
            "Altered consciousness"
        ]
    },
    "chest_trauma": {
        "keywords": ["chest injury", "chest trauma", "rib pain after injury"],
        "severity": "high",
        "differential": [
            "Rib fractures",
            "Pulmonary contusion",
            "Hemothorax",
            "Pneumothorax",
            "Cardiac contusion"
        ],
        "red_flags": [
            "Difficulty breathing",
            "Asymmetric breath sounds",
            "Hypotension"
        ]
    },
    "fever": {
        "keywords": ["fever", "temperature", "chills"],
        "severity": "moderate",
        "differential": [
            "Viral infection (flu, cold, COVID-19)",
            "Bacterial infection (UTI, pneumonia, strep)",
            "Fungal infection",
            "Medications (drug fever)"
        ],
        "red_flags": [
            "Very high fever (>104°F)",
            "Fever >7 days",
            "Associated severe symptoms",
            "Immunocompromised"
        ]
    },
    "headache": {
        "keywords": ["headache"],
        "severity": "low",
        "differential": [
            "Tension headache",
            "Migraine",
            "Sinus headache",
            "Caffeine withdrawal",
            "Dehydration"
        ],
        "red_flags": [
            "Change in pattern",
            "Sudden worst ever",
            "With fever/stiff neck",
            "With focal deficits"
        ]
    }
}


# === Gemini Model Initialization ===

class LocalFallbackModel:
    """Fallback model for when Gemini API is unavailable.
    
    Provides safe placeholder responses in development/demo mode.
    Maintains API compatibility with google.generativeai.GenerativeModel.
    """
    
    def __init__(self, error_message: Optional[str] = None):
        """
        Args:
            error_message: Optional error details to include in response.
        """
        self.error_message = error_message
    
    def generate_content(self, prompt: str) -> "FallbackResponse":
        """
        Generate content (fallback mode).
        
        Args:
            prompt: User prompt.
        
        Returns:
            FallbackResponse object with text attribute.
        """
        if self.error_message:
            message = (
                f"Gemini API unavailable: {self.error_message}. "
                f"Running in fallback demo mode.\n\n"
                f"Received prompt: {prompt[:150]}..."
            )
        else:
            message = (
                "Running in local demo mode (Gemini API key not configured).\n\n"
                f"Received prompt: {prompt[:150]}..."
            )
        return FallbackResponse(message)


class FallbackResponse:
    """Fallback response object compatible with Gemini responses."""
    
    def __init__(self, text: str):
        """
        Args:
            text: Response text.
        """
        self.text = text
        self.candidates = []


# Initialize Gemini model with fallback support
model: Optional[Any] = None
try:
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_KEY:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        logger.info(f"✅ Gemini API configured with model: {GEMINI_MODEL_NAME}")
    else:
        model = LocalFallbackModel()
        logger.warning("⚠️  GEMINI_API_KEY not set — using local fallback model for responses")
except Exception as e:
    model = LocalFallbackModel(error_message=str(e))
    logger.exception(f"❌ Failed to initialize Gemini: {type(e).__name__}: {e}")


# === FastAPI App Setup ===

app = FastAPI(
    title="Medical Chat Assistant",
    description="Medical information retrieval API with RAG and safety filters",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Rate Limiting ===

def check_rate_limit(client_ip: str) -> bool:
    """
    Check if client has exceeded rate limit.
    
    Implements sliding window rate limiting (30 requests per minute per IP).
    
    Args:
        client_ip: Client IP address.
    
    Returns:
        bool: True if request is allowed, False if rate limit exceeded.
    
    Notes:
        - Removes requests older than 60 seconds from tracking
        - Allows 30 requests per sliding 60-second window
        - Records new request timestamp if allowed
    """
    now = time.time()
    
    # Clean old requests (older than window)
    request_count[client_ip] = [
        t for t in request_count[client_ip]
        if now - t < RATE_LIMIT_WINDOW_SECS
    ]
    
    # Check if limit exceeded
    if len(request_count[client_ip]) >= MAX_REQUESTS_PER_MINUTE:
        return False
    
    # Record this request
    request_count[client_ip].append(now)
    return True


# === Audit Logging ===

def log_audit(event_type: str, data: Dict[str, Any]) -> None:
    """
    Log event to audit trail.
    
    Args:
        event_type: Type of event (e.g., "chat_request", "chat_blocked", "ingest_success").
        data: Event-specific data to log.
    
    Notes:
        - Includes ISO timestamp automatically
        - Logs as structured JSON for parsing
        - Used for security audit trail and monitoring
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "data": data
    }
    logger.info(json.dumps(log_entry))


# === Pydantic Models ===

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User message/question for the medical assistant"
    )


class IngestDoc(BaseModel):
    """Document ingestion model."""
    id: str = Field(..., description="Document identifier")
    text: str = Field(..., description="Document text content")
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional document metadata (source, date, author, etc)"
    )


# === Safety & Diagnosis Functions ===

def safety_check(text: str) -> Tuple[bool, str]:
    """
    Check if message violates safety policies.
    
    Detects attempts to request diagnoses, prescriptions, or PII collection.
    
    Args:
        text: User message text.
    
    Returns:
        Tuple[bool, str]: (is_safe, error_message)
            - is_safe: True if message passes safety check
            - error_message: Explanation if blocked, empty string if allowed
    
    Raises:
        SafetyFilterException: When severe violations detected (optional future enhancement).
    
    Notes:
        - Checks for diagnosis/prescription keywords (case-insensitive)
        - Checks for PII keywords (case-insensitive)
        - Does not perform full NLP analysis (lightweight implementation)
    """
    lower_text = text.lower()
    
    # Check for prohibited medical advice requests
    for word in PROHIBITED_WORDS:
        if word in lower_text:
            return False, (
                "I can't provide diagnoses, prescriptions, or exact dosages. "
                "Please consult a licensed healthcare professional for medical advice."
            )
    
    # Check for PII requests
    for pii_word in PII_WORDS:
        if pii_word in lower_text:
            return False, (
                "I cannot collect or process personal private information. "
                "Please avoid sharing SSN, phone numbers, addresses, or dates of birth."
            )
    
    return True, ""


def get_symptom_severity(text: str) -> Tuple[str, Dict[str, Any]]:
    """
    Assess symptom severity and return triage guidance.
    
    Args:
        text (str): User message describing symptoms.
    
    Returns:
        Tuple[str, Dict]: (severity_level, triage_info)
            - severity_level: "critical", "high", "moderate", "low"
            - triage_info: Dict with indicator, guidance, differential diagnoses
    
    Notes:
        - Critical: life-threatening symptoms requiring emergency care
        - High: serious symptoms requiring same-day evaluation
        - Moderate: concerning symptoms requiring prompt evaluation
        - Low: minor symptoms that can be monitored
    """
    lower_text = text.lower()
    max_severity_level = -1
    matched_pattern = None
    
    # Check for critical and high-severity patterns first
    for pattern_key, pattern_info in SYMPTOM_PATTERNS.items():
        keywords = pattern_info.get("keywords", [])
        if any(keyword in lower_text for keyword in keywords):
            severity = pattern_info.get("severity", "low")
            severity_level = SEVERITY_LEVELS[severity]["level"]
            
            if severity_level > max_severity_level:
                max_severity_level = severity_level
                matched_pattern = pattern_info
    
    # Determine final severity level
    if max_severity_level >= 3:
        final_severity = "critical"
    elif max_severity_level >= 2:
        final_severity = "high"
    elif max_severity_level >= 1:
        final_severity = "moderate"
    else:
        final_severity = "low"
    
    severity_info = SEVERITY_LEVELS[final_severity].copy()
    
    # Add differential diagnosis if pattern matched
    if matched_pattern:
        severity_info["differential"] = matched_pattern.get("differential", [])
        severity_info["red_flags"] = matched_pattern.get("red_flags", [])
    
    return final_severity, severity_info


def generate_triage_response(text: str) -> str:
    """
    Generate triage-aware response with severity guidance.
    
    Args:
        text (str): User symptom description.
    
    Returns:
        str: Formatted triage guidance with severity indicator.
    
    Notes:
        - Includes severity level indicator (emoji-based)
        - Lists possible differential diagnoses
        - Highlights red flag symptoms
        - Recommends appropriate care level
    """
    severity, info = get_symptom_severity(text)
    lower_text = text.lower()
    
    response = f"{info['indicator']}\n\n"
    
    # Add differential diagnosis if available
    if "differential" in info and info["differential"]:
        response += "**Possible causes to discuss with a healthcare provider:**\n"
        for diagnosis in info["differential"][:5]:  # Limit to 5
            response += f"• {diagnosis}\n"
        response += "\n"
    
    # Add red flags if applicable
    if "red_flags" in info and info["red_flags"]:
        response += "**Red flags that warrant immediate evaluation:**\n"
        for flag in info["red_flags"][:4]:  # Limit to 4
            response += f"• {flag}\n"
        response += "\n"
    
    # Care recommendation
    response += f"**Recommended action:** {info['guidance']}\n\n"
    response += "**What to do now:**\n"
    
    if severity == "critical":
        response += (
            "1. Call 911 or go to the nearest emergency room immediately\n"
            "2. Do not drive yourself if symptoms are severe\n"
            "3. Inform emergency responders of all symptoms\n"
        )
    elif severity == "high":
        response += (
            "1. Contact your healthcare provider or urgent care clinic today\n"
            "2. If unable to reach provider, visit urgent care\n"
            "3. Prepare a list of all symptoms and when they started\n"
        )
    else:
        response += (
            "1. Monitor your symptoms closely\n"
            "2. Stay hydrated and get adequate rest\n"
            "3. Contact your doctor if symptoms worsen or persist\n"
        )
    
    response += f"\n{MEDICAL_DISCLAIMER}"
    return response


def symptom_checker(text: str) -> str:
    """
    Rule-based symptom checking and general guidance.
    
    Args:
        text: User message text.
    
    Returns:
        str: Symptom guidance or generic response.
    
    Notes:
        - Uses simple keyword matching (not ML-based)
        - Returns conservative, disclaimer-inclusive guidance
        - All responses recommend professional consultation
        - Future enhancement: ML-based NLP for accuracy
    """
    return generate_triage_response(text)


@app.post("/chat", tags=["Chat"])
async def chat(req: ChatRequest, request: Request) -> Dict[str, Any]:
    """
    Chat endpoint for medical information retrieval.
    
    Retrieves relevant medical documents via RAG, applies safety filters,
    and generates responses using Gemini API (or fallback model).
    
    Args:
        req: ChatRequest with user message.
        request: FastAPI request object (for client IP tracking).
    
    Returns:
        Dict with keys:
            - "reply": Generated response text
            - "sources": List of source document names used
            - "disclaimer": Legal/medical disclaimer
    
    Raises:
        HTTPException 429: Too many requests (rate limit exceeded).
        HTTPException 400: Safety filter violation (diagnosis/prescription/PII).
        HTTPException 500: RAG retrieval or Gemini error (returns fallback response).
    
    Notes:
        - Rate limited to 30 requests/minute per IP
        - All requests logged to audit trail
        - Safety filter applied before processing
        - Retrieved medical documents included in prompt context
        - Symptom checker provides pre-computed guidance
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # === Rate Limiting ===
    if not check_rate_limit(client_ip):
        logger.warning(f"⚠️  Rate limit exceeded for IP: {client_ip}")
        log_audit("rate_limit_exceeded", {"ip": client_ip})
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later (30 requests/minute limit)."
        )
    
    user_message = req.message
    
    # === Log Request ===
    log_audit("chat_request", {
        "ip": client_ip,
        "message_length": len(user_message)
    })
    
    # === Safety Check ===
    is_safe, safety_error = safety_check(user_message)
    if not is_safe:
        logger.info(f"⛔ Safety filter blocked message from {client_ip}: {safety_error[:50]}")
        log_audit("chat_blocked", {
            "ip": client_ip,
            "reason": "safety_filter",
            "blocked_reason": safety_error
        })
        raise HTTPException(
            status_code=400,
            detail={
                "reply": safety_error,
                "disclaimer": MEDICAL_DISCLAIMER
            }
        )
    
    # === Retrieve Medical Context ===
    contexts = ""
    sources = []
    retrieved = {"results": []}
    
    try:
        retrieved = medical_rag.retrieve(user_message, n_results=3)
        contexts = "\n\n".join([
            f"Source: {d.get('meta', {}).get('source', 'unknown')}\n{d.get('text', '')}"
            for d in retrieved.get('results', [])
        ])
        sources = [d.get('meta', {}).get('source') for d in retrieved.get('results', [])]
        logger.debug(f"📚 Retrieved {len(sources)} medical documents for query: {user_message[:50]}")
    except Exception as e:
        logger.error(f"RAG retrieval error: {type(e).__name__}: {e}")
        log_audit("rag_retrieval_error", {
            "ip": client_ip,
            "error": str(e)
        })
        # Continue with empty context (graceful degradation)
    
    # === Build Prompt ===
    system_prompt = (
        "You are a medical information assistant. Provide general medical information only. "
        "NEVER provide a diagnosis, prescribe medications, or give exact medical dosages. "
        "Always recommend consulting a licensed healthcare professional for personalized care. "
        "When answering, prefer information from the provided sources and cite them when relevant. "
        "End every response with the disclaimer: 'This is general information. Consult a medical professional.'"
    )
    
    symptom_advice = symptom_checker(user_message)
    
    prompt = (
        f"{system_prompt}\n\n"
        f"Retrieved Medical Sources:\n{contexts}\n\n"
        f"User Question: {user_message}\n\n"
        f"General Symptom Guidance (do NOT diagnose): {symptom_advice}\n\n"
        f"Provide a concise, helpful response. Include the medical disclaimer at the end."
    )
    
    # === Generate Response ===
    try:
        response = model.generate_content(prompt)
        reply = getattr(response, "text", None) or (
            response.candidates[0].content if getattr(response, "candidates", None) else
            "I'm unable to generate a response right now. Please try again later."
        )
        if hasattr(reply, "strip"):
            reply = reply.strip()
    except Exception as e:
        logger.error(f"Gemini generation error: {type(e).__name__}: {e}")
        reply = (
            "I encountered an error while processing your request. "
            "Please try again. " + MEDICAL_DISCLAIMER
        )
    
    # === Log Success ===
    log_audit("chat_response", {
        "ip": client_ip,
        "sources_count": len(sources),
        "reply_length": len(reply)
    })
    
    logger.info(f"👤 User: {user_message[:80]}")
    logger.info(f"🤖 Assistant: {reply[:80]}...")
    
    return {
        "reply": reply,
        "sources": sources,
        "disclaimer": MEDICAL_DISCLAIMER
    }


@app.post("/ingest", tags=["Document Management"])
async def ingest(docs: List[IngestDoc]) -> Dict[str, Any]:
    """
    Ingest documents into RAG store.
    
    Accepts one or more documents with text and metadata.
    Automatically chunks large documents and stores in ChromaDB (or JSON fallback).
    
    Args:
        docs: List of IngestDoc objects with id, text, and optional metadata.
    
    Returns:
        Dict with ingestion results:
            - "result": Dict with "added" (items), "chunks" (created), "fallback" (optional)
    
    Raises:
        HTTPException 400: No documents provided.
        HTTPException 500: Ingestion failure.
    
    Notes:
        - Documents >300 chars are automatically chunked
        - Metadata preserved with each chunk (includes original doc ID)
        - Uses ChromaDB for persistent storage; falls back to JSON
    
    Example:
        POST /ingest
        [
            {
                "id": "doc_001",
                "text": "Fever is elevated body temperature...",
                "meta": {"source": "guide.pdf", "page": 5}
            }
        ]
    """
    if not docs:
        raise HTTPException(status_code=400, detail="No documents provided.")
    
    # Convert Pydantic models to dicts for RAG module
    raw_docs = [
        {"id": d.id, "text": d.text, "meta": d.meta}
        for d in docs
    ]
    
    try:
        result = medical_rag.ingest_documents(raw_docs)
        logger.info(
            f"✅ Ingestion complete: {result['added']} items, "
            f"{result.get('chunks', 0)} chunks created"
        )
        return {"result": result}
    except Exception as e:
        logger.error(f"Document ingestion error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest documents: {str(e)}"
        )


@app.post("/ingest-pdf", tags=["Document Management"])
async def ingest_pdf(
    file: UploadFile = File(...),
    request: Request = None
) -> Dict[str, Any]:
    """
    Ingest a PDF file directly.
    
    Extracts text from PDF, chunks automatically, and ingests into RAG store.
    Useful for bulk medical document ingestion (guidelines, protocols, etc).
    
    Args:
        file: PDF file upload.
        request: FastAPI request (for audit logging).
    
    Returns:
        Dict with ingestion results:
            - "result": Ingestion stats (added, chunks, fallback)
            - "filename": Original filename
    
    Raises:
        HTTPException 400: Non-PDF file or empty PDF.
        HTTPException 500: PDF extraction or ingestion error.
    
    Notes:
        - Only accepts .pdf files (case-insensitive)
        - Requires pdfminer.six for text extraction
        - Large PDFs are chunked automatically (500 chars, 50 char overlap)
        - Document ID derived from filename (without extension)
    
    Example:
        POST /ingest-pdf
        Content-Type: multipart/form-data
        file: medical_guidelines.pdf
    """
    client_ip = request.client.host if request and request.client else "unknown"
    
    # === Validate file type ===
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        logger.warning(f"⚠️  Non-PDF file rejected from {client_ip}: {file.filename}")
        log_audit("ingest_rejected", {
            "ip": client_ip,
            "reason": "non_pdf_file",
            "filename": file.filename
        })
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported. Please upload a .pdf file."
        )
    
    # === Log ingest start ===
    log_audit("ingest_started", {
        "ip": client_ip,
        "filename": file.filename,
        "file_type": "pdf"
    })
    
    tmp_path = None
    try:
        # === Save and extract PDF ===
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        logger.debug(f"📄 Extracting text from: {file.filename}")
        text = extract_text(tmp_path)
        
        if not text.strip():
            log_audit("ingest_failed", {
                "ip": client_ip,
                "reason": "empty_extraction",
                "filename": file.filename
            })
            raise PDFProcessingError(
                f"No text extracted from PDF '{file.filename}'. "
                "Ensure PDF contains readable text (not scanned images)."
            )
        
        # === Create document and ingest ===
        doc_id = os.path.splitext(file.filename)[0]
        doc = {
            "id": doc_id,
            "text": text,
            "meta": {"source": file.filename}
        }
        
        result = medical_rag.ingest_documents([doc], chunk=True)
        
        # === Log success ===
        log_audit("ingest_success", {
            "ip": client_ip,
            "filename": file.filename,
            "items_added": result.get("added", 0),
            "chunks_created": result.get("chunks", 0)
        })
        
        logger.info(
            f"📥 PDF Ingestion Complete: {file.filename} "
            f"({result['added']} items, {result.get('chunks', 0)} chunks)"
        )
        
        return {
            "result": result,
            "filename": file.filename
        }
    
    except PDFProcessingError as e:
        logger.error(f"PDF processing error: {e}")
        log_audit("ingest_error", {
            "ip": client_ip,
            "filename": file.filename,
            "error_type": "pdf_processing",
            "error_message": str(e)
        })
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Unexpected PDF ingest error: {type(e).__name__}: {e}")
        log_audit("ingest_error", {
            "ip": client_ip,
            "filename": file.filename,
            "error_type": type(e).__name__,
            "error_message": str(e)
        })
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(e)}"
        )
    
    finally:
        # === Cleanup ===
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
                logger.debug(f"Cleaned up temp file: {tmp_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file {tmp_path}: {e}")


@app.get("/models", tags=["System"])
async def list_models() -> List[str]:
    """
    List available Gemini models.
    
    Returns:
        List[str]: Model names available in Gemini API (empty if not configured).
    
    Notes:
        - Requires GEMINI_API_KEY to be set
        - Returns empty list if Gemini unavailable
    """
    try:
        models = [m.name for m in genai.list_models()]
        logger.debug(f"Retrieved {len(models)} available Gemini models")
        return models
    except Exception as e:
        logger.error(f"Failed to list Gemini models: {type(e).__name__}: {e}")
        return []


@app.get("/health", tags=["System"])
async def health() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Dict: {"status": "ok"} if service is running.
    
    Notes:
        - No dependencies checked (always returns 200 OK if API running)
        - Used for load balancer health checks
        - Use /chat endpoint to test full functionality
    """
    return {"status": "ok"}


if __name__ == "__main__":
    """
    Application entry point.
    
    Starts FastAPI server with uvicorn.
    
    Configuration:
        - Host: 0.0.0.0 (listen on all interfaces)
        - Port: 8000 (or PORT env var if set)
        - Reload: disabled (to prevent double-process issues)
        - Workers: single process (default uvicorn behavior)
    
    Environment Variables:
        - PORT: Server port (default 8000)
        - GEMINI_API_KEY: Google Gemini API key (optional, enables API calls)
        - OPENAI_API_KEY: OpenAI API key (optional, enables semantic embeddings)
        - CHROMA_PERSIST_DIR: ChromaDB storage directory (default ./chroma_db)
        - CHUNK_SIZE: Document chunk size in characters (default 500)
        - CHUNK_OVERLAP: Chunk overlap size (default 50)
    
    Notes:
        - Disable reload=True to avoid double-process behavior
        - Consider using --workers for production deployment
        - Logs startup messages with model initialization status
    """
    port = int(os.getenv("PORT", "8000"))
    rag_store = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    logger.info(f"🚀 Starting Medical Chat Assistant on 0.0.0.0:{port}")
    logger.info(f"📚 RAG Store: {rag_store}")
    logger.info(f"⚙️  Model: {GEMINI_MODEL_NAME}")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Prevent double-process issues
    )
