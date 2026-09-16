import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);

  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isThinking, setIsThinking] = useState(false);

  const [uploadStatus, setUploadStatus] = useState("");
  const [error, setError] = useState("");

  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isThinking]);

  async function loadDocuments() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/documents`);

      if (!response.ok) {
        return;
      }

      const data = await response.json();

      if (Array.isArray(data)) {
        setDocuments(data);
      } else if (Array.isArray(data.documents)) {
        setDocuments(data.documents);
      } else {
        setDocuments([]);
      }
    } catch (err) {
      console.error("Could not load documents:", err);
    }
  }

  function validateFile(file) {
    if (!file) {
      return false;
    }

    const isPDF =
      file.type === "application/pdf" ||
      file.name.toLowerCase().endsWith(".pdf");

    if (!isPDF) {
      setError("Only PDF documents are supported right now.");
      return false;
    }

    const maxSize = 25 * 1024 * 1024;

    if (file.size > maxSize) {
      setError("File size must be less than 25 MB.");
      return false;
    }

    setError("");
    return true;
  }

  function handleFileSelect(file) {
    if (!validateFile(file)) {
      return;
    }

    setSelectedFile(file);
    setUploadStatus("");
  }

  function handleInputChange(event) {
    const file = event.target.files?.[0];

    if (file) {
      handleFileSelect(file);
    }
  }

  function handleDragOver(event) {
    event.preventDefault();
    setIsDragging(true);
  }

  function handleDragLeave(event) {
    event.preventDefault();
    setIsDragging(false);
  }

  function handleDrop(event) {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files?.[0];

    if (file) {
      handleFileSelect(file);
    }
  }

  async function uploadDocument() {
    if (!selectedFile) {
      setError("Please select a PDF document first.");
      return;
    }

    setIsUploading(true);
    setError("");
    setUploadStatus("Uploading and processing document...");

    try {
      const formData = new FormData();

      formData.append("file", selectedFile);

      const response = await fetch(
        `${API_BASE_URL}/api/documents/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            data.message ||
            "Document upload failed."
        );
      }

      setUploadStatus(
        `✓ ${selectedFile.name} uploaded successfully`
      );

      setMessages((previous) => [
        ...previous,
        {
          role: "system",
          content: `Document "${selectedFile.name}" is ready. You can now ask questions about your documents.`,
        },
      ]);

      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      await loadDocuments();
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Something went wrong while uploading the document."
      );

      setUploadStatus("");
    } finally {
      setIsUploading(false);
    }
  }

  async function askQuestion() {
    const cleanQuestion = question.trim();

    if (!cleanQuestion || isThinking) {
      return;
    }

    setError("");

    const userMessage = {
      role: "user",
      content: cleanQuestion,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setQuestion("");
    setIsThinking(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: cleanQuestion,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            data.message ||
            "Unable to get an answer."
        );
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            data.answer ||
            "I could not generate an answer.",
          sources: data.sources || [],
        },
      ]);
    } catch (err) {
      console.error(err);

      setMessages((previous) => [
        ...previous,
        {
          role: "error",
          content:
            err.message ||
            "Something went wrong while asking the question.",
        },
      ]);
    } finally {
      setIsThinking(false);
    }
  }

  function handleQuestionKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  }

  function clearChat() {
    setMessages([]);
    setError("");
  }

  function formatFileSize(bytes) {
    if (!bytes) {
      return "";
    }

    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  function getDocumentName(document) {
    return (
      document.filename ||
      document.file_name ||
      document.name ||
      "Document"
    );
  }

  function getDocumentStatus(document) {
    return (
      document.status ||
      document.processing_status ||
      "processed"
    );
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">✦</div>

          <div>
            <h1>RAG AI</h1>
            <span>Document Intelligence</span>
          </div>
        </div>

        <div className="topbar-right">
          <div className="status-pill">
            <span className="status-dot"></span>
            Gemini Connected
          </div>

          <button
            className="clear-button"
            onClick={clearChat}
          >
            Clear Chat
          </button>
        </div>
      </header>

      <main className="workspace">

        {/* LEFT SIDEBAR */}
        <aside className="sidebar">

          <div className="sidebar-header">
            <div>
              <h2>Documents</h2>
              <p>
                Upload documents to your knowledge base
              </p>
            </div>

            <span className="document-count">
              {documents.length}
            </span>
          </div>

          {/* DROP ZONE */}
          <div
            className={`drop-zone ${
              isDragging ? "dragging" : ""
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() =>
              fileInputRef.current?.click()
            }
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleInputChange}
              hidden
            />

            <div className="upload-icon">
              ↑
            </div>

            <h3>
              {isDragging
                ? "Drop your PDF here"
                : "Drag & Drop your PDF"}
            </h3>

            <p>
              or click to browse files
            </p>

            <span className="upload-format">
              PDF • Maximum 25 MB
            </span>
          </div>

          {/* SELECTED FILE */}
          {selectedFile && (
            <div className="selected-file">

              <div className="file-icon">
                PDF
              </div>

              <div className="selected-file-info">
                <strong>
                  {selectedFile.name}
                </strong>

                <span>
                  {formatFileSize(
                    selectedFile.size
                  )}
                </span>
              </div>

              <button
                className="remove-file"
                onClick={() => {
                  setSelectedFile(null);

                  if (fileInputRef.current) {
                    fileInputRef.current.value = "";
                  }
                }}
              >
                ×
              </button>

              <button
                className="upload-button"
                onClick={uploadDocument}
                disabled={isUploading}
              >
                {isUploading
                  ? "Processing..."
                  : "Upload Document"}
              </button>
            </div>
          )}

          {/* UPLOAD STATUS */}
          {uploadStatus && (
            <div className="upload-success">
              {uploadStatus}
            </div>
          )}

          {/* ERROR */}
          {error && (
            <div className="error-box">
              <span>!</span>
              {error}
            </div>
          )}

          {/* DOCUMENT LIST */}
          <div className="document-section">

            <div className="section-title">
              <span>Your Documents</span>
            </div>

            {documents.length === 0 ? (
              <div className="empty-documents">
                <div className="empty-icon">
                  📄
                </div>

                <p>
                  No documents uploaded yet
                </p>

                <span>
                  Upload a PDF to start asking questions.
                </span>
              </div>
            ) : (
              <div className="document-list">

                {documents.map((document, index) => (
                  <div
                    className="document-card"
                    key={
                      document.id ||
                      document.document_id ||
                      index
                    }
                  >
                    <div className="document-icon">
                      PDF
                    </div>

                    <div className="document-details">
                      <strong>
                        {getDocumentName(document)}
                      </strong>

                      <div className="document-meta">
                        <span>
                          {getDocumentStatus(
                            document
                          )}
                        </span>

                        {document.num_chunks && (
                          <span>
                            {document.num_chunks} chunks
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="document-check">
                      ✓
                    </div>
                  </div>
                ))}

              </div>
            )}

          </div>

        </aside>

        {/* CHAT AREA */}
        <section className="chat-area">

          {/* CHAT HEADER */}
          <div className="chat-header">

            <div>
              <div className="chat-title-row">
                <div className="ai-avatar">
                  ✦
                </div>

                <div>
                  <h2>
                    Ask your documents
                  </h2>

                  <p>
                    Ask questions and get answers
                    from your uploaded knowledge base.
                  </p>
                </div>
              </div>
            </div>

            <div className="retrieval-badge">
              <span></span>
              RAG Active
            </div>

          </div>

          {/* CHAT MESSAGES */}
          <div className="messages">

            {messages.length === 0 && (
              <div className="welcome">

                <div className="welcome-icon">
                  ✦
                </div>

                <h2>
                  Welcome to your Document AI
                </h2>

                <p>
                  Upload a document from the left,
                  then ask anything about its contents.
                </p>

                <div className="suggestion-grid">

                  <button
                    onClick={() =>
                      setQuestion(
                        "What is this document about?"
                      )
                    }
                  >
                    <span>💡</span>
                    What is this document about?
                  </button>

                  <button
                    onClick={() =>
                      setQuestion(
                        "Summarize the important points."
                      )
                    }
                  >
                    <span>📝</span>
                    Summarize the important points
                  </button>

                  <button
                    onClick={() =>
                      setQuestion(
                        "What are the key dates mentioned?"
                      )
                    }
                  >
                    <span>📅</span>
                    What are the key dates?
                  </button>

                  <button
                    onClick={() =>
                      setQuestion(
                        "What are the important numbers in this document?"
                      )
                    }
                  >
                    <span>🔢</span>
                    Find important numbers
                  </button>

                </div>

              </div>
            )}

            {messages.map((message, index) => {

              if (message.role === "system") {
                return (
                  <div
                    className="system-message"
                    key={index}
                  >
                    ✓ {message.content}
                  </div>
                );
              }

              if (message.role === "error") {
                return (
                  <div
                    className="chat-message error-message"
                    key={index}
                  >
                    <div className="message-avatar error-avatar">
                      !
                    </div>

                    <div className="message-content">
                      <div className="message-name">
                        Error
                      </div>

                      <div className="message-bubble">
                        {message.content}
                      </div>
                    </div>
                  </div>
                );
              }

              return (
                <div
                  className={`chat-message ${message.role}`}
                  key={index}
                >

                  <div
                    className={`message-avatar ${
                      message.role === "user"
                        ? "user-avatar"
                        : "ai-avatar"
                    }`}
                  >
                    {message.role === "user"
                      ? "You"
                      : "✦"}
                  </div>

                  <div className="message-content">

                    <div className="message-name">
                      {message.role === "user"
                        ? "You"
                        : "RAG AI"}
                    </div>

                    <div className="message-bubble">
                      {message.content}
                    </div>

                    {/* SOURCES */}
                    {message.sources &&
                      message.sources.length > 0 && (
                        <div className="sources">

                          <div className="sources-title">
                            Sources
                          </div>

                          {message.sources.map(
                            (source, sourceIndex) => (
                              <div
                                className="source-card"
                                key={sourceIndex}
                              >
                                <span className="source-number">
                                  {sourceIndex + 1}
                                </span>

                                <div>
                                  <strong>
                                    {source.filename ||
                                      "Document"}
                                  </strong>

                                  {source.page && (
                                    <span>
                                      Page{" "}
                                      {source.page}
                                    </span>
                                  )}
                                </div>
                              </div>
                            )
                          )}

                        </div>
                      )}

                  </div>

                </div>
              );
            })}

            {/* THINKING */}
            {isThinking && (
              <div className="chat-message assistant">

                <div className="message-avatar ai-avatar">
                  ✦
                </div>

                <div className="message-content">

                  <div className="message-name">
                    RAG AI
                  </div>

                  <div className="message-bubble thinking">
                    <span></span>
                    <span></span>
                    <span></span>
                    <label>
                      Searching your documents...
                    </label>
                  </div>

                </div>

              </div>
            )}

            <div ref={chatEndRef} />

          </div>

          {/* QUESTION INPUT */}
          <div className="input-area">

            <div className="input-wrapper">

              <textarea
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                onKeyDown={handleQuestionKeyDown}
                placeholder="Ask anything about your uploaded documents..."
                rows={1}
                disabled={isThinking}
              />

              <button
                className="send-button"
                onClick={askQuestion}
                disabled={
                  !question.trim() ||
                  isThinking
                }
              >
                ➤
              </button>

            </div>

            <div className="input-footer">
              <span>
                Press Enter to send • Shift + Enter
                for a new line
              </span>

              <span>
                Powered by Gemini + ChromaDB
              </span>
            </div>

          </div>

        </section>

      </main>
    </div>
  );
}

export default App;