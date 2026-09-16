from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest

from app.services.rag.rag_pipeline import answer_question


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


# ============================================================
# Chat Endpoint
# ============================================================

@router.post("")
def chat(
    request: ChatRequest,
):
    """
    Ask a question about uploaded documents.
    """

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:

        result = answer_question(
            question
        )

        return {
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )