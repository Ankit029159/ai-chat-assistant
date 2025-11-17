import requests
import time

BASE = "http://127.0.0.1:8000"

def ingest_test_doc():
    docs = [
        {
            "id": "testdoc_rag_001",
            "text": "This is a test medical doc about frobin syndrome. UniqueTestPhrase: frobin-unique-ABC123. It contains clear guidance: patients with frobin may experience subtle fatigue.",
            "meta": {"source": "testdoc_rag_001.pdf"}
        }
    ]
    print("Ingesting test document...")
    r = requests.post(f"{BASE}/ingest", json=docs)
    print("Ingest status:", r.status_code)
    try:
        print(r.json())
    except Exception:
        print(r.text)

def query_test():
    time.sleep(1)
    payload = {"message": "Tell me about frobin-unique-ABC123"}
    print("Querying chat for unique phrase...")
    r = requests.post(f"{BASE}/chat", json=payload)
    print("Chat status:", r.status_code)
    try:
        print(r.json())
    except Exception:
        print(r.text)

if __name__ == '__main__':
    ingest_test_doc()
    query_test()
