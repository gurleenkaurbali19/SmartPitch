import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import shutil
from sqlalchemy.orm import Session
from app.models import Resume, VectorMeta, User
import datetime
import uuid
from fastapi import UploadFile
import fitz
import re

# Loading the sentence transformer model once
model = SentenceTransformer('all-mpnet-base-v2')

RESUME_VECTORS_DIR = r"D:\SmartPitch\smartPitchBackend\resume_vectors"

RESUME_UPLOAD_DIR = r"D:\SmartPitch\smartPitchBackend\resume_uploads"

def save_resume_file(user_identifier: str, file: UploadFile) -> str:
    """
    Saves the uploaded PDF file to the resume_uploads folder with the user_identifier as filename.
    Overwrites existing file if present.
    
    Returns the full saved file path.
    """
    os.makedirs(RESUME_UPLOAD_DIR, exist_ok=True)
    file_location = os.path.join(RESUME_UPLOAD_DIR, f"{user_identifier}.pdf")
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_location



def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extract section-wise from a resume,
    plus extract name, emails, phones, and links grouped under one 'header' key
    Returns dict with headers and sections as keys.
    """
    section_titles = [
        "summary", "objective", "education", "experience",
        "skills", "projects", "certifications", "contact", "links"
    ]
    
    pattern = re.compile(
        rf"(?im)^({'|'.join([re.escape(t) for t in section_titles])})\b.*", 
        re.MULTILINE
    )
    
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    
    matches = list(pattern.finditer(text))
    sections_dict = {}
    
    # Extract header text (before first section)
    header_text = ""
    if matches:
        first_section_start = matches[0].start()
        header_text = text[:first_section_start].strip()
    else:
        header_text = text.strip()
    
    # Extract emails
    email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    emails = list(set(email_pattern.findall(text)))
    
    # Extract phones
    phone_pattern = re.compile(r"(\+?\d{1,4}?[-.\s]?)?(\(?\d{2,5}\)?[-.\s]?)?[-\d.\s]{5,15}\d")
    phones_raw = phone_pattern.findall(text)
    phones = list(set("".join(p).strip() for p in phones_raw if any(p)))
    
    # Extract relevant links (github, linkedin, portfolio)
    link_pattern = re.compile(r"(https?://[^\s]+)")
    links_all = link_pattern.findall(text.lower())
    links = list(set(l for l in links_all if "github.com" in l or "linkedin.com" in l or "portfolio" in l or "personal" in l))
    
    # Extract name heuristic: first non-empty line of header_text
    name = ""
    for line in header_text.splitlines():
        line = line.strip()
        if line:
            name = line
            break
    
    # Compose header list
    header_list = []
    if name:
        header_list.append(name)
    header_list.extend(emails)
    header_list.extend(phones)
    header_list.extend(links)
    sections_dict["header"] = header_list
    
    # Extract other sections like before
    if matches:
        section_positions = [m.start() for m in matches] + [len(text)]
        section_names = [m.group(1).strip().lower() for m in matches]
        for i, section in enumerate(section_names):
            section_text = text[section_positions[i]:section_positions[i+1]].strip()
            if section in ["skills", "projects", "certifications"]:
                items = re.split(r"\n[-*•]\s*|\n\d+\.\s*", section_text)
                items = [item.strip() for item in items if item.strip()]
                if items:
                    sections_dict[section] = items
            else:
                if section_text:
                    sections_dict[section] = section_text
    else:
        # no headings detected
        if text.strip():
            sections_dict["full_text"] = text.strip()
    
    return sections_dict


def generate_embeddings_for_sections(sections_dict):
    """
    Given sections_dict from extract_text_from_pdf (keys: section names, values: str or list),
    generate vector embeddings for each section and its items.
    Returns a nested dict: {section: [embeddings]} for list sections,
    or {section: embedding} for text sections.
    """
    embeddings_dict = {}

    for section, content in sections_dict.items():
        # If content is a list (skills, projects, etc.), embed each item
        if isinstance(content, list):
            embeddings = [model.encode(item) for item in content if item.strip()]
            embeddings_dict[section] = embeddings
        else:
            # For plain text sections (summary, experience, etc.), embed the text
            if content.strip():
                embeddings_dict[section] = model.encode(content)

    return embeddings_dict

def save_embeddings(user_identifier: str, embeddings_dict: dict):
    """
    Saves embeddings provided as a dict {section_name: embedding_or_list_of_embeddings}
    into the user subfolder inside RESUME_VECTORS_DIR.
    Each section saved as a separate .npy file, e.g. skills.npy, projects.npy, etc.
    """
    user_folder = os.path.join(RESUME_VECTORS_DIR, user_identifier)
    os.makedirs(user_folder, exist_ok=True)

    for section, emb in embeddings_dict.items():
        embedding_path = os.path.join(user_folder, f"{section}.npy")

        # Embedding might be a list of numpy arrays or a single numpy array
        if isinstance(emb, list):
            np.save(embedding_path, np.array(emb))
        else:
            np.save(embedding_path, emb)


def update_resume_record(db: Session, user_email: str, filename: str, file_path: str) -> Resume:
    """
    Adds or updates a resume record for the given user email.
    Only one resume per user is allowed.
    Returns the Resume object.
    """
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise ValueError("User not found")

    resume = db.query(Resume).filter(Resume.user_id == user.user_id).first()
    if resume:
        resume.filename = filename
        resume.file_path = file_path  # Store the path
        resume.uploaded_at = datetime.datetime.utcnow()
    else:
        resume = Resume(
            user_id=user.user_id,
            filename=filename,
            file_path=file_path,  # Store path on creation
            uploaded_at=datetime.datetime.utcnow()
        )
        db.add(resume)

    db.commit()
    db.refresh(resume)
    return resume


def update_vector_meta_record(db: Session, user_email: str, resume_id: int, faiss_vector_id: str = None, vector_folder_path: str = None) -> VectorMeta:
    """
    Adds or updates a vector_meta record for the user and resume.
    Generates a new faiss_vector_id if not provided and creates if not found.
    Returns the VectorMeta object.
    """
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise ValueError("User not found")

    vector_meta = db.query(VectorMeta).filter(
        VectorMeta.user_id == user.user_id,
        VectorMeta.resume_id == resume_id
    ).first()

    if vector_meta:
        # Update fields if new values are provided
        if faiss_vector_id and faiss_vector_id != vector_meta.faiss_vector_id:
            vector_meta.faiss_vector_id = faiss_vector_id
        if vector_folder_path:
            vector_meta.vector_folder_path = vector_folder_path
        vector_meta.created_at = datetime.datetime.utcnow()
    else:
        # Create new record with unique faiss_vector_id if not provided
        if not faiss_vector_id:
            faiss_vector_id = str(uuid.uuid4())
        vector_meta = VectorMeta(
            user_id=user.user_id,
            resume_id=resume_id,
            faiss_vector_id=faiss_vector_id,
            vector_folder_path=vector_folder_path,
            created_at=datetime.datetime.utcnow()
        )
        db.add(vector_meta)

    db.commit()
    db.refresh(vector_meta)
    return vector_meta
