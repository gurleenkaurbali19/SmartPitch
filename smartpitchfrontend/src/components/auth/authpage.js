import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function AuthPage() {
  const navigate = useNavigate();

  // Form states
  const [isLoginTab, setIsLoginTab] = useState(false); // toggle between login/signup
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [otpVerified, setOtpVerified] = useState(false);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");

  // Send OTP
  const sendOtp = async () => {
  if (!email) {
    setMessage("Please enter an email.");
    return;
  }
  const res = await fetch("http://localhost:8000/auth/request-otp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  if (res.ok) {
    setOtpSent(true);
    setMessage("OTP sent! Check your email.");
  } else {
    try {
      const errorData = await res.json();
      if (errorData.detail === "User already exists") {
        setMessage("User already exists. Please login.");
      } else {
        setMessage("Failed to send OTP.");
      }
    } catch {
      setMessage("Failed to send OTP.");
    }
  }
};


  // Create account (set password)
  const createAccount = async () => {
    if (!password || !confirmPassword) {
      setMessage("Please enter and confirm your password.");
      return;
    }
    if (password !== confirmPassword) {
      setMessage("Passwords do not match.");
      return;
    }
    const res = await fetch("http://localhost:8000/auth/set-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password, confirm_password: confirmPassword }),
    });
    if (res.ok) {
      setMessage("Account created successfully! You can now login.");
      setOtpSent(false);
      setOtpVerified(false);
      setEmail("");
      setOtp("");
      setPassword("");
      setConfirmPassword("");
    } else {
      setMessage("Failed to create account.");
    }
  };
  // Verify OTP
const verifyOtp = async () => {
  if (!otp) {
    setMessage("Please enter the OTP.");
    return;
  }
  const res = await fetch("http://localhost:8000/auth/verify-otp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, otp }),
  });
  if (res.ok) {
    setOtpVerified(true);
    setMessage("OTP verified! Please set your password.");
  } else {
    setMessage("Invalid or expired OTP.");
  }
};


  // Handle login
  const handleLogin = async () => {
    setMessage("");
    if (!email || !password) {
      setMessage("Please enter email and password.");
      return;
    }
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);
    formData.append("grant_type", "password");

    const res = await fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: formData.toString(),
    });

    if (res.ok) {
      const data = await res.json();
      sessionStorage.setItem("access_token", data.access_token);
      setMessage("Login successful! Welcome.");
      navigate("/home"); // Navigate to home page (lowercase /home)
    } else {
      setMessage("Incorrect username or password.");
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: "auto" }}>
      <h2>{isLoginTab ? "Login" : "Sign Up"}</h2>
      <button onClick={() => setIsLoginTab(!isLoginTab)}>
        Switch to {isLoginTab ? "Sign Up" : "Login"}
      </button>

      {!isLoginTab && (
        <>
          <div>
            <label>Email:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          {!otpSent && (
            <button onClick={sendOtp}>Send OTP</button>
          )}

          {otpSent && !otpVerified && (
            <>
              <div>
                <label>Enter OTP:</label>
                <input
                  type="text"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                />
              </div>
              <button onClick={verifyOtp}>Verify OTP</button>
            </>
          )}

          {otpVerified && (
            <>
              <div>
                <label>Password:</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <div>
                <label>Confirm Password:</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>
              <button onClick={createAccount}>Create Account</button>
            </>
          )}
        </>
      )}

      {isLoginTab && (
        <>
          <div>
            <label>Email:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label>Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button onClick={handleLogin}>Login</button>
        </>
      )}

      <p>{message}</p>
    </div>
  );
}

