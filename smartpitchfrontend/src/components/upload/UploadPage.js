import React, { useState } from "react";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [extracted, setExtracted] = useState(null);

  // Read token from sessionStorage (set on login)
  const token = sessionStorage.getItem("access_token");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage("");
    setExtracted(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setExtracted(null);
    if (!file) {
      setMessage("Please select a PDF file to upload.");
      return;
    }
    if (file.type !== "application/pdf") {
      setMessage("Only PDF files are allowed.");
      return;
    }

    setLoading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/upload/resume", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        setMessage("Resume uploaded and text extracted!");
        setFile(null);
        setExtracted(data.extracted_sections); // Show extracted dict on the page
      } else {
        const errData = await res.json();
        setMessage(errData.detail || "Upload failed.");
      }
    } catch (error) {
      setMessage("Upload error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "auto", padding: 20 }}>
      <h2>Upload Resume</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" accept="application/pdf" onChange={handleFileChange} />
        <br />
        <button type="submit" disabled={loading}>
          {loading ? "Uploading..." : "Upload"}
        </button>
      </form>
      {message && <p style={{ marginTop: 10 }}>{message}</p>}
      {extracted && (
        <div style={{ marginTop: 24, padding: 10, border: "1px solid #ccc", background: "#f8f8f8" }}>
          <h4>Extracted Resume Sections</h4>
          <pre style={{ fontSize: 13, whiteSpace: "pre-wrap" }}>
            {JSON.stringify(extracted, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
