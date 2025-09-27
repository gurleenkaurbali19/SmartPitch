import React, { useState } from "react";

export default function UploadPage() {
  // Resume states
  const [resumeFile, setResumeFile] = useState(null);

  // JD states
  const [jdFile, setJdFile] = useState(null);
  const [jdText, setJdText] = useState("");
  const [jdSections, setJdSections] = useState(null); // Store JD sections for draft email

  // Final LLM response state
  const [llmResponse, setLlmResponse] = useState(null);

  // Drafted email state
  const [draftedEmail, setDraftedEmail] = useState(null);

  // Message and loading flags
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const token = sessionStorage.getItem("access_token");

  // Resume handlers
  const handleResumeFileChange = (e) => {
    setResumeFile(e.target.files[0]);
    setMessage("");
    setLlmResponse(null);
    setDraftedEmail(null);
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
    setDraftedEmail(null);
    const formData = new FormData();
    formData.append("file", resumeFile);

    try {
      const res = await fetch("http://localhost:8000/upload/resume", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });
      if (res.ok) {
        await res.json(); // Discard resume extracted sections
        setMessage("Resume uploaded successfully!");
        setResumeFile(null);
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
    setMessage("");
    setLlmResponse(null);
    setDraftedEmail(null);
    setJdSections(null);
  };

  const handleJdTextChange = (e) => {
    setJdText(e.target.value);
    setJdFile(null);
    setMessage("");
    setLlmResponse(null);
    setDraftedEmail(null);
    setJdSections(null);
  };

  const handleJdSubmit = async (e) => {
    e.preventDefault();
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
    setLlmResponse(null);
    setDraftedEmail(null);

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
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        setMessage("JD uploaded and relevance summary generated!");
        setJdFile(null);
        setJdText("");
        setJdSections(data.jd_sections);
        setLlmResponse(data.llm_relevance_summary);
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

  // Draft Email handler
  const handleDraftEmailClick = async () => {
  if (!jdSections || !llmResponse) {
    setMessage("Please upload JD and generate relevance summary first.");
    return;
  }
  setLoading(true);
  setMessage("");
  setDraftedEmail(null);

  try {
    const res = await fetch("http://localhost:8000/upload/draft-email", { // Updated URL here
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        jd_sections: jdSections,
        llm_relevance_summary: llmResponse,
        candidate_name: "Candidate Name", // Adapt as needed or pass dynamically
      }),
    });
    if (res.ok) {
      const data = await res.json();
      setDraftedEmail(data.email_draft);
      setMessage("Draft email generated successfully.");
    } else {
      const errData = await res.json();
      setMessage(errData.detail || "Failed to generate draft email.");
    }
  } catch (error) {
    setMessage("Error generating draft email. Please try again.");
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

      {/* Confirmation Message */}
      {message && <p style={{ marginTop: 10, color: "green" }}>{message}</p>}

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

          {/* Draft Email Button */}
          <button onClick={handleDraftEmailClick} disabled={loading} style={{ marginTop: 16 }}>
            {loading ? "Generating Draft..." : "Draft Email"}
          </button>
        </div>
      )}

      {/* Drafted Email Display */}
      {draftedEmail && (
        <div style={{ marginTop: 24, padding: 10, border: "1px solid #ccc", background: "#f0f0f0" }}>
          <h4>Drafted Email</h4>
          <pre style={{ whiteSpace: "pre-wrap", fontSize: 14 }}>{draftedEmail}</pre>
        </div>
      )}
    </div>
  );
}
