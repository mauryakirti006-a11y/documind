import React, { useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);

  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const [summary, setSummary] = useState("");

  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);

  const [answer, setAnswer] = useState("");
  const [results, setResults] = useState([]);

  const [error, setError] = useState("");

  // ========================================================
  // FILE SELECT
  // ========================================================

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (!file) {
      return;
    }

    setSelectedFile(file);
    setUploadMessage("");
    setUploadSuccess(false);
    setSummary("");
    setAnswer("");
    setResults([]);
    setError("");
  };

  // ========================================================
  // UPLOAD
  // ========================================================

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a document first.");
      return;
    }

    const formData = new FormData();

    formData.append(
      "file",
      selectedFile
    );

    setUploading(true);
    setUploadMessage("");
    setUploadSuccess(false);
    setSummary("");
    setAnswer("");
    setResults([]);
    setError("");

    try {
      const response = await axios.post(
        `${API_URL}/api/files/upload`,
        formData
      );

      setUploadSuccess(true);

      setUploadMessage(
        `${selectedFile.name} uploaded successfully.`
      );

      setSummary(
        response.data.summary || ""
      );

      console.log(
        "Upload response:",
        response.data
      );
    } catch (err) {
      console.error(
        "Upload error:",
        err
      );

      setUploadSuccess(false);

      if (err.response) {
        setError(
          err.response.data?.detail ||
          `Upload failed. Status: ${err.response.status}`
        );
      } else {
        setError(
          "Cannot connect to backend. Make sure FastAPI is running on port 8000."
        );
      }
    } finally {
      setUploading(false);
    }
  };

  // ========================================================
  // ASK QUESTION
  // ========================================================

  const askQuestion = async () => {
    if (!question.trim()) {
      setError(
        "Please enter a question."
      );
      return;
    }

    setAsking(true);
    setAnswer("");
    setResults([]);
    setError("");

    try {
      const response = await axios.post(
        `${API_URL}/api/ask`,
        {
          question:
            question.trim()
        }
      );

      console.log(
        "Question response:",
        response.data
      );

      setAnswer(
        response.data.answer || ""
      );

      setResults(
        response.data.results || []
      );
    } catch (err) {
      console.error(
        "Question error:",
        err
      );

      if (err.response) {
        setError(
          err.response.data?.detail ||
          `Question failed. Status: ${err.response.status}`
        );
      } else {
        setError(
          "Cannot connect to backend. Make sure FastAPI is running."
        );
      }
    } finally {
      setAsking(false);
    }
  };

  // ========================================================
  // ENTER
  // ========================================================

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      askQuestion();
    }
  };

  // ========================================================
  // LOCATION
  // ========================================================

  const getSourceLocation = (result) => {
    const locations = [];

    if (result.page !== null && result.page !== undefined) {
      locations.push(
        `Page ${result.page}`
      );
    }

    if (result.sheet) {
      locations.push(
        `Sheet: ${result.sheet}`
      );
    }

    if (result.row !== null && result.row !== undefined) {
      locations.push(
        `Row ${result.row}`
      );
    }

    if (result.slide !== null && result.slide !== undefined) {
      locations.push(
        `Slide ${result.slide}`
      );
    }

    return locations.length > 0
      ? locations.join(" • ")
      : "Location not available";
  };

  return (
    <div className="app">

      {/* ================================================== */}
      {/* NAVBAR */}
      {/* ================================================== */}

      <nav className="navbar">

        <div className="brand">
          <div className="brand-icon">
            D
          </div>

          <div>
            <div className="brand-name">
              DocuMind
            </div>

            <div className="brand-subtitle">
              Intelligent Document Assistant
            </div>
          </div>
        </div>

        <div className="status-pill">
          <span className="status-dot"></span>
          AI Ready
        </div>

      </nav>

      {/* ================================================== */}
      {/* HERO */}
      {/* ================================================== */}

      <main className="main">

        <section className="hero">

          <div className="hero-badge">
            ✦ DOCUMENT INTELLIGENCE
          </div>

          <h1>
            Ask your documents.
            <br />
            <span>
              Get intelligent answers.
            </span>
          </h1>

          <p>
            Upload your documents and ask questions
            using AI-powered semantic search and
            document-grounded answers.
          </p>

        </section>

        {/* ================================================== */}
        {/* UPLOAD */}
        {/* ================================================== */}

        <section className="card upload-card">

          <div className="section-heading">

            <div className="section-icon">
              ↑
            </div>

            <div>
              <h2>
                Upload Document
              </h2>

              <p>
                PDF, Word, Excel, PowerPoint, CSV,
                TXT or images
              </p>
            </div>

          </div>

          <label className="drop-zone">

            <input
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.docx,.txt,.csv,.xlsx,.pptx,.png,.jpg,.jpeg"
            />

            <div className="upload-symbol">
              ↑
            </div>

            <div className="drop-title">
              {selectedFile
                ? selectedFile.name
                : "Choose a document"}
            </div>

            <div className="drop-text">
              Click here to browse files
            </div>

          </label>

          {selectedFile && (
            <div className="selected-file">
              <span>Selected</span>

              <strong>
                {selectedFile.name}
              </strong>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={
              !selectedFile ||
              uploading
            }
            className="olive-button"
          >
            {uploading
              ? "Processing document..."
              : "Upload & Process"}
          </button>

          {uploadSuccess && (
            <div className="success-box">
              <span>✓</span>

              <div>
                <strong>
                  Upload successful
                </strong>

                <p>
                  Your document is ready for questions.
                </p>
              </div>
            </div>
          )}

        </section>

        {/* ================================================== */}
        {/* SUMMARY */}
        {/* ================================================== */}

        {summary && (
          <section className="card summary-card">

            <div className="section-heading">

              <div className="section-icon summary-icon">
                ✦
              </div>

              <div>
                <h2>
                  Document Summary
                </h2>

                <p>
                  AI-generated overview of your document
                </p>
              </div>

            </div>

            <div className="summary-text">
              {summary}
            </div>

          </section>
        )}

        {/* ================================================== */}
        {/* QUESTION */}
        {/* ================================================== */}

        <section className="card question-card">

          <div className="section-heading">

            <div className="section-icon ask-icon">
              ?
            </div>

            <div>
              <h2>
                Ask a Question
              </h2>

              <p>
                Ask anything about your uploaded document
              </p>
            </div>

          </div>

          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(
                event.target.value
              )
            }
            onKeyDown={handleKeyDown}
            placeholder="Example: What is FinTech?"
            rows="4"
          />

          <div className="question-footer">

            <span className="hint">
              Press Enter to ask
            </span>

            <button
              onClick={askQuestion}
              disabled={
                asking ||
                !question.trim()
              }
              className="brown-button"
            >
              {asking
                ? "Thinking..."
                : "Ask Question →"}
            </button>

          </div>

        </section>

        {/* ================================================== */}
        {/* ERROR */}
        {/* ================================================== */}

        {error && (
          <section className="error-box">

            <span>!</span>

            <div>
              <strong>
                Something went wrong
              </strong>

              <p>
                {error}
              </p>
            </div>

          </section>
        )}

        {/* ================================================== */}
        {/* AI ANSWER */}
        {/* ================================================== */}

        {answer && (
          <section className="card answer-card">

            <div className="answer-header">

              <div className="ai-avatar">
                ✦
              </div>

              <div>
                <h2>
                  AI Answer
                </h2>

                <p>
                  Generated using your uploaded document
                </p>
              </div>

            </div>

            <div className="answer-content">
              {answer}
            </div>

          </section>
        )}

        {/* ================================================== */}
        {/* EVIDENCE */}
        {/* ================================================== */}

        {results.length > 0 && (
          <section className="card evidence-card">

            <div className="evidence-header">

              <div>
                <h2>
                  Evidence
                </h2>

                <p>
                  {results.length} relevant pieces
                  of information retrieved
                </p>
              </div>

              <div className="evidence-count">
                {results.length}
              </div>

            </div>

            <div className="evidence-list">

              {results.map(
                (result, index) => (

                  <div
                    className="evidence-item"
                    key={index}
                  >

                    <div className="evidence-top">

                      <span className="result-number">
                        {String(
                          index + 1
                        ).padStart(
                          2,
                          "0"
                        )}
                      </span>

                      <span className="similarity">
                        Similarity{" "}
                        {Number(
                          result.similarity || 0
                        ).toFixed(2)}
                      </span>

                    </div>

                    <p className="evidence-text">
                      {result.text}
                    </p>

                    <div className="source-info">

                      <span>
                        📄{" "}
                        {result.document ||
                          "Unknown document"}
                      </span>

                      <span>
                        📍{" "}
                        {getSourceLocation(
                          result
                        )}
                      </span>

                    </div>

                  </div>
                )
              )}

            </div>

          </section>
        )}

      </main>

      {/* ================================================== */}
      {/* FOOTER */}
      {/* ================================================== */}

      <footer>
        <span>
          DocuMind
        </span>

        <span>
          Document Intelligence • RAG • Ollama
        </span>
      </footer>

    </div>
  );
}

export default App;