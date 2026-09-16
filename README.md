# 🤖 RAG Bank & Books AI

An AI-powered Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask questions about their content.

The system is designed to support both:

- 📚 General documents / books
- 🏦 Bank statements

The application combines semantic vector search, structured SQL queries, SQLite, ChromaDB, and Google Gemini to provide contextual answers from uploaded documents.

---

# ✨ Features

## 📄 Document Management

- Drag-and-drop PDF upload
- Click-to-upload support
- PDF validation
- Document processing
- Document library
- Upload status
- Document metadata

## 💬 AI Document Q&A

Users can ask natural-language questions about uploaded documents.

Example:

```text
What is this document about?
What are the important dates?
Summarize the important points.

The system retrieves relevant document content before sending the context to Gemini.

🔎 Retrieval-Augmented Generation

The application follows the RAG architecture:

User Question
      |
      v
Question Embedding
      |
      v
ChromaDB Vector Search
      |
      v
Relevant Document Chunks
      |
      v
Prompt Construction
      |
      v
Google Gemini
      |
      v
AI Answer
🏦 Bank Statement Intelligence

Bank statements are designed to support structured transaction analysis.

Example questions:

How much did I spend in June?
What was my largest transaction?
How much did I spend on Amazon?
What was my closing balance?
How much money was credited?

These questions can be processed using structured transaction data stored in SQLite.

📚 Book / PDF Q&A

General PDFs and books use vector-based retrieval.

Example:

Who are the main characters?
What is Chapter 3 about?
Explain the main concept discussed in the document.
🏗️ Architecture
                         React Frontend
                              |
                              |
                    ---------------------
                    |                   |
                    v                   v
              Upload PDF           Ask Question
                    |                   |
                    v                   v
                FastAPI             FastAPI
                    |                   |
                    v                   v
              PDF Parser          Query Router
                    |             /     |      \
                    v            /      |       \
                Chunking       SQL   Vector   Hybrid
                    |            |      |       |
                    v            |      v       |
              Embeddings        |   ChromaDB    |
                    |            |      |       |
                    v            |      |       |
                ChromaDB         |      |       |
                    |            |      |       |
                    |            ---- Retrieval
                    |                    |
                    -----------------------
                             |
                             v
                       Context Builder
                             |
                             v
                       Google Gemini
                             |
                             v
                         AI Answer
                             |
                             v
                       React Frontend
🛠️ Technology Stack
Backend
Python
FastAPI
SQLAlchemy
SQLite
Pydantic
Pydantic Settings
Uvicorn
RAG
ChromaDB
Sentence Transformers
all-MiniLM-L6-v2
PDF extraction
Vector similarity search
LLM
Google Gemini API
google-genai Python SDK
Frontend
React
Vite
JavaScript
CSS
📁 Project Structure
rag-bank-books/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── chat.py
│   │   │       ├── documents.py
│   │   │       └── sessions.py
│   │   │
│   │   ├── core/
│   │   │   └── config.py
│   │   │
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   └── init_db.py
│   │   │
│   │   ├── models/
│   │   │   ├── db_models.py
│   │   │   └── schemas.py
│   │   │
│   │   ├── services/
│   │   │   ├── embeddings/
│   │   │   ├── ingestion/
│   │   │   ├── llm/
│   │   │   ├── rag/
│   │   │   └── vectorstore/
│   │   │
│   │   └── utils/
│   │
│   ├── data/
│   │   ├── uploads/
│   │   ├── vectorstore/
│   │   └── app.db
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   │
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   ├── hooks/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   │
│   ├── public/
│   ├── package.json
│   └── package-lock.json
│
├── .env.example
├── .gitignore
└── README.md
🚀 Getting Started
1. Clone the repository
git clone YOUR_GITHUB_REPOSITORY_URL

Enter the project:

cd rag-bank-books
🐍 Backend Setup

Go to the backend:

cd backend

Create a virtual environment:

python -m venv venv
Windows PowerShell

Instead of activating the virtual environment, you can directly use:

.\venv\Scripts\python.exe

Install dependencies:

.\venv\Scripts\python.exe -m pip install -r requirements.txt
🔐 Configure Gemini API

Create:

backend/.env

Add:

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.8-flash

Never commit the .env file.

🗄️ Initialize Database

From the backend directory:

.\venv\Scripts\python.exe -m app.db.init_db

Expected:

Database initialized.
▶️ Start Backend

Run:

.\venv\Scripts\python.exe -m uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs
⚛️ Frontend Setup

Open another terminal.

Go to:

cd frontend

Install dependencies:

npm install

Start React:

npm run dev

Frontend:

http://localhost:5173
🔄 Application Workflow
Upload
Drag & Drop PDF
       |
       v
React
       |
       v
FastAPI
       |
       v
PDF Parser
       |
       v
Text Extraction
       |
       v
Chunking
       |
       v
Embeddings
       |
       v
ChromaDB
💬 Question Answering
User Question
      |
      v
React
      |
      v
FastAPI
      |
      v
Query Router
      |
      +-------------------+
      |                   |
      v                   v
   Vector Search       SQL Query
      |                   |
      v                   v
   ChromaDB             SQLite
      |                   |
      +---------+---------+
                |
                v
          Retrieved Data
                |
                v
             Gemini
                |
                v
             Answer
🔌 API Endpoints
Health Check
GET /
Document Upload
POST /api/documents/upload

Uploads and processes a PDF document.

Documents
GET /api/documents

Returns uploaded documents.

Chat
POST /api/chat

Example request:

{
  "question": "When was Telangana formed as a separate state?"
}

Example response:

{
  "question": "When was Telangana formed as a separate state?",
  "answer": "Telangana was formed as a separate state on 2 June 2014.",
  "sources": []
}
🧠 RAG Components
Document Loader

Extracts text from uploaded PDF documents.

Chunking

Large documents are divided into smaller pieces called chunks.

Example:

PDF
 |
 +-- Chunk 1
 +-- Chunk 2
 +-- Chunk 3
 +-- Chunk 4
Embeddings

Each chunk is converted into a numerical vector representation.

The project currently uses:

all-MiniLM-L6-v2
Vector Database

ChromaDB stores document embeddings and metadata.

Retrieval

When the user asks a question, the system searches for semantically relevant chunks.

Generation

Retrieved context is provided to Google Gemini to generate the final answer.

🏦 Bank Statement Architecture

Bank statements can contain structured financial transactions.

Example:

Date         Description       Debit      Credit     Balance
------------------------------------------------------------
01-Jun-2026  Salary Credit                 45000     97000
02-Jun-2026  Amazon Purchase    2499                 94501
05-Jun-2026  Electricity Bill   1850                 91971

The system can store transactions in SQLite:

transactions
------------------------
id
document_id
txn_date
description
debit_amount
credit_amount
balance
txn_type
raw_text
page_number

This enables accurate financial aggregation.

🔀 Query Routing

The planned query router determines how to answer a question.

SQL Question
How much did I spend in June?

Route:

Question
   ↓
SQL
   ↓
SUM(debit_amount)
   ↓
Answer
Semantic Question
What does this book explain about machine learning?

Route:

Question
   ↓
Vector Search
   ↓
ChromaDB
   ↓
Gemini
Hybrid Question
What were my biggest expenses and what categories did they belong to?

Route:

Question
   ↓
SQL + Vector Search
   ↓
Combined Context
   ↓
Gemini
🔒 Security

This project handles potentially sensitive documents.

Important rules:

Never commit .env
Never commit Gemini API keys
Never commit bank statements
Never commit uploaded documents
Never commit SQLite databases
Never commit ChromaDB data
Keep API keys on the backend
Never expose Gemini API keys in React
Use environment variables for secrets
⚠️ Sensitive Data Warning

Do not upload real bank statements to a public GitHub repository.

For development and testing, use synthetic/demo bank statements.

🧪 Testing

Backend import test:

.\venv\Scripts\python.exe -c "from app.main import app; print('FastAPI application import OK')"

RAG import test:

.\venv\Scripts\python.exe -c "from app.services.rag.rag_pipeline import answer_question; print('RAG pipeline import OK')"

Database initialization:

.\venv\Scripts\python.exe -m app.db.init_db
📌 Current Status
✅ FastAPI backend
✅ React frontend
✅ Gemini integration
✅ ChromaDB
✅ Sentence Transformer embeddings
✅ PDF upload
✅ PDF text extraction
✅ Document chunking
✅ RAG pipeline
✅ Drag-and-drop UI
✅ Chat interface
✅ Source display
🔄 Bank statement parser
🔄 SQL query engine
🔄 Query router
🔄 Hybrid SQL + RAG
🔄 Authentication
🔄 Docker
🛣️ Future Roadmap
Phase 1
Basic RAG
PDF ingestion
Embeddings
ChromaDB
Gemini
Phase 2
Bank statement parser
Transaction extraction
SQLite financial queries
SQL query engine
Query router
Phase 3
Multi-document conversations
Chat sessions
Conversation history
Better citations
Document filtering
Phase 4
OCR
Better table extraction
Authentication
Role-based access
Error handling
Production logging
Phase 5
Docker
PostgreSQL
Cloud deployment
Monitoring
Production security
👨‍💻 Author

B.Tech Graduate
Python / FastAPI / Data / AI Project

📄 License

This project is intended for learning, development, and demonstration purposes.


---

# 6. Now check your project before Git

Go to your **project root**, not backend:

```powershell
cd "C:\Users\ADMIN\Downloads\rag-bank-books-gemini-starter\rag-bank-books"