from sentence_transformers import SentenceTransformer
from app.core.config import settings

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model

def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    return get_model().encode(texts, normalize_embeddings=True).tolist()

def embed_query(text: str) -> list[float]:
    return get_model().encode([text], normalize_embeddings=True)[0].tolist()
