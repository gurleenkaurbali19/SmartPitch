import React, { useState, useEffect } from "react";

export default function UploadPage() {
  // Resume states
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeExtracted, setResumeExtracted] = useState(null);

  // JD states
  const [jdFile, setJdFile] = useState(null);
  const [jdText, setJdText] = useState("");
  const [jdJsonFiles, setJdJsonFiles] = useState(null);
  const [jsonContents, setJsonContents] = useState({}); // To store each JSON file's content
  const [jdEmbeddingFiles, setJdEmbeddingFiles] = useState(null); // New: Section-wise embedding file paths
  const [relevanceResults, setRelevanceResults] = useState(null); // New: show relevance_search output

  // Message and loading flags
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const token = sessionStorage.getItem("access_token");

  // Resume handlers
  const handleResumeFileChange = (e) => {
    setResumeFile(e.target.files[0]);
    setResumeExtracted(null);
    setMessage("");
  };

  const handleResumeSubmit = async (e) => {
    e.preventDefault();
    if (!resumeFile) {
      setMessage("Please select a PDF file to upload.");
      return;
    }
    if (resumeFile.type !== "application/pdf") {
      setMessage("Only PDF files are allowed for resumes.");
      return;
    }
    setLoading(true);
    setMessage("");
    const formData = new FormData();
    formData.append("file", resumeFile);

    try {
      const res = await fetch("http://localhost:8000/upload/resume", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        setMessage("Resume uploaded and text extracted!");
        setResumeFile(null);
        setResumeExtracted(data.extracted_sections);
      } else {
        const errData = await res.json();
        setMessage(errData.detail || "Resume upload failed.");
      }
    } catch (error) {
      setMessage("Resume upload error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // JD handlers
  const handleJdFileChange = (e) => {
    setJdFile(e.target.files[0]);
    setJdText("");
    setJdJsonFiles(null);
    setJsonContents({});
    setJdEmbeddingFiles(null);
    setRelevanceResults(null);
    setMessage("");
  };

  const handleJdTextChange = (e) => {
    setJdText(e.target.value);
    setJdFile(null);
    setJdJsonFiles(null);
    setJsonContents({});
    setJdEmbeddingFiles(null);
    setRelevanceResults(null);
    setMessage("");
  };

  const handleJdSubmit = async (e) => {
    e.preventDefault();
    setJdJsonFiles(null);
    setJsonContents({});
    setJdEmbeddingFiles(null);
    setRelevanceResults(null);
    if (!jdText && !jdFile) {
      setMessage("Please paste JD text or select a JD PDF file to upload.");
      return;
    }
    if (jdFile && jdFile.type !== "application/pdf") {
      setMessage("Only PDF files are allowed for JD.");
      return;
    }
    setLoading(true);
    setMessage("");
    const formData = new FormData();
    if (jdFile) {
      formData.append("file", jdFile);
    } else {
      formData.append("jd_text", jdText);
    }
    try {
      const res = await fetch("http://localhost:8000/upload/jd", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        setMessage("JD processed and JSON, Embedding & Relevance data created!");
        setJdFile(null);
        setJdText("");
        setJdJsonFiles(data.jd_json_files);
        setJdEmbeddingFiles(data.jd_embedding_files);
        setRelevanceResults(data.relevance_results);
      } else {
        const errData = await res.json();
        setMessage(errData.detail || "JD upload failed.");
      }
    } catch (error) {
      setMessage("JD upload error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Fetch content for each JD JSON file section
  useEffect(() => {
    const fetchJsonContents = async () => {
      if (!jdJsonFiles) return;
      const contents = {};
      for (const section of Object.keys(jdJsonFiles)) {
        try {
          const res = await fetch(
            `http://localhost:8000/upload/jd/json-content?section=${encodeURIComponent(section)}`,
            { headers: { Authorization: `Bearer ${token}` }}
          );
          if (res.ok) {
            const json = await res.json();
            contents[section] = json;
          } else {
            contents[section] = "Failed to load content";
          }
        } catch {
          contents[section] = "Error loading content";
        }
      }
      setJsonContents(contents);
    };

    fetchJsonContents();
  }, [jdJsonFiles, token]);

  return (
    <div style={{ maxWidth: 700, margin: "auto", padding: 20 }}>
      {/* Resume Upload */}
      <h2>Upload Resume</h2>
      <form onSubmit={handleResumeSubmit}>
        <input type="file" accept="application/pdf" onChange={handleResumeFileChange} />
        <br />
        <button type="submit" disabled={loading}>
          {loading ? "Uploading..." : "Upload Resume"}
        </button>
      </form>
      {resumeExtracted && (
        <div style={{ marginTop: 24, padding: 10, border: "1px solid #ccc", background: "#f8f8f8" }}>
          <h4>Extracted Resume Sections</h4>
          <pre style={{ fontSize: 13, whiteSpace: "pre-wrap" }}>
            {JSON.stringify(resumeExtracted, null, 2)}
          </pre>
        </div>
      )}

      <hr style={{ margin: "40px 0" }} />

      {/* Job Description Upload */}
      <h2>Upload or Paste Job Description</h2>
      <form onSubmit={handleJdSubmit} style={{ display: "flex", gap: 16 }}>
        <textarea
          placeholder="Paste Job Description text here..."
          value={jdText}
          onChange={handleJdTextChange}
          rows={10}
          style={{ flex: 1, resize: "vertical" }}
          disabled={loading}
        />
        <div>
          <input
            type="file"
            accept=".pdf"
            onChange={handleJdFileChange}
            disabled={loading}
            style={{ marginBottom: 8 }}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Processing..." : "Upload JD"}
          </button>
        </div>
      </form>

      {/* JD JSON Files Display */}
      {jdJsonFiles && (
        <div style={{ marginTop: 24, padding: 10, border: "1px solid #ccc", background: "#f0f0f0" }}>
          <h4>JD JSON File Paths & Contents</h4>
          <ul style={{ fontSize: 13, wordBreak: "break-word" }}>
            {Object.entries(jdJsonFiles).map(([section, path]) => (
              <li key={section} style={{ marginBottom: 20 }}>
                <strong>{section}:</strong> {path}
                <pre
                  style={{
                    marginTop: 8,
                    backgroundColor: "#fff",
                    padding: 10,
                    border: "1px solid #ddd",
                    whiteSpace: "pre-wrap",
                    maxHeight: 200,
                    overflow: "auto",
                  }}
                >
                  {jsonContents[section]
                    ? JSON.stringify(jsonContents[section], null, 2)
                    : "Loading..."}
                </pre>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* JD Embedding Files Display */}
      {jdEmbeddingFiles && (
        <div style={{ marginTop: 24, padding: 10, border: "1px solid #ccc", background: "#e0f7fa" }}>
          <h4>JD Section-Wise Embedding Files</h4>
          <ul style={{ fontSize: 13, wordBreak: "break-word" }}>
            {Object.entries(jdEmbeddingFiles).map(([section, path]) => (
              <li key={section}>
                <strong>{section}:</strong> {path}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Relevance Search Results Display */}
      {relevanceResults && (
        <div style={{ marginTop: 24, padding: 10, border: "1px solid #ccc", background: "#d0f0d0" }}>
          <h4>Relevance Search Results</h4>
          <pre style={{ fontSize: 13, whiteSpace: "pre-wrap" }}>
            {JSON.stringify(relevanceResults, null, 2)}
          </pre>
        </div>
      )}

      {/* Message Display */}
      {message && <p style={{ marginTop: 10, color: "red" }}>{message}</p>}
    </div>
  );
}
