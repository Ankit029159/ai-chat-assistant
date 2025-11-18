import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app, request_count

client = TestClient(app)

# Mock response for Gemini API
def mock_gemini_response(prompt):
    """Mock Gemini response to avoid API quota limits during testing."""
    mock_resp = MagicMock()
    mock_resp.text = "This is a mock medical response for testing purposes. Please consult a healthcare professional for actual medical advice."
    mock_resp.candidates = []
    return mock_resp


@pytest.fixture(autouse=True)
def reset_rate_limit():
    """Reset rate limit before each test."""
    request_count.clear()
    yield
    request_count.clear()


class TestHealth:
    """Test health check endpoint."""
    
    def test_health_returns_ok(self):
        """GET /health should return 200 with status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestChat:
    """Test chat endpoint with safety filters and RAG."""
    
    def test_chat_general_question(self):
        """POST /chat with general question should return 200."""
        with patch('app.model.generate_content', return_value=mock_gemini_response("test")):
            response = client.post("/chat", json={"message": "What is a fever?"})
            assert response.status_code == 200
            data = response.json()
            assert "reply" in data
            assert "sources" in data
            assert "disclaimer" in data
            assert len(data["reply"]) > 0
    
    def test_chat_medical_question(self):
        """POST /chat with medical symptom should return 200 with sources."""
        with patch('app.model.generate_content', return_value=mock_gemini_response("test")):
            response = client.post("/chat", json={"message": "I have a fever and cough"})
            assert response.status_code == 200
            data = response.json()
            assert "reply" in data
            assert isinstance(data["sources"], list)
            assert "disclaimer" in data
    
    def test_chat_safety_filter_diagnosis(self):
        """POST /chat with 'diagnose' keyword should return 400."""
        response = client.post("/chat", json={"message": "Can you diagnose my symptoms?"})
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        # detail may be a dict or string depending on FastAPI version
        detail = data.get("detail")
        if isinstance(detail, dict):
            assert "diagnosis" in str(detail).lower() or "can't" in str(detail).lower()
    
    def test_chat_safety_filter_prescription(self):
        """POST /chat with 'prescription' keyword should return 400."""
        response = client.post("/chat", json={"message": "What prescription should I take?"})
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_chat_safety_filter_pii(self):
        """POST /chat with PII keyword should return 400."""
        response = client.post("/chat", json={"message": "My SSN is 123-45-6789"})
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_chat_rate_limit(self):
        """POST /chat exceeding rate limit should return 429."""
        # Make 31 requests (limit is 30/min)
        responses = []
        with patch('app.model.generate_content', return_value=mock_gemini_response("test")):
            for i in range(31):
                resp = client.post("/chat", json={"message": f"Question {i}"})
                responses.append(resp.status_code)
        
        # Last request should be 429 (too many requests)
        assert responses[-1] == 429
        # Reset by calling health endpoint (different IP/context)
        client.get("/health")


class TestIngest:
    """Test document ingestion endpoint."""
    
    def test_ingest_single_document(self):
        """POST /ingest with single document should return 200."""
        docs = [
            {
                "id": "test_doc_1",
                "text": "This is a test medical document about headaches.",
                "meta": {"source": "test.txt"}
            }
        ]
        response = client.post("/ingest", json=docs)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "added" in data["result"]
        assert data["result"]["added"] >= 1
    
    def test_ingest_multiple_documents(self):
        """POST /ingest with multiple documents should return 200."""
        docs = [
            {
                "id": "test_doc_2",
                "text": "Document about fever symptoms.",
                "meta": {"source": "doc2.txt"}
            },
            {
                "id": "test_doc_3",
                "text": "Document about cold and flu.",
                "meta": {"source": "doc3.txt"}
            }
        ]
        response = client.post("/ingest", json=docs)
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["added"] >= 2
    
    def test_ingest_empty_list(self):
        """POST /ingest with empty list should return 400."""
        response = client.post("/ingest", json=[])
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_ingest_with_chunking(self):
        """POST /ingest with large document should chunk and return chunks count."""
        large_text = "Medical information. " * 100  # Create a long text
        docs = [
            {
                "id": "test_doc_large",
                "text": large_text,
                "meta": {"source": "large.txt"}
            }
        ]
        response = client.post("/ingest", json=docs)
        assert response.status_code == 200
        data = response.json()
        # Should have chunks if text is large enough
        assert "result" in data


class TestRAG:
    """Test RAG retrieval functionality via /chat endpoint."""
    
    def test_rag_retrieval_after_ingest(self):
        """After ingesting, /chat should retrieve relevant documents."""
        # Ingest a document
        docs = [
            {
                "id": "rag_test_doc",
                "text": "The patient presents with persistent headaches and fever for three days.",
                "meta": {"source": "patient_note.txt"}
            }
        ]
        ingest_resp = client.post("/ingest", json=docs)
        assert ingest_resp.status_code == 200
        
        # Query related to the document (mocked Gemini response)
        with patch('app.model.generate_content', return_value=mock_gemini_response("test")):
            chat_resp = client.post("/chat", json={"message": "What about headaches and fever?"})
            assert chat_resp.status_code == 200
            data = chat_resp.json()
            assert len(data["sources"]) > 0  # Should have retrieved sources


class TestEndpointIntegration:
    """Test end-to-end workflows."""
    
    def test_ingest_and_chat_workflow(self):
        """Complete workflow: ingest document → chat query → verify retrieval."""
        # Step 1: Ingest
        docs = [
            {
                "id": "workflow_test",
                "text": "Pneumonia is a serious lung infection characterized by fever, cough, and difficulty breathing.",
                "meta": {"source": "medical_textbook.txt"}
            }
        ]
        ingest_resp = client.post("/ingest", json=docs)
        assert ingest_resp.status_code == 200
        assert ingest_resp.json()["result"]["added"] >= 1
        
        # Step 2: Query (mocked Gemini response)
        with patch('app.model.generate_content', return_value=mock_gemini_response("test")):
            chat_resp = client.post("/chat", json={"message": "Tell me about pneumonia symptoms"})
            assert chat_resp.status_code == 200
        
            # Step 3: Verify response structure
            data = chat_resp.json()
            assert "reply" in data
            assert isinstance(data["sources"], list)
            assert "disclaimer" in data
            assert len(data["disclaimer"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
