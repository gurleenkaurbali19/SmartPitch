<h1 align="center">💼 SmartPitch</h1>
<h4 align="center">Your AI-powered helper to make smart pitches</h4>

---

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/1f9f2af3-a6d0-43c0-b3dc-077a8aa68fc7" width="300" alt="Login Page" />
      <br/>
      <b>Login Page</b>
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/974b435f-b312-436d-839d-37b3ea0e06ab" width="300" alt="Resume Upload" />
      <br/>
      <b>Home page</b>
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/b078617d-8aaf-41e8-8046-1f1b6af37390" width="300" alt="Relevance Summary" />
      <br/>
      <b>Resume/JD upload page</b>
    </td>
  </tr>
</table>




## 🧠 Overview

**SmartPitch** is an AI-powered full-stack platform that helps users **create smart, personalized job applications**.  
It intelligently matches uploaded resumes with job descriptions, analyzes relevancy using embeddings and LLMs, and drafts customized job application emails, helping users pitch themselves effectively.

---

## 🚀 Key Features

✅ **User Authentication System**  
- Secure signup and login with OTP verification   

✅ **Resume Upload & Vectorization**  
- Upload resume (PDF)  
- Extracts structured sections like skills, experience, and education  
- Generates semantic embeddings using SentenceTransformer  
- Stores embeddings in FAISS vector databases per user  

✅ **Job Description Upload & Parsing**  
- Upload JD or paste text directly  
- Extracts roles, skills, responsibilities, and requirements  
- Converts them into embeddings for vector comparison  

✅ **AI-Powered Resume–JD Matching**  
- Performs semantic similarity search between user resume and JD  
- Highlights best-matching sections  
- Generates a natural-language **Relevance Summary** with Cohere LLM  

✅ **Smart Application Email Generator**  
- Uses LLM to create a personalized job application email  
- Adapts tone, style, and content based on match level  

✅ **Frontend Integration**  
- Simple yet interactive React UI  
- Built for smooth, step-by-step flow from login → upload → analysis → results  

---

## 🧩 Project Architecture
```
SmartPitch/
│
├── smartPitchBackend/                      # FastAPI backend
│   ├── app/
│   │   ├── routers/                        # API route handlers
│   │   │   ├── auth.py                     # Signup/Login/OTP routes
│   │   │   ├── draft_email.py              # Job application email generator
│   │   │   ├── upload.py                   # Resume upload & processing
│   │   │   ├── upload_jd.py                # Job description upload & parsing
│   │   │   └── __init__.py
│   │   │
│   │   ├── schemas/                        
│   │   ├── services/                       
│   │   ├── utils/                          # helper scripts
│   │   │   ├── create_tables.py            # Create DB tables
│   │   │   ├── drop_tables.py              # Drop all tables
│   │   │   ├── check_tables.py             # Verify tables
│   │   │   ├── check_users.py              # Check user data
│   │   │   ├── delete_users.py             # Delete users
│   │   │   ├── print_all_tables.py         # View all DB tables
│   │   │   ├── view_users.py               # Print user list
│   │   │   ├── view_email_logs.py          # Check sent email logs
│   │   │   ├── crud.py                     # Core DB operations
│   │   │   └── __init__.py
│   │   │
│   │   ├── database.py                     # SQLModel DB setup
│   │   ├── models.py                       # Database models (User, Resume, JD, etc.)
│   │   ├── main.py                         # FastAPI entrypoint
│   │   └── __init__.py
│   │
│   ├── .env                                # Environment variables
│   ├── requirements.txt                    # Python dependencies
│   └── smartpitch.db                       # SQLite database file
│
├── smartpitchfrontend/                     # React frontend
│   ├── public/                             # Static files
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/                       # Auth-related components
│   │   │   │   ├── AuthPage.js             # Login/Signup page
│   │   │   │   └── Home.js                 # Post-login home/dashboard
│   │   │   │
│   │   │   ├── upload/                     # Upload-related components
│   │   │   │   └── UploadPage.js           # Resume/JD upload page
│   │   │
│   │   ├── App.js                        
│   │   ├── App.css                        
│   │   ├── App.test.js                     
│   │   ├── index.js                        
│   │   └── index.css                       
│   │
│   ├── package.json                        
│   └── node_modules/                       
│
├── .gitignore                              
└── README.md                               

```

---

## 🗄️ Database Schema

**Tables included:**

| Table | Description |
|--------|--------------|
| `users` | Stores user info, hashed passwords, and signup timestamps |
| `resumes` | Tracks uploaded resumes with filenames and file paths |
| `vector_meta` | Stores FAISS vector folder paths and metadata |


---

## ⚙️ Tech Stack

| Layer | Technology |
|--------|-------------|
| **Frontend** | React |
| **Backend** | FastAPI + SQLModel |
| **Database** | SQLite |
| **Embeddings** | SentenceTransformer (`all-MiniLM-L6-v2`) |
| **Vector Store** | FAISS |
| **AI Model (LLM)** | Cohere (`command-r-plus-08-2024`) |
| **Authentication** | JWT Tokens + OTP Email Verification |

---

## 🧱 Modules & Workflow

### 1️⃣ User Authentication
- Signup with email → OTP sent → verify OTP → set password  
- Login with email + password → JWT token generated  
- Frontend maintains session token for access  

### 2️⃣ Resume Upload
- PDF uploaded → parsed → cleaned → structured into sections  
- Embeddings generated per section  
- Stored inside user’s FAISS index in `resume_vectors/{user_id}`  

### 3️⃣ Job Description Upload
- JD uploaded or pasted → sectioned → embeddings generated  
- Stored temporarily for matching  

### 4️⃣ Resume ↔ JD Matching
- Cosine similarity calculated between JD and resume embeddings  
- Retrieves top matching chunks  
- Cohere LLM generates an AI-based relevance summary  

### 5️⃣ Smart Email Generator
- AI drafts personalized job application emails  
- Uses candidate name, skills, and JD keywords dynamically  

---

## 🧰 Installation & Setup

### Backend (FastAPI)
```
cd smartPitchBackend
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate (Windows)
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (React)
```
cd smartPitchFrontend
npm start
```

---

## 🧑‍💻 Example Signup Flow

1️⃣ Enter email → Request OTP  
2️⃣ Check email → Enter OTP → Verify  
3️⃣ Set password → Create account  
4️⃣ Login → Upload resume → Upload JD → Get match summary  

---

## 👩‍💻 Author

Gurleen Kaur Bali  
🎓 Oracle Certified Generative AI Professional | Data Science & Full Stack Developer

---


