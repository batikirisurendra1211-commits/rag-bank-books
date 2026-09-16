from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import documents
from app.api.routes import chat


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Bank Books RAG API",
    description=(
        "Hybrid RAG system for books and bank statements "
        "using Gemini."
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Routes
# ============================================================

app.include_router(
    documents.router
)

app.include_router(
    chat.router
)


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Bank Books RAG API is running"
    }


# ============================================================
# Health Endpoint
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }