from app.core.config import settings

from app.services.embeddings.embedder import embed_query
from app.services.vectorstore.chroma_client import search_chunks
from app.services.llm.gemini_client import generate_text
from app.services.llm.prompt_templates import build_rag_prompt


# ============================================================
# Build Context
# ============================================================

def build_context(
    results: dict,
) -> tuple[str, list[dict]]:
    """
    Convert ChromaDB search results into:

    1. A context string for Gemini.
    2. A list of source references.

    Args:
        results:
            Results returned by ChromaDB.

    Returns:
        Tuple containing:
            context
            sources
    """

    documents = results.get(
        "documents",
        [[]],
    )

    metadatas = results.get(
        "metadatas",
        [[]],
    )

    distances = results.get(
        "distances",
        [[]],
    )

    # --------------------------------------------------------
    # No documents found
    # --------------------------------------------------------

    if not documents:
        return "", []

    if not documents[0]:
        return "", []

    document_list = documents[0]

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata_list = []

    if metadatas and metadatas[0]:
        metadata_list = metadatas[0]

    # --------------------------------------------------------
    # Distances
    # --------------------------------------------------------

    distance_list = []

    if distances and distances[0]:
        distance_list = distances[0]

    # --------------------------------------------------------
    # Context containers
    # --------------------------------------------------------

    context_parts = []

    sources = []

    # --------------------------------------------------------
    # Process retrieved documents
    # --------------------------------------------------------

    for index, document_text in enumerate(
        document_list
    ):

        if not document_text:
            continue

        # ----------------------------------------------------
        # Get metadata
        # ----------------------------------------------------

        if index < len(metadata_list):
            metadata = metadata_list[index] or {}
        else:
            metadata = {}

        # ----------------------------------------------------
        # Get distance
        # ----------------------------------------------------

        if index < len(distance_list):
            distance = distance_list[index]
        else:
            distance = None

        # ----------------------------------------------------
        # Get filename
        # ----------------------------------------------------

        filename = metadata.get(
            "filename",
            "Unknown document",
        )

        # ----------------------------------------------------
        # Get page
        # ----------------------------------------------------

        page = metadata.get(
            "page",
            "Unknown",
        )

        # ----------------------------------------------------
        # Get document ID
        # ----------------------------------------------------

        document_id = metadata.get(
            "document_id",
            None,
        )

        # ----------------------------------------------------
        # Build context block
        # ----------------------------------------------------

        context_block = (
            f"[Source {index + 1}]\n"
            f"Document: {filename}\n"
            f"Page: {page}\n"
            f"Content:\n"
            f"{document_text}"
        )

        context_parts.append(
            context_block
        )

        # ----------------------------------------------------
        # Build source object
        # ----------------------------------------------------

        sources.append(
            {
                "filename": filename,
                "page": str(page),
                "distance": distance,
                "document_id": document_id,
            }
        )

    # --------------------------------------------------------
    # Join context
    # --------------------------------------------------------

    context = "\n\n".join(
        context_parts
    )

    return context, sources


# ============================================================
# Ask Question
# ============================================================

def answer_question(
    question: str,
) -> dict:
    """
    Complete RAG pipeline.

    Flow:

        User Question
             ↓
        Query Embedding
             ↓
        ChromaDB Search
             ↓
        Relevant Chunks
             ↓
        Context Builder
             ↓
        Gemini Prompt
             ↓
        Gemini API
             ↓
        Final Answer
    """

    # --------------------------------------------------------
    # Validate question
    # --------------------------------------------------------

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    question = question.strip()

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    # --------------------------------------------------------
    # Step 1: Create query embedding
    # --------------------------------------------------------

    query_embedding = embed_query(
        question
    )

    # --------------------------------------------------------
    # Step 2: Search ChromaDB
    # --------------------------------------------------------

    results = search_chunks(
        query_embedding=query_embedding,
        top_k=settings.top_k,
    )

    # --------------------------------------------------------
    # Step 3: Build context
    # --------------------------------------------------------

    context, sources = build_context(
        results
    )

    # --------------------------------------------------------
    # No relevant context
    # --------------------------------------------------------

    if not context:

        return {
            "answer": (
                "I could not find any relevant "
                "information in the uploaded documents."
            ),
            "sources": [],
        }

    # --------------------------------------------------------
    # Step 4: Build Gemini prompt
    # --------------------------------------------------------

    prompt = build_rag_prompt(
        question=question,
        context=context,
    )

    # --------------------------------------------------------
    # Step 5: Generate answer with Gemini
    # --------------------------------------------------------

    answer = generate_text(
        prompt
    )

    # --------------------------------------------------------
    # Step 6: Return answer + sources
    # --------------------------------------------------------

    return {
        "answer": answer,
        "sources": sources,
    }