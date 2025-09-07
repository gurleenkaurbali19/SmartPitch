import React from "react";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div style={{ padding: 20 }}>
      <h1>Welcome to the Home Page!</h1>
      <p>Hello, you are logged in.</p>
      <button onClick={() => navigate("/upload")}>Upload Resume</button>
    </div>
  );
}
