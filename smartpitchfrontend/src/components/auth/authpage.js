import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const CLOUD_IMAGE_URL = "/auth_background.jpg";

export default function AuthPage() {
  const navigate = useNavigate();
  const [isLoginTab, setIsLoginTab] = useState(false);
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [otpVerified, setOtpVerified] = useState(false);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  // Update window width for responsiveness
  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Responsive font sizes with fallback for very small
  const headingFontSize = windowWidth < 400 ? "24px" : "clamp(24px, 5vw, 40px)";
  const subheadingFontSize = windowWidth < 400 ? "14px" : "clamp(14px, 2.5vw, 18px)";

  const styles = {
    bg: {
      minHeight: "100vh",
      width: "100vw",
      backgroundImage: `url(${CLOUD_IMAGE_URL})`,
      backgroundRepeat: "no-repeat",
      backgroundPosition: "center top",
      backgroundSize: "cover",
      position: "fixed",
      top: 0,
      left: 0,
      zIndex: -1,
      overflowX: "hidden",
    },
    container: {
      maxWidth: 360,
      minHeight: "100vh",
      margin: "0 auto",
      padding: "40px 20px 40px",
      backgroundColor: "rgba(224, 247, 250, 0.9)",
      border: "2px solid #adceeb",
      borderRadius: 18,
      boxShadow: "2px 4px 0 0 #addfe8",
      fontFamily: "'Share Tech Mono', monospace",
      position: "relative",
      zIndex: 10,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      boxSizing: "border-box",
      overflowY: "auto",
    },
    bar: {
      background: "#c6e2f9",
      borderBottom: "2px solid #adceeb",
      borderRadius: "16px 16px 0 0",
      fontSize: "1.15rem",
      padding: "12px 14px",
      display: "flex",
      justifyContent: "center",
      letterSpacing: "1px",
      width: "100%",
      boxSizing: "border-box",
      marginBottom: 20,
    },
    heading: {
      fontWeight: "bold",
      textAlign: "center",
      paddingTop: 20,
      paddingBottom: 12,
      color: "#25626c",
      textShadow: "1px 1px 0 #b7e6e3",
      fontSize: headingFontSize,
      width: "100%",
    },
    subheading: {
      fontSize: subheadingFontSize,
      color: "#4a7c79",
      fontWeight: "normal",
      marginTop: 4,
      width: "100%",
      textAlign: "center",
      lineHeight: 1.2,
    },
    field: {
      margin: "20px 0 0 0",
      width: "100%",
    },
    label: {
      fontSize: "1.07em",
      marginBottom: 8,
      color: "#546e7a",
      display: "block",
    },
    input: {
      width: "100%",
      padding: "10px 9px",
      fontSize: "1em",
      borderRadius: 7,
      border: "1.5px solid #adceeb",
      outline: "none",
      background: "#f5fcff",
      fontFamily: "'Share Tech Mono', monospace",
      boxSizing: "border-box",
    },
    button: {
      background: "#b7e6e3",
      border: "2px solid #56b1ac",
      borderRadius: 10,
      fontFamily: "'Share Tech Mono', monospace",
      color: "#25626c",
      padding: "11px 0",
      marginTop: 25,
      width: "100%",
      fontSize: "1.10em",
      cursor: "pointer",
      boxShadow: "1px 2.5px #b9e3ea",
      transition: "background 0.15s",
    },
    buttonGreen: {
      background: "#e4fcf9",
      border: "2px solid #56b1ac",
      borderRadius: 10,
      color: "#25626c",
      padding: "11px 0",
      marginTop: 15,
      width: "100%",
      fontSize: "1.10em",
      cursor: "pointer",
      boxShadow: "1px 2.5px #b9e3ea",
    },
    message: {
      margin: "18px 0 0 0",
      textAlign: "center",
      fontSize: "1em",
      color: "#c7807b",
      wordWrap: "break-word",
    },
  };

  // Handler functions (sendOtp, verifyOtp, createAccount, handleLogin) same as before...

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
        setMessage(
          errorData.detail === "User already exists"
            ? "User already exists. Please login."
            : "Failed to send OTP."
        );
      } catch {
        setMessage("Failed to send OTP.");
      }
    }
  };

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
      setIsLoginTab(true);
    } else {
      setMessage("Failed to create account.");
    }
  };

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
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData.toString(),
    });
    if (res.ok) {
      const data = await res.json();
      sessionStorage.setItem("access_token", data.access_token);
      setMessage("Login successful! Redirecting...");
      setTimeout(() => navigate("/home"), 1000);
    } else {
      setMessage("Incorrect username or password.");
    }
  };

  return (
    <div>
      <div style={styles.bg} />
      <div style={styles.container}>
        <div style={styles.heading}>
          SmartPitch
          <div style={styles.subheading}>Your assistant to craft smart pitches</div>
        </div>
        <div style={styles.bar}>{isLoginTab ? "Login" : "Sign Up"}</div>
        <div style={{ marginTop: 25, textAlign: "center" }}>
          <button
            type="button"
            style={styles.button}
            onClick={() => {
              setIsLoginTab(!isLoginTab);
              setMessage("");
              setOtpSent(false);
              setOtpVerified(false);
              setEmail("");
              setOtp("");
              setPassword("");
              setConfirmPassword("");
            }}
          >
            Switch to {isLoginTab ? "Sign Up" : "Login"}
          </button>
        </div>
        <div style={styles.field}>
          <label style={styles.label}>Email</label>
          <input
            type="email"
            style={styles.input}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        {!isLoginTab && (
          <>
            {!otpSent && (
              <button style={styles.button} onClick={sendOtp}>
                Send OTP
              </button>
            )}
            {otpSent && !otpVerified && (
              <>
                <div style={styles.field}>
                  <label style={styles.label}>OTP</label>
                  <input
                    type="text"
                    style={styles.input}
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                  />
                </div>
                <button style={styles.buttonGreen} onClick={verifyOtp}>
                  Verify OTP
                </button>
              </>
            )}
            {otpVerified && (
              <>
                <div style={styles.field}>
                  <label style={styles.label}>Password</label>
                  <input
                    type="password"
                    style={styles.input}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
                <div style={styles.field}>
                  <label style={styles.label}>Confirm Password</label>
                  <input
                    type="password"
                    style={styles.input}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                  />
                </div>
                <button style={styles.button} onClick={createAccount}>
                  Create Account
                </button>
              </>
            )}
          </>
        )}
        {isLoginTab && (
          <>
            <div style={styles.field}>
              <label style={styles.label}>Password</label>
              <input
                type="password"
                style={styles.input}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <button style={styles.button} onClick={handleLogin}>
              Login
            </button>
          </>
        )}
        {message && <div style={styles.message}>{message}</div>}
      </div>
    </div>
  );
}
