import React, { useState, useEffect } from "react";

const BACKGROUND_IMAGE = "/upload_background.jpg";

const styles = {
  wrapper: {
    height: "100vh",
    width: "100vw",
    backgroundImage: `url(${BACKGROUND_IMAGE})`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
    fontFamily: "'Share Tech Mono', monospace",
    color: "#25626c",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: 24,
    boxSizing: "border-box",
    overflowY: "auto",
    overflowX: "hidden",
  },
  container: {
    width: "100%",
    maxWidth: 760,
    display: "flex",
    flexDirection: "column",
    gap: 32,
  },
  box: {
    backgroundColor: "rgba(224, 247, 250, 0.9)",
    padding: 24,
    borderRadius: 20,
    border: "2px solid #adceeb",
    boxShadow: "4px 6px 0 0 #addfe8",
    boxSizing: "border-box",
  },
  heading: {
    fontSize: "clamp(28px, 5vw, 36px)",
    fontWeight: "bold",
    marginBottom: 16,
    textShadow: "1px 1px 0 #b7e6e3",
    textAlign: "center",
  },
  boxTitle: {
    fontSize: "1.4em",
    fontWeight: "600",
    marginBottom: 14,
    color: "#25626c",
    textShadow: "1px 1px 0 #d0f0d0",
  },
  message: {
    color: "#2b6263",
    fontWeight: "700",
    whiteSpace: "pre-wrap",
    textAlign: "center",
    textShadow: "0 0 6px #c4f4f4",
    marginTop: 16,
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },
  inputFile: {
    padding: "10px 14px",
    borderRadius: 10,
    border: "2px solid #56b1ac",
    fontFamily: "'Share Tech Mono', monospace",
    backgroundColor: "#a6dedf",
    cursor: "pointer",
    color: "#25626c",
  },
  textarea: {
    width: "100%",
    fontFamily: "'Share Tech Mono', monospace",
    fontSize: 16,
    padding: 14,
    borderRadius: 14,
    border: "2px solid #6fc2c2",
    resize: "vertical",
    minHeight: 180,
    color: "#25626c",
    boxSizing: "border-box",
    backgroundColor: "rgba(243, 250, 250, 0.9)",
    boxShadow: "2px 3px 8px rgba(115, 175, 178, 0.25)",
  },
  button: {
    background: "#56b1ac",
    border: "2px solid #3b8b8a",
    color: "#fff",
    fontSize: "1.2em",
    fontWeight: "700",
    padding: "16px 36px",
    borderRadius: 20,
    cursor: "pointer",
    boxShadow: "3px 6px 18px rgba(33, 150, 145, 0.65)",
    fontFamily: "'Share Tech Mono', monospace",
    transition: "background 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease",
    userSelect: "none",
    alignSelf: "flex-start",
  },
  buttonDisabled: {
    background: "#a8d5d7",
    borderColor: "#8ac2c5",
    cursor: "not-allowed",
    boxShadow: "none",
    color: "#dff1f1",
  },
  jdForm: {
    display: "flex",
    gap: 24,
    flexWrap: "wrap",
    alignItems: "flex-start",
  },
  jdTextareaContainer: {
    flex: 1,
    minWidth: 300,
  },
  jdFileContainer: {
    display: "flex",
    flexDirection: "column",
    gap: 16,
    minWidth: 160,
  },
  responseBox: {
    padding: 20,
    fontFamily: "'Share Tech Mono', monospace",
    fontSize: 15,
    whiteSpace: "pre-wrap",
    color: "#1c665f",
    backgroundColor: "rgba(208, 240, 208, 0.9)",
    borderRadius: 16,
    border: "2px solid #6fc2c2",
    boxShadow: "inset 2px 4px 10px #76b1b1",
    marginTop: 10,
    maxHeight: 250,
    overflowY: "auto",
    overflowX: "hidden",
  },
  emailOptionsBox: {
    backgroundColor: "rgba(224, 247, 250, 0.95)",
    borderRadius: 20,
    border: "2px solid #56b1ac",
    boxShadow: "3px 6px 12px #56b1ac88",
    padding: 24,
    marginTop: 16,
    fontFamily: "'Share Tech Mono', monospace",
    color: "#25626c",
    maxWidth: 700,
  },
  emailOptions: {
    display: "flex",
    flexWrap: "wrap",
    gap: 24,
    marginTop: 12,
    fontSize: 14,
  },
  emailOptionLabel: {
    display: "flex",
    alignItems: "center",
    gap: 10,
  },
  emailOptionInput: {
    width: 110,
    padding: 10,
    borderRadius: 12,
    border: "2px solid #56b1ac",
    color: "#25626c",
    backgroundColor: "rgba(235, 255, 255, 0.9)",
  },
  emailOptionSelect: {
    padding: 10,
    borderRadius: 12,
    border: "2px solid #56b1ac",
    color: "#25626c",
    backgroundColor: "rgba(235, 255, 255, 0.9)",
  },
  draftedEmailBox: {
    marginTop: 28,
    padding: 24,
    fontFamily: "'Share Tech Mono', monospace",
    fontSize: 15,
    borderRadius: 20,
    border: "2px solid #56b1ac",
    boxShadow: "0 4px 16px #72bfbecc",
    maxHeight: 350,
    position: "relative",
    backgroundColor: "rgba(210, 245, 245, 0.95)",
  },
  draftTextarea: {
    width: "100%",
    height: "290px",
    resize: "none",
    border: "none",
    fontSize: 15,
    fontFamily: "'Share Tech Mono', monospace",
    lineHeight: 1.5,
    backgroundColor: "transparent",
    color: "#25626c",
    outline: "none",
  },
  copyButton: {
    position: "absolute",
    top: 12,
    right: 12,
    background: "#56b1ac",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    padding: "6px 14px",
    cursor: "pointer",
    fontSize: 14,
    boxShadow: "1px 2px 6px rgba(0,0,0,0.3)",
    userSelect: "none",
  },
};

