import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

print('GET /health ->', client.get('/health').json())

# Test chat endpoint (uses fallback model if Gemini not configured)
resp = client.post('/chat', json={'message': 'I have a fever and cough'})
print('POST /chat ->', resp.status_code, resp.json())

# Test ingest endpoint and fallback store
doc = {'id': 'testdoc_001', 'text': 'This is a test medical note about headaches and fever.', 'meta': {'source': 'testdoc_001.txt'}}
resp2 = client.post('/ingest', json=[doc])
print('POST /ingest ->', resp2.status_code, resp2.json())

# Test retrieval via medical_rag directly
from medical_rag import retrieve
print('retrieve ->', retrieve('headache'))
