from pathlib import Path
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.db_models import Document, Chunk

from app.services.ingestion.pdf_parser import extract_pdf_pages
from app.services.ingestion.chunker import chunk_text
from app.services.embeddings.embedder import embed_texts
from app.services.vectorstore.chroma_client import add_chunks


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a PDF document.

    Processing flow:
    1. Validate PDF
    2. Save PDF to uploads directory
    3. Create document record in SQLite
    4. Extract text page by page
    5. Split text into chunks
    6. Generate embeddings
    7. Store embeddings in ChromaDB
    8. Store chunk metadata in SQLite
    9. Update document status
    """

    # ---------------------------------------------------------
    # 1. Validate file
    # ---------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided.",
        )

    filename = Path(file.filename).name

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # ---------------------------------------------------------
    # 2. Create upload directory
    # ---------------------------------------------------------

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # 3. Create safe file path
    # ---------------------------------------------------------

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    safe_filename = f"{timestamp}_{filename}"

    file_path = upload_dir / safe_filename

    # ---------------------------------------------------------
    # 4. Save uploaded file
    # ---------------------------------------------------------

    try:
        file_content = await file.read()

        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty.",
            )

        file_path.write_bytes(file_content)

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save uploaded file: {exc}",
        )

    # ---------------------------------------------------------
    # 5. Create document record
    # ---------------------------------------------------------

    document = Document(
        filename=filename,
        doc_type="general",
        upload_date=datetime.now(timezone.utc),
        status="processing",
        num_chunks=0,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    try:

        # -----------------------------------------------------
        # 6. Extract PDF text
        # -----------------------------------------------------

        pages = extract_pdf_pages(str(file_path))

        if not pages:
            document.status = "failed"

            db.commit()

            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the PDF.",
            )

        # -----------------------------------------------------
        # 7. Create chunks
        # -----------------------------------------------------

        all_chunks = []

        for page in pages:

            page_number = page.get("page_number", 1)

            page_text = page.get("text", "")

            if not page_text:
                continue

            chunks = chunk_text(page_text)

            for chunk_index, chunk in enumerate(chunks):

                if not chunk.strip():
                    continue

                all_chunks.append(
                    {
                        "text": chunk,
                        "page_number": page_number,
                        "chunk_index": chunk_index,
                    }
                )

        if not all_chunks:
            document.status = "failed"

            db.commit()

            raise HTTPException(
                status_code=400,
                detail="No usable text chunks were created from the PDF.",
            )

        # -----------------------------------------------------
        # 8. Generate embeddings
        # -----------------------------------------------------

        texts = [
            item["text"]
            for item in all_chunks
        ]

        embeddings = embed_texts(texts)

        if len(embeddings) != len(texts):
            document.status = "failed"

            db.commit()

            raise HTTPException(
                status_code=500,
                detail="Number of embeddings does not match number of chunks.",
            )

        # -----------------------------------------------------
        # 9. Prepare ChromaDB metadata
        # -----------------------------------------------------

        chroma_ids = []

        chroma_documents = []

        chroma_embeddings = []

        chroma_metadatas = []

        # -----------------------------------------------------
        # 10. Save chunk metadata to SQLite
        # -----------------------------------------------------

        for index, item in enumerate(all_chunks):

            chunk_text_value = item["text"]

            page_number = item["page_number"]

            chunk_index = item["chunk_index"]

            chunk_record = Chunk(
                document_id=document.id,
                chunk_index=index,
                page_number=page_number,
                text_preview=chunk_text_value[:500],
            )

            db.add(chunk_record)

            chroma_id = (
                f"document_{document.id}_chunk_{index}"
            )

            chroma_ids.append(chroma_id)

            chroma_documents.append(
                chunk_text_value
            )

            chroma_embeddings.append(
                embeddings[index]
            )

            chroma_metadatas.append(
                {
                    "document_id": str(document.id),
                    "filename": filename,
                    "doc_type": document.doc_type,
                    "page": str(page_number),
                    "chunk_index": str(index),
                }
            )

        # -----------------------------------------------------
        # 11. Commit SQLite chunks
        # -----------------------------------------------------

        db.commit()

        # -----------------------------------------------------
        # 12. Store vectors in ChromaDB
        # -----------------------------------------------------

        add_chunks(
            ids=chroma_ids,
            documents=chroma_documents,
            embeddings=chroma_embeddings,
            metadatas=chroma_metadatas,
        )

        # -----------------------------------------------------
        # 13. Update document status
        # -----------------------------------------------------

        document.num_chunks = len(all_chunks)

        document.status = "completed"

        db.commit()

        db.refresh(document)

        # -----------------------------------------------------
        # 14. Return response
        # -----------------------------------------------------

        return {
            "message": "Document uploaded and processed successfully.",
            "document": {
                "id": document.id,
                "filename": document.filename,
                "doc_type": document.doc_type,
                "status": document.status,
                "num_chunks": document.num_chunks,
            },
        }

    except HTTPException:
        raise

    except Exception as exc:

        # -----------------------------------------------------
        # Mark document as failed
        # -----------------------------------------------------

        document.status = "failed"

        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {exc}",
        )


@router.get("/")
def list_documents(
    db: Session = Depends(get_db),
):
    """
    Return all uploaded documents.
    """

    documents = (
        db.query(Document)
        .order_by(Document.id.desc())
        .all()
    )

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "doc_type": document.doc_type,
            "upload_date": (
                document.upload_date.isoformat()
                if document.upload_date
                else None
            ),
            "status": document.status,
            "num_chunks": document.num_chunks,
        }
        for document in documents
    ]


@router.get("/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a single document by ID.
    """

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return {
        "id": document.id,
        "filename": document.filename,
        "doc_type": document.doc_type,
        "upload_date": (
            document.upload_date.isoformat()
            if document.upload_date
            else None
        ),
        "status": document.status,
        "num_chunks": document.num_chunks,
    }