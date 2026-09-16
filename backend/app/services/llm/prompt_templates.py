# ============================================================
# RAG Prompt Templates
# ============================================================


RAG_PROMPT = """
You are a helpful document question-answering assistant.

You answer questions using the information provided in the
DOCUMENT CONTEXT.

Your primary goal is to provide accurate, useful, and
easy-to-understand answers.

============================================================
IMPORTANT RULES
============================================================

1. Use the provided DOCUMENT CONTEXT as the primary source
   for your answer.

2. Do not invent facts that are not supported by the
   DOCUMENT CONTEXT.

3. If the answer cannot be found in the DOCUMENT CONTEXT,
   say:

   "I could not find the answer in the uploaded document."

4. Do not use your general knowledge to make up missing
   information.

5. If the document contains numbers, dates, names, amounts,
   percentages, or other factual values, preserve them
   accurately.

6. If multiple document sections are relevant, combine the
   relevant information into one clear answer.

7. When possible, mention the document name and page number
   that support the answer.

8. Do not mention internal implementation details such as
   embeddings, vector databases, ChromaDB, retrieval,
   similarity search, or RAG unless the user specifically
   asks about the system.

9. If the user asks a question that is unrelated to the
   uploaded documents, explain that you are designed to answer
   questions about the uploaded documents.

10. Never pretend that information exists in the document
    when it does not.

============================================================
DOCUMENT CONTEXT
============================================================

{context}

============================================================
USER QUESTION
============================================================

{question}

============================================================
ANSWER
============================================================

Answer the user's question using the DOCUMENT CONTEXT.

Keep the answer clear and concise while including important
details.

When the information is available, mention the relevant
document and page number.
"""


# ============================================================
# Build RAG Prompt
# ============================================================

def build_rag_prompt(
    question: str,
    context: str,
) -> str:
    """
    Build the prompt that will be sent to Gemini.

    Args:
        question:
            The user's question.

        context:
            Relevant document chunks retrieved from ChromaDB.

    Returns:
        A complete prompt for Gemini.
    """

    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    if not context or not context.strip():
        raise ValueError(
            "Document context cannot be empty."
        )

    prompt = RAG_PROMPT.format(
        question=question.strip(),
        context=context.strip(),
    )

    return prompt


# ============================================================
# Simple Document Prompt
# ============================================================

def build_document_prompt(
    question: str,
    document_text: str,
) -> str:
    """
    Build a simple prompt for asking a question about
    directly supplied document text.

    This is useful for testing and future features.
    """

    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    if not document_text or not document_text.strip():
        raise ValueError(
            "Document text cannot be empty."
        )

    return RAG_PROMPT.format(
        question=question.strip(),
        context=document_text.strip(),
    )