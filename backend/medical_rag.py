import os
from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings
import json
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Simple Chroma-based RAG helper for medical docs
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

# Text splitter for chunking large documents
TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=int(os.getenv("CHUNK_SIZE", 500)),
    chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 50)),
    separators=["\n\n", "\n", ".", " ", ""]
)


def _get_client():
    try:
        settings = Settings(chroma_db_impl="duckdb+parquet", persist_directory=CHROMA_PERSIST_DIR)
        return chromadb.Client(settings)
    except Exception:
        # ChromaDB may be using a deprecated configuration on some installs.
        # Fall back to a lightweight JSON-backed store to allow local testing and indexing.
        return None


def _get_embeddings():
    # Uses OpenAI embeddings; ensure OPENAI_API_KEY env var is set
    return OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))


def get_collection(name: str = "medical"):
    # If chroma client is available, use real collection
    client = _get_client()
    if client is not None:
        embeddings = _get_embeddings()
        collection = client.get_or_create_collection(name=name, embedding_function=embeddings.embed_query)
        return collection

    # Otherwise return None to indicate fallback store should be used
    return None


def ingest_documents(docs: List[Dict[str, Any]], collection_name: str = "medical", chunk: bool = True):
    """Ingest a list of documents into Chroma collection.

    docs: list of dicts: {"id": str, "text": str, "meta": { ... }}
    chunk: if True, split large docs into smaller chunks
    """
    collection = get_collection(collection_name)
    ids = []
    texts = []
    metadatas = []

    for i, doc in enumerate(docs):
        doc_id = doc.get("id", f"doc_{i}")
        doc_text = doc.get("text", "")
        doc_meta = doc.get("meta", {})

        if chunk and len(doc_text) > 300:  # Only chunk if doc is substantial
            chunks = TEXT_SPLITTER.split_text(doc_text)
            for j, chunk_text in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{j}"
                chunk_meta = {**doc_meta, "chunk_index": j, "original_doc_id": doc_id}
                ids.append(chunk_id)
                texts.append(chunk_text)
                metadatas.append(chunk_meta)
        else:
            ids.append(doc_id)
            texts.append(doc_text)
            metadatas.append(doc_meta)

    if collection is not None:
        collection.add(ids=ids, documents=texts, metadatas=metadatas)
        return {"added": len(ids), "chunks": len(ids) - len(docs)}

    # Fallback: simple JSON-backed store for local testing
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    fallback_file = os.path.join(CHROMA_PERSIST_DIR, "fallback_store.json")
    try:
        existing = []
        if os.path.exists(fallback_file):
            with open(fallback_file, "r", encoding="utf-8") as fh:
                try:
                    existing = json.load(fh)
                except Exception:
                    existing = []
        for i in range(len(ids)):
            existing.append({"id": ids[i], "text": texts[i], "meta": metadatas[i]})
        with open(fallback_file, "w", encoding="utf-8") as fh:
            json.dump(existing, fh, ensure_ascii=False, indent=2)
        return {"added": len(ids), "chunks": len(ids) - len(docs), "fallback": True}
    except Exception as e:
        raise


def retrieve(query: str, n_results: int = 3, collection_name: str = "medical") -> Dict[str, Any]:
    collection = get_collection(collection_name)
    docs = []
    # If a real Chroma collection exists, use it
    if collection is not None:
        result = collection.query(query_texts=[query], n_results=n_results)
        docs_list = result.get("documents", [[]])[0] if result.get("documents") else []
        metas_list = result.get("metadatas", [[]])[0] if result.get("metadatas") else []
        ids_list = result.get("ids", [[]])[0] if result.get("ids") else []
        for i in range(len(docs_list)):
            chunk_id = ids_list[i] if i < len(ids_list) else None
            chunk_text = docs_list[i] if i < len(docs_list) else ""
            chunk_meta = metas_list[i] if i < len(metas_list) else {}
            docs.append({"id": chunk_id, "text": chunk_text, "meta": chunk_meta})
        return {"results": docs}

    # Fallback: load JSON-backed store and perform simple substring matching
    fallback_file = os.path.join(CHROMA_PERSIST_DIR, "fallback_store.json")
    if not os.path.exists(fallback_file):
        return {"results": []}
    try:
        with open(fallback_file, "r", encoding="utf-8") as fh:
            stored = json.load(fh)
    except Exception:
        stored = []

    # Simple relevancy: count query term occurrences in text
    scores = []
    q = query.lower()
    for item in stored:
        text = (item.get("text") or "").lower()
        score = text.count(q)
        # also boost if any word overlaps
        for tok in q.split():
            if tok and tok in text:
                score += 1
        if score > 0:
            scores.append((score, item))

    scores.sort(key=lambda x: x[0], reverse=True)
    for s, item in scores[:n_results]:
        docs.append({"id": item.get("id"), "text": item.get("text"), "meta": item.get("meta", {})})
    return {"results": docs}
