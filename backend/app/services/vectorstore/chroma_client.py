import chromadb

from app.core.config import settings


# ============================================================
# ChromaDB Client
# ============================================================

_client = chromadb.PersistentClient(
    path=settings.chroma_path
)


# ============================================================
# ChromaDB Collection
# ============================================================

_collection = _client.get_or_create_collection(
    name="rag_chunks",
    metadata={
        "hnsw:space": "cosine"
    },
)


# ============================================================
# Add Chunks
# ============================================================

def add_chunks(
    ids: list[str],
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
) -> None:
    """
    Add or update document chunks in ChromaDB.

    Args:
        ids:
            Unique ID for every chunk.

        documents:
            Text content of every chunk.

        embeddings:
            Embedding vector for every chunk.

        metadatas:
            Metadata associated with every chunk.
    """

    if not ids:
        return

    if len(ids) != len(documents):
        raise ValueError(
            "ids and documents must have the same length."
        )

    if len(ids) != len(embeddings):
        raise ValueError(
            "ids and embeddings must have the same length."
        )

    if len(ids) != len(metadatas):
        raise ValueError(
            "ids and metadatas must have the same length."
        )

    _collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


# ============================================================
# Search Chunks
# ============================================================

def search_chunks(
    query_embedding: list[float],
    top_k: int = 5,
) -> dict:
    """
    Search ChromaDB using a query embedding.

    Args:
        query_embedding:
            Embedding vector generated from the user's question.

        top_k:
            Number of relevant chunks to retrieve.

    Returns:
        ChromaDB query result.
    """

    if not query_embedding:
        return {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

    if top_k <= 0:
        top_k = 5

    collection_count = _collection.count()

    if collection_count == 0:
        return {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

    # ChromaDB cannot request more results than
    # the number of documents stored in the collection.
    n_results = min(
        top_k,
        collection_count,
    )

    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    return results


# ============================================================
# Backward-Compatible Search Function
# ============================================================

def search(
    query_embedding: list[float],
    top_k: int = 5,
) -> dict:
    """
    Backward-compatible alias for search_chunks().

    This allows older parts of the application to use:

        from chroma_client import search

    while the main implementation remains search_chunks().
    """

    return search_chunks(
        query_embedding=query_embedding,
        top_k=top_k,
    )


# ============================================================
# Get Collection Count
# ============================================================

def get_collection_count() -> int:
    """
    Return the number of vectors stored in ChromaDB.
    """

    return _collection.count()


# ============================================================
# Delete Collection
# ============================================================

def delete_collection() -> None:
    """
    Delete the RAG collection.

    Useful during development if the vector database
    needs to be rebuilt.
    """

    global _collection

    try:
        _client.delete_collection(
            name="rag_chunks"
        )
    except Exception:
        pass

    _collection = _client.get_or_create_collection(
        name="rag_chunks",
        metadata={
            "hnsw:space": "cosine"
        },
    )