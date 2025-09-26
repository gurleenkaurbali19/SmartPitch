import React, { useState } from "react";

export default function UploadPage() {
  // Resume states
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeExtracted, setResumeExtracted] = useState(null);

  // JD states
  const [jdFile, setJdFile] = useState(null);
  const [jdText, setJdText] = useState("");
  
  // Final LLM response state
  const [llmResponse, setLlmResponse] = useState(null);

  // Message and loading flags
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const token = sessionStorage.getItem("access_token");

  // Resume handlers
  const handleResumeFileChange = (e) => {
    setResumeFile(e.target.files[0]);
    setResumeExtracted(null);
    setLlmResponse(null);
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
    setLlmResponse(null);
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
    setLlmResponse(null);
    setMessage("");
  };

  const handleJdTextChange = (e) => {
    setJdText(e.target.value);
    setJdFile(null);
    setLlmResponse(null);
    setMessage("");
  };

  const handleJdSubmit = async (e) => {
    e.preventDefault();
    setLlmResponse(null);
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
        setMessage("JD processed and relevance summary generated!");
        setJdFile(null);
        setJdText("");
        setLlmResponse(data.llm_relevance_summary);  // Use only the LLM response here
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

      {/* LLM Final Response Display */}
      {llmResponse && (
        <div style={{ marginTop: 24, padding: 10, border: "1px solid #ccc", background: "#d0f0d0" }}>
          <h4>Job Relevance Summary from AI</h4>
          <pre style={{ whiteSpace: "pre-wrap", fontSize: 14 }}>{llmResponse}</pre>
        </div>
      )}

      {/* Message Display */}
      {message && <p style={{ marginTop: 10, color: "red" }}>{message}</p>}
    </div>
  );
}
