import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");

  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);

  const [answer, setAnswer] = useState("");
  const [evidence, setEvidence] = useState([]);
  const [summary, setSummary] = useState("");

  const [error, setError] = useState("");

  // =========================================================
  // FILE SELECTION
  // =========================================================

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) {
      setFile(null);
      return;
    }

    setFile(selectedFile);

    // Clear previous state
    setError("");
    setUploadMessage("");
    setUploadedFile(null);
    setSummary("");
    setAnswer("");
    setEvidence([]);
  };

  // =========================================================
  // FILE UPLOAD
  // =========================================================

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a document first.");
      return;
    }

    setUploading(true);
    setError("");
    setUploadMessage("");
    setUploadedFile(null);
    setAnswer("");
    setEvidence([]);
    setSummary("");

    const formData = new FormData();

    // IMPORTANT:
    // The backend expects the field name "file".
    formData.append("file", file);

    try {
      console.log("Uploading:", file.name);

      const response = await axios.post(
        `${API_URL}/api/files/upload`,
        formData
      );

      console.log("Upload status:", response.status);
      console.log("Upload response:", response.data);

      const data = response.data || {};

      // Save complete backend response
      setUploadedFile(data);

      setUploadMessage(
        data.message ||
        "Document uploaded and processed successfully."
      );

      // Support summary if backend returns one
      if (data.summary) {
        setSummary(data.summary);
      }

      // Support chunks/results if backend returns them
      if (Array.isArray(data.evidence)) {
        setEvidence(data.evidence);
      }

      if (Array.isArray(data.results)) {
        setEvidence(data.results);
      }

    } catch (err) {
      console.error("================================");
      console.error("UPLOAD ERROR");
      console.error("================================");
      console.error(err);
      console.error("Message:", err.message);
      console.error("Response:", err.response);
      console.error("Response data:", err.response?.data);
      console.error("Status:", err.response?.status);

      let errorMessage = "Document upload failed.";

      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  // =========================================================
  // ASK QUESTION
  // =========================================================

  const askQuestion = async () => {
    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    setAsking(true);
    setError("");
    setAnswer("");
    setEvidence([]);

    try {
      console.log("Question:", question);

      const response = await axios.post(
        `${API_URL}/api/ask`,
        {
          question: question.trim(),
        }
      );

      console.log("Question response:", response.data);

      const data = response.data || {};

      // =====================================================
      // IRRELEVANT QUESTION
      // =====================================================

      if (data.relevant === false) {
        setAnswer(
          data.answer ||
          "This question is not related to the uploaded document."
        );

        setEvidence([]);
        return;
      }

      // =====================================================
      // NORMAL ANSWER
      // =====================================================

      setAnswer(
        data.answer ||
        "No answer was returned."
      );

      // Backend may call this "results" or "evidence"
      setEvidence(
        data.results ||
        data.evidence ||
        []
      );

    } catch (err) {
      console.error("================================");
      console.error("QUESTION ERROR");
      console.error("================================");
      console.error(err);
      console.error("Response:", err.response);
      console.error("Response data:", err.response?.data);

      let errorMessage = "Could not get an answer.";

      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);

    } finally {
      setAsking(false);
    }
  };

  // =========================================================
  // ENTER KEY
  // =========================================================

  const handleQuestionKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  // =========================================================
  // CLEAR ERROR
  // =========================================================

  const clearError = () => {
    setError("");
  };

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="app">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="header">
        <div>
          <h1>📄 Document Intelligence</h1>

          <p>
            Upload a document and ask questions
            using AI-powered document retrieval.
          </p>
        </div>
      </header>


      <main className="container">

        {/* ===================================================
            UPLOAD SECTION
        =================================================== */}

        <section className="card">

          <h2>📤 Upload Document</h2>

          <p className="description">
            Upload PDF, DOCX, TXT, CSV, Excel,
            PowerPoint or image files.
          </p>

          <div className="upload-box">

            <input
              type="file"
              accept="
                .pdf,
                .docx,
                .txt,
                .csv,
                .xlsx,
                .pptx,
                .png,
                .jpg,
                .jpeg
              "
              onChange={handleFileChange}
              disabled={uploading}
            />

            {/* Selected file */}

            {file && (
              <p className="selected-file">
                Selected: <strong>{file.name}</strong>
              </p>
            )}

            {/* Upload button */}

            <button
              onClick={handleUpload}
              disabled={!file || uploading}
            >
              {uploading
                ? "Processing..."
                : "Upload Document"}
            </button>

          </div>


          {/* Upload success */}

          {uploadMessage && (
            <div className="success">
              ✅ {uploadMessage}
            </div>
          )}

        </section>


        {/* ===================================================
            UPLOADED DOCUMENT
        =================================================== */}

        {uploadedFile && (
          <section className="card">

            <h2>📁 Uploaded Document</h2>

            <div className="document-info">

              <p>
                <strong>Name:</strong>{" "}
                {uploadedFile.original_filename ||
                  uploadedFile.filename ||
                  uploadedFile.file_name ||
                  file?.name ||
                  "N/A"}
              </p>

              <p>
                <strong>File ID:</strong>{" "}
                {uploadedFile.file_id ||
                  uploadedFile.id ||
                  "N/A"}
              </p>

              {uploadedFile.chunks !== undefined && (
                <p>
                  <strong>Chunks:</strong>{" "}
                  {uploadedFile.chunks}
                </p>
              )}

              {uploadedFile.message && (
                <p>
                  <strong>Status:</strong>{" "}
                  {uploadedFile.message}
                </p>
              )}

            </div>

          </section>
        )}


        {/* ===================================================
            SUMMARY
        =================================================== */}

        <section className="card">

          <h2>📋 Document Summary</h2>

          {summary ? (
            <div className="summary">
              {summary}
            </div>
          ) : (
            <div className="empty">
              Summary will appear here after the
              backend provides it.
            </div>
          )}

        </section>


        {/* ===================================================
            ASK QUESTION
        =================================================== */}

        <section className="card">

          <h2>🔍 Ask a Question</h2>

          <p className="description">
            Ask something related to the uploaded document.
          </p>

          <div className="question-box">

            <input
              type="text"
              value={question}
              placeholder="Example: What is the candidate's name?"
              onChange={(event) => {
                setQuestion(event.target.value);
                clearError();
              }}
              onKeyDown={handleQuestionKeyDown}
              disabled={asking}
            />

            <button
              onClick={askQuestion}
              disabled={asking || !question.trim()}
            >
              {asking
                ? "Searching..."
                : "Ask Question"}
            </button>

          </div>

        </section>


        {/* ===================================================
            ERROR
        =================================================== */}

        {error && (
          <div className="error">
            ❌ {error}
          </div>
        )}


        {/* ===================================================
            ANSWER
        =================================================== */}

        {answer && (
          <section className="card">

            <h2>💡 Answer</h2>

            <div className="answer">
              {answer}
            </div>

          </section>
        )}


        {/* ===================================================
            EVIDENCE
        =================================================== */}

        {evidence.length > 0 && (
          <section className="card">

            <h2>📚 Evidence / Retrieved Chunks</h2>

            {evidence.map((item, index) => (

              <div
                className="evidence"
                key={index}
              >

                <div className="evidence-header">

                  <strong>
                    Evidence {index + 1}
                  </strong>

                  {item.distance !== undefined && (
                    <span>
                      Distance:{" "}
                      {Number(item.distance).toFixed(3)}
                    </span>
                  )}

                </div>


                {item.document && (
                  <p>
                    <strong>Document:</strong>{" "}
                    {item.document}
                  </p>
                )}


                {item.page !== undefined &&
                  item.page !== null && (
                    <p>
                      <strong>Page:</strong>{" "}
                      {item.page}
                    </p>
                  )}


                {item.slide !== undefined &&
                  item.slide !== null && (
                    <p>
                      <strong>Slide:</strong>{" "}
                      {item.slide}
                    </p>
                  )}


                {item.sheet && (
                  <p>
                    <strong>Sheet:</strong>{" "}
                    {item.sheet}
                  </p>
                )}


                {item.section && (
                  <p>
                    <strong>Section:</strong>{" "}
                    {item.section}
                  </p>
                )}


                {item.text && (
                  <div className="evidence-text">
                    {item.text}
                  </div>
                )}

              </div>

            ))}

          </section>
        )}

      </main>


      {/* =====================================================
          FOOTER
      ===================================================== */}

      <footer>
        Document Intelligence System
      </footer>

    </div>
  );
}

export default App;