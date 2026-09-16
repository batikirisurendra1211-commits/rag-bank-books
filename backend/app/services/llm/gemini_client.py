from google import genai

from app.core.config import settings


# ============================================================
# Gemini Client
# ============================================================

_client = None


# ============================================================
# Get Gemini Client
# ============================================================

def get_client():
    """
    Create and return the Gemini API client.

    The client is created only once.
    """

    global _client

    if _client is None:

        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. "
                "Add your Gemini API key to backend/.env."
            )

        _client = genai.Client(
            api_key=settings.gemini_api_key
        )

    return _client


# ============================================================
# Generate Text
# ============================================================

def generate_text(
    prompt: str,
) -> str:
    """
    Send a prompt to Gemini and return the generated text.
    """

    if not prompt or not prompt.strip():
        raise ValueError(
            "Prompt cannot be empty."
        )

    client = get_client()

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
    )

    if not response:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    text = getattr(
        response,
        "text",
        None,
    )

    if not text:
        raise RuntimeError(
            "Gemini response did not contain text."
        )

    return text.strip()