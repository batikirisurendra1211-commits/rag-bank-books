from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'app.db'}"
    chroma_path: str = str(BASE_DIR / "data" / "vectorstore")
    upload_dir: str = str(BASE_DIR / "data" / "uploads")
    embedding_model: str = "all-MiniLM-L6-v2"
    top_k: int = 5

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