export default function UploadPage() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jdFile, setJdFile] = useState(null);
  const [jdText, setJdText] = useState("");
  const [jdSections, setJdSections] = useState(null);
  const [llmResponse, setLlmResponse] = useState(null);
  const [draftedEmail, setDraftedEmail] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [emailLength, setEmailLength] = useState(120);
  const [tone, setTone] = useState("Formal");
  const [detailLevel, setDetailLevel] = useState("Summary");
  const [closing, setClosing] = useState("Regards");

  const token = sessionStorage.getItem("access_token");

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
        await res.json();
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

  const handleDraftEmailClick = async () => {
    if (!jdSections || !llmResponse) {
      setMessage("Please upload JD and generate relevance summary first.");
      return;
    }
    setLoading(true);
    setMessage("");
    setDraftedEmail(null);

    try {
      const res = await fetch("http://localhost:8000/upload/draft-email", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          jd_sections: jdSections,
          llm_relevance_summary: llmResponse,
          candidate_name: "Candidate Name",
          email_length: emailLength,
          tone: tone,
          detail_level: detailLevel,
          closing: closing,
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
    <div style={styles.wrapper}>
      <main style={styles.container}>
        <h1 style={styles.heading}>SmartPitch - Upload and Generate</h1>

        {/* Resume Upload Box */}
        <section style={styles.box}>
          <h2 style={styles.boxTitle}>Upload Resume</h2>
          <form onSubmit={handleResumeSubmit} style={styles.form}>
            <input
              type="file"
              accept="application/pdf"
              onChange={handleResumeFileChange}
              style={styles.inputFile}
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading}
              style={{
                ...styles.button,
                ...(loading ? styles.buttonDisabled : {}),
              }}
            >
              {loading ? "Uploading..." : "Upload Resume"}
            </button>
          </form>
          {message && message.includes("Resume") && (
            <p style={styles.message}>{message}</p>
          )}
        </section>

        {/* Job Description Upload Box */}
        <section style={styles.box}>
          <h2 style={styles.boxTitle}>Upload or Paste Job Description</h2>
          <form onSubmit={handleJdSubmit} style={styles.jdForm}>
            <div style={styles.jdTextareaContainer}>
              <textarea
                placeholder="Paste Job Description text here..."
                value={jdText}
                onChange={handleJdTextChange}
                rows={10}
                style={styles.textarea}
                disabled={loading}
              />
            </div>
            <div style={styles.jdFileContainer}>
              <input
                type="file"
                accept=".pdf"
                onChange={handleJdFileChange}
                disabled={loading}
                style={styles.inputFile}
              />
              <button
                type="submit"
                disabled={loading}
                style={{
                  ...styles.button,
                  ...(loading ? styles.buttonDisabled : {}),
                }}
              >
                {loading ? "Processing..." : "Upload JD"}
              </button>
            </div>
          </form>
          {message && message.includes("JD") && (
            <p style={styles.message}>{message}</p>
          )}
        </section>

        {/* LLM Relevance Summary Box */}
        {llmResponse && (
          <section style={styles.box}>
            <h2 style={styles.boxTitle}>Job Relevance Summary from AI</h2>
            <pre style={styles.responseBox}>{llmResponse}</pre>
          </section>
        )}

        {/* Email Drafting Options Box */}
        {llmResponse && (
          <section style={styles.emailOptionsBox}>
            <h2 style={styles.boxTitle}>Email Drafting Options</h2>
            <div style={styles.emailOptions}>
              <label style={styles.emailOptionLabel}>
                Email Length (words):
                <input
                  type="number"
                  value={emailLength}
                  min={50}
                  max={400}
                  step={10}
                  style={styles.emailOptionInput}
                  onChange={(e) => setEmailLength(Number(e.target.value))}
                  disabled={loading}
                />
              </label>

              <label style={styles.emailOptionLabel}>
                Tone:
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  style={styles.emailOptionSelect}
                  disabled={loading}
                >
                  <option>Formal</option>
                  <option>Friendly</option>
                  <option>Confident</option>
                  <option>Polite</option>
                  <option>Direct</option>
                  <option>Casual</option>
                </select>
              </label>

              <label style={styles.emailOptionLabel}>
                Details:
                <select
                  value={detailLevel}
                  onChange={(e) => setDetailLevel(e.target.value)}
                  style={styles.emailOptionSelect}
                  disabled={loading}
                >
                  <option value="Summary">Summary</option>
                  <option value="Detailed">Detailed</option>
                </select>
              </label>

              <label style={styles.emailOptionLabel}>
                Closing:
                <input
                  type="text"
                  value={closing}
                  maxLength={40}
                  style={{ ...styles.emailOptionInput, width: 140 }}
                  onChange={(e) => setClosing(e.target.value)}
                  placeholder="e.g. Regards, Best wishes"
                  disabled={loading}
                />
              </label>
            </div>

            <button
              onClick={handleDraftEmailClick}
              disabled={loading}
              style={{
                ...styles.button,
                ...(loading ? styles.buttonDisabled : {}),
                marginTop: 16,
              }}
            >
              {loading ? "Generating Draft..." : "Draft Email"}
            </button>
          </section>
        )}

        {/* Drafted Email Box with Copy and Edit */}
        {draftedEmail && (
          <section style={styles.draftedEmailBox}>
            <h2 style={styles.boxTitle}>Drafted Email</h2>
            <button
              style={styles.copyButton}
              onClick={() => navigator.clipboard.writeText(draftedEmail)}
              title="Copy email to clipboard"
            >
              Copy
            </button>
            <textarea
              style={styles.draftTextarea}
              value={draftedEmail}
              onChange={(e) => setDraftedEmail(e.target.value)}
            />
          </section>
        )}
      </main>
    </div>
  );
}
