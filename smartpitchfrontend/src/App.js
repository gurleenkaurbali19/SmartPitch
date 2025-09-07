import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AuthPage from "./components/auth/authpage";
import Home from "./components/auth/Home";
import UploadPage from "./components/upload/UploadPage";  // Import the new UploadPage component

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AuthPage />} />
        <Route path="/home" element={<Home />} />
        <Route path="/upload" element={<UploadPage />} />  {/* Add upload route */}
      </Routes>
    </Router>
  );
}

export default App;
