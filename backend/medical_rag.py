"""
Medical RAG (Retrieval-Augmented Generation) module.

Handles document ingestion, chunking, and semantic retrieval for medical documents.
Supports ChromaDB with fallback to JSON-based storage for local development.

Key Features:
  - Automatic document chunking with configurable sizes
  - ChromaDB integration for semantic search (primary)
  - JSON fallback store for local development (when ChromaDB unavailable)
  - Comprehensive logging and error handling
  - Type hints for all functions
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configure logging
logger = logging.getLogger(__name__)

# Configuration constants
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
MIN_DOC_SIZE: int = 300  # Minimum doc size to trigger chunking
SEMANTIC_CHUNK_SIZE: int = int(os.getenv("SEMANTIC_CHUNK_SIZE", "800"))

# Initialize text splitter for chunking large documents
TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ".", " ", ""]
)

# Semantic text splitter for medical content (larger chunks for better context)
SEMANTIC_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=SEMANTIC_CHUNK_SIZE,
    chunk_overlap=int(SEMANTIC_CHUNK_SIZE * 0.1),  # 10% overlap
    separators=["\n\n", "\n\n## ", "\n## ", "\n", ".", " ", ""]
)


def _get_client() -> Optional[chromadb.Client]:
    """
    Initialize ChromaDB client with graceful fallback.
    
    Returns:
        Optional[chromadb.Client]: ChromaDB Client if successfully initialized,
                                  None if using fallback JSON store.
    
    Notes:
        ChromaDB may fail with deprecated configuration on some systems.
        Falls back to JSON-based storage in such cases.
        Logs warnings on failure but does not raise exceptions.
    """
    try:
        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=CHROMA_PERSIST_DIR
        )
        return chromadb.Client(settings)
    except Exception as e:
        logger.warning(
            f"ChromaDB client initialization failed ({type(e).__name__}): {e}. "
            "Using fallback JSON store for local testing."
        )
        return None


def _get_embeddings() -> OpenAIEmbeddings:
    """
    Get configured OpenAI embeddings instance.
    
    Returns:
        OpenAIEmbeddings: Configured embeddings model.
    
    Raises:
        Exception: If OPENAI_API_KEY not set or OpenAI API error occurs.
    
    Notes:
        Requires OPENAI_API_KEY environment variable to be set.
        Used for semantic similarity searches in ChromaDB.
    """
    return OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))


def get_collection(name: str = "medical") -> Optional[chromadb.Collection]:
    """
    Get or create a ChromaDB collection.
    
    Args:
        name (str): Collection name. Defaults to "medical".
    
    Returns:
        Optional[chromadb.Collection]: ChromaDB collection if available,
                                      None if using fallback mode.
    
    Notes:
        - Returns None when ChromaDB is unavailable (graceful fallback)
        - Collection is created if it doesn't exist
        - Uses OpenAI embeddings for semantic search
    """
    client = _get_client()
    if client is not None:
        try:
            embeddings = _get_embeddings()
            collection = client.get_or_create_collection(
                name=name,
                embedding_function=embeddings.embed_query
            )
            logger.info(f"Successfully loaded ChromaDB collection: {name}")
            return collection
        except Exception as e:
            logger.error(f"Failed to get collection '{name}': {type(e).__name__}: {e}")
            return None
    return None


def _chunk_medical_text(text: str, semantic: bool = True) -> List[str]:
    """
    Chunk text with semantic awareness for medical documents.
    
    Args:
        text (str): Document text to chunk.
        semantic (bool): Use semantic chunking (larger chunks, better context). Default True.
    
    Returns:
        List[str]: List of text chunks.
    
    Notes:
        - Semantic mode: 800 chars, preserves medical context boundaries
        - Regular mode: 500 chars, standard overlap
        - Both preserve paragraph and section boundaries
    """
    if semantic and len(text) > SEMANTIC_CHUNK_SIZE:
        splitter = SEMANTIC_SPLITTER
    else:
        splitter = TEXT_SPLITTER
    
    return splitter.split_text(text)


def ingest_documents(
    docs: List[Dict[str, Any]],
    collection_name: str = "medical",
    chunk: bool = True,
    semantic: bool = True
) -> Dict[str, Any]:
    """
    Ingest documents into RAG store (ChromaDB or fallback JSON).
    
    Args:
        docs (List[Dict[str, Any]]): List of documents to ingest. Each dict should contain:
            - "id" (str, optional): Document identifier. Auto-generated if not provided.
            - "text" (str, required): Document text content.
            - "meta" (Dict, optional): Document metadata (e.g., source, date, author).
        collection_name (str): Name of ChromaDB collection. Defaults to "medical".
        chunk (bool): Whether to split large documents. Defaults to True.
        semantic (bool): Use semantic chunking for better medical context. Defaults to True.
    
    Returns:
        Dict[str, Any]: Ingestion statistics with keys:
            - "added": Number of items added (including chunks)
            - "chunks": Number of chunks created from original docs
            - "fallback": (Optional) True if using JSON fallback store
    
    Raises:
        Exception: If fallback JSON storage fails critically.
    
    Notes:
        - Documents larger than MIN_DOC_SIZE (300 chars) are chunked
        - Chunks include metadata linking back to original document
        - Gracefully falls back to JSON if ChromaDB unavailable
        - All logging includes document counts and storage type
    
    Example:
        docs = [
            {
                "id": "doc_001",
                "text": "Fever is a body temperature above...",
                "meta": {"source": "medical_guide.pdf", "page": 5}
            }
        ]
        result = ingest_documents(docs, semantic=True)
        print(result)  # {"added": 2, "chunks": 1, "fallback": False}
    """
    collection = get_collection(collection_name)
    ids: List[str] = []
    texts: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    # Process each document
    for i, doc in enumerate(docs):
        doc_id: str = doc.get("id", f"doc_{i}")
        doc_text: str = doc.get("text", "")
        doc_meta: Dict[str, Any] = doc.get("meta", {})

        if not doc_text:
            logger.warning(f"Document '{doc_id}' has empty text, skipping")
            continue

        if chunk and len(doc_text) > MIN_DOC_SIZE:
            # Split documents with semantic awareness
            chunks: List[str] = _chunk_medical_text(doc_text, semantic=semantic)
            for j, chunk_text in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{j}"
                chunk_meta = {
                    **doc_meta,
                    "chunk_index": j,
                    "chunk_total": len(chunks),
                    "original_doc_id": doc_id,
                    "chunk_method": "semantic" if semantic else "standard"
                }
                ids.append(chunk_id)
                texts.append(chunk_text)
                metadatas.append(chunk_meta)
            logger.debug(f"Chunked document '{doc_id}' into {len(chunks)} chunks (semantic={semantic})")
        else:
            ids.append(doc_id)
            texts.append(doc_text)
            metadatas.append(doc_meta)

    # Store in ChromaDB if available
    if collection is not None:
        try:
            collection.add(ids=ids, documents=texts, metadatas=metadatas)
            logger.info(
                f"Ingested {len(ids)} items ({len(docs)} docs) "
                f"to ChromaDB collection '{collection_name}'"
            )
            return {"added": len(ids), "chunks": len(ids) - len(docs)}
        except Exception as e:
            logger.error(
                f"Failed to add to ChromaDB ({type(e).__name__}): {e}. "
                "Falling back to JSON storage."
            )

    # Fallback: JSON-backed store for local testing
    return _ingest_to_fallback_store(ids, texts, metadatas, len(docs))


def _ingest_to_fallback_store(
    ids: List[str],
    texts: List[str],
    metadatas: List[Dict[str, Any]],
    original_doc_count: int
) -> Dict[str, Any]:
    """
    Ingest documents to JSON fallback store.
    
    Args:
        ids (List[str]): Document/chunk IDs.
        texts (List[str]): Document/chunk texts.
        metadatas (List[Dict[str, Any]]): Document/chunk metadata.
        original_doc_count (int): Number of original documents (before chunking).
    
    Returns:
        Dict[str, Any]: Ingestion stats including "fallback": True indicator.
    
    Raises:
        Exception: If JSON file operations fail critically.
    
    Notes:
        - Creates chroma_db directory if it doesn't exist
        - Appends to existing fallback store (does not overwrite)
        - Handles corrupted JSON gracefully (starts fresh)
    """
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    fallback_file = os.path.join(CHROMA_PERSIST_DIR, "fallback_store.json")
    
    try:
        existing: List[Dict[str, Any]] = []
        
        # Load existing records
        if os.path.exists(fallback_file):
            with open(fallback_file, "r", encoding="utf-8") as fh:
                try:
                    existing = json.load(fh)
                except json.JSONDecodeError:
                    logger.warning(
                        f"Fallback store JSON corrupted at {fallback_file}, starting fresh"
                    )
                    existing = []
        
        # Add new items to existing records
        for i in range(len(ids)):
            existing.append({
                "id": ids[i],
                "text": texts[i],
                "meta": metadatas[i]
            })
        
        # Write back to file
        with open(fallback_file, "w", encoding="utf-8") as fh:
            json.dump(existing, fh, ensure_ascii=False, indent=2)
        
        logger.info(
            f"Ingested {len(ids)} items ({original_doc_count} docs) "
            f"to JSON fallback store at {fallback_file}"
        )
        return {
            "added": len(ids),
            "chunks": len(ids) - original_doc_count,
            "fallback": True
        }
    except Exception as e:
        logger.error(f"Fallback store ingestion failed ({type(e).__name__}): {e}")
        raise


def retrieve(
    query: str,
    n_results: int = 3,
    collection_name: str = "medical"
) -> Dict[str, Any]:
    """
    Retrieve relevant documents from RAG store.
    
    Args:
        query (str): Search query string.
        n_results (int): Number of results to return. Defaults to 3.
        collection_name (str): Collection name. Defaults to "medical".
    
    Returns:
        Dict[str, Any]: Retrieved documents with key "results" containing list:
            - "id" (str): Document/chunk ID
            - "text" (str): Document/chunk text
            - "meta" (Dict): Document/chunk metadata
    
    Notes:
        - Tries ChromaDB first for semantic search
        - Falls back to JSON store with simple relevancy scoring
        - Returns empty results if no matches found
        - Logs query attempts for audit trail
    
    Example:
        result = retrieve("fever symptoms")
        for doc in result["results"]:
            print(f"Source: {doc['meta'].get('source')}")
            print(f"Content: {doc['text'][:100]}...")
    """
    collection = get_collection(collection_name)
    
    # Try ChromaDB first for semantic search
    if collection is not None:
        try:
            return _retrieve_from_chromadb(collection, query, n_results)
        except Exception as e:
            logger.error(
                f"ChromaDB retrieval failed ({type(e).__name__}): {e}. "
                "Falling back to JSON store."
            )

    # Fallback: JSON-backed store with simple relevancy scoring
    return _retrieve_from_fallback_store(query, n_results)


def _retrieve_from_chromadb(
    collection: chromadb.Collection,
    query: str,
    n_results: int
) -> Dict[str, Any]:
    """
    Retrieve documents from ChromaDB collection using semantic search.
    
    Args:
        collection (chromadb.Collection): ChromaDB collection to search.
        query (str): Search query.
        n_results (int): Number of results to return.
    
    Returns:
        Dict[str, Any]: Dict with "results" key containing retrieved documents.
    
    Notes:
        - Uses semantic similarity for ranking
        - Preserves chunk metadata including chunk indices
        - Handles malformed Chroma responses gracefully
    """
    result = collection.query(query_texts=[query], n_results=n_results)
    docs: List[Dict[str, Any]] = []
    
    # Extract lists from Chroma response structure
    docs_list = result.get("documents", [[]])[0] if result.get("documents") else []
    metas_list = result.get("metadatas", [[]])[0] if result.get("metadatas") else []
    ids_list = result.get("ids", [[]])[0] if result.get("ids") else []
    
    for i in range(len(docs_list)):
        docs.append({
            "id": ids_list[i] if i < len(ids_list) else None,
            "text": docs_list[i] if i < len(docs_list) else "",
            "meta": metas_list[i] if i < len(metas_list) else {}
        })
    
    logger.info(
        f"Retrieved {len(docs)} results from ChromaDB for query: '{query[:50]}'..."
    )
    return {"results": docs}


def _retrieve_from_fallback_store(query: str, n_results: int) -> Dict[str, Any]:
    """
    Retrieve documents from JSON fallback store using simple relevancy scoring.
    
    Args:
        query (str): Search query.
        n_results (int): Number of results to return.
    
    Returns:
        Dict[str, Any]: Dict with "results" key containing matched documents.
    
    Notes:
        - Uses substring matching and word overlap for scoring
        - Faster than ChromaDB but less semantically accurate
        - Falls back gracefully if store doesn't exist or is corrupted
        - Scoring: +1 for each query occurrence, +1 for each matching word
    
    Scoring Algorithm:
        For each stored document:
        1. Count exact substring matches of full query
        2. Count individual word matches
        3. Sort by total score (descending)
        4. Return top N results
    """
    fallback_file = os.path.join(CHROMA_PERSIST_DIR, "fallback_store.json")
    
    if not os.path.exists(fallback_file):
        logger.warning(f"Fallback store file not found at {fallback_file}")
        return {"results": []}
    
    try:
        with open(fallback_file, "r", encoding="utf-8") as fh:
            stored = json.load(fh)
    except json.JSONDecodeError as e:
        logger.error(f"Fallback store JSON corrupted: {e}")
        return {"results": []}

    # Score documents by relevance
    scores: List[tuple] = []
    q = query.lower()
    q_words = set(tok for tok in q.split() if tok)
    
    for item in stored:
        text = (item.get("text") or "").lower()
        
        # Score based on substring matches
        score = text.count(q) * 2  # Weight exact substring matches
        
        # Boost score if any query words appear in text
        text_words = set(text.split())
        matching_words = len(q_words & text_words)
        score += matching_words
        
        if score > 0:
            scores.append((score, item))

    # Sort by relevance (descending) and return top results
    scores.sort(key=lambda x: x[0], reverse=True)
    docs = [item for _, item in scores[:n_results]]
    
    logger.info(
        f"Retrieved {len(docs)} results from fallback store for query: '{query[:50]}'..."
    )
    return {"results": docs}
