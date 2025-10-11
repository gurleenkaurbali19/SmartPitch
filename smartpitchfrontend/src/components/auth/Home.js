import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const BACKGROUND_IMAGE = "/home_background.jpg";

const styles = {
  wrapper: {
    minHeight: "100vh",
    width: "100vw",
    maxWidth: "100vw",
    overflowY: "auto",
    overflowX: "hidden", // Prevent horizontal scroll bar
    backgroundImage: `url(${BACKGROUND_IMAGE})`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    padding: 40,
    boxSizing: "border-box",
    fontFamily: "'Share Tech Mono', monospace",
    color: "#25626c",
    display: "flex",
    justifyContent: "center",
    alignItems: "flex-start",
    gap: 40,
    flexWrap: "wrap",
  },
  box: {
    backgroundColor: "rgba(224, 247, 250, 0.85)",
    padding: 30,
    borderRadius: 18,
    border: "2px solid #adceeb",
    boxShadow: "2px 4px 0 0 #addfe8",
    maxWidth: 450,
    flexGrow: 1,
    boxSizing: "border-box",
    opacity: 1,
    animationName: "floating",
    animationDuration: "8s",
    animationIterationCount: "infinite",
    animationDirection: "alternate",
    animationTimingFunction: "ease-in-out",
  },
  descBox: {
    animationDelay: "0s",
  },
  actionBox: {
    animationDelay: "1s",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    maxWidth: 300,
  },
  heading: {
    fontSize: "clamp(28px, 5vw, 40px)",
    fontWeight: "bold",
    marginBottom: 12,
    textShadow: "1px 1px 0 #b7e6e3",
  },
  subheading: {
    fontSize: "clamp(16px, 2.5vw, 20px)",
    color: "#4a7c79",
    marginBottom: 20,
  },
  paragraph: {
    fontSize: "1.15em",
    lineHeight: 1.6,
    userSelect: "none",
  },
  actionHeading: {
    fontSize: "clamp(24px, 4vw, 32px)",
    fontWeight: "bold",
    marginBottom: 16,
    textShadow: "1px 1px 0 #b7e6e3",
    userSelect: "none",
  },
  actionText: {
    fontSize: "1.1em",
    marginBottom: 28,
    userSelect: "none",
    textAlign: "center",
  },
  button: {
    background: "#b7e6e3",
    border: "2px solid #56b1ac",
    borderRadius: 10,
    color: "#25626c",
    padding: "14px 38px",
    fontSize: "1.2em",
    cursor: "pointer",
    boxShadow: "1px 2.5px #b9e3ea",
    fontFamily: "'Share Tech Mono', monospace",
    transition: "background 0.3s, box-shadow 0.3s, transform 0.3s",
    userSelect: "none",
  },
  buttonHover: {
    background: "#a1d8d5",
    boxShadow: "1px 4px 7px #8ac3c0",
    transform: "scale(1.05)",
  },
};

export default function Home() {
  const navigate = useNavigate();
  const [hover, setHover] = useState(false);

  return (
    <>
      <style>{`
        @keyframes floating {
          0% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-15px);
          }
          100% {
            transform: translateY(0);
          }
        }
      `}</style>

      <div style={styles.wrapper}>
        <section style={{ ...styles.box, ...styles.descBox }}>
          <h1 style={styles.heading}>Welcome to SmartPitch!</h1>
          <div style={styles.subheading}>Your assistant to craft smart pitches</div>
          <p style={styles.paragraph}>
            SmartPitch is your AI-powered assistant designed to make
            your job hunting journey simpler and more productive. Upload your 
            resume and job descriptions with ease, and get tailored, professional email 
            pitches that highlight your strengths.
            <br />
            <br />
            Whether you’re applying for your dream job or exploring new career opportunities,
            SmartPitch crafts pitches that get noticed and increase your chances of landing interviews.
            Save time and impress recruiters with pitches customized for each job—effortlessly!
            <br />
            <br />
            Ready to transform your job search? Let SmartPitch help you make smarter pitches today!
          </p>
        </section>

        <section 
          style={{ ...styles.box, ...styles.actionBox }}
        >
          <h2 style={styles.actionHeading}>Ready to try it out?</h2>
          <p style={styles.actionText}>Upload your resume and let the magic begin!</p>
          <button
            style={hover ? { ...styles.button, ...styles.buttonHover } : styles.button}
            onClick={() => navigate("/upload")}
            onMouseEnter={() => setHover(true)}
            onMouseLeave={() => setHover(false)}
          >
            Upload Resume
          </button>
        </section>
      </div>
    </>
  );
}
