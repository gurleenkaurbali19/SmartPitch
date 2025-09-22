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
import json
from typing import Dict, List
import glob

# Get base directory relative to this file's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Use environment variables as overrides, or fallback to base dir + relative folder
RESUME_VECTORS_DIR = os.getenv("RESUME_VECTORS_DIR", os.path.join(BASE_DIR, "..", "resume_vectors"))
RESUME_UPLOAD_DIR = os.getenv("RESUME_UPLOAD_DIR", os.path.join(BASE_DIR, "..", "resume_uploads"))

# Normalize absolute paths
RESUME_VECTORS_DIR = os.path.abspath(RESUME_VECTORS_DIR)
RESUME_UPLOAD_DIR = os.path.abspath(RESUME_UPLOAD_DIR)

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



def extract_text_from_pdf(pdf_path: str) -> Dict[str, List[str]]:
    """
    Extract text and links from resume PDF:
    - Extract header info: name, emails, phones, all links (from annotations and text).
    - Extract sections by headings.
    - Always return each section as list of string items for consistent output.
    - Links like 'live project', 'certificate', 'github demo' are excluded from main text sections.
    """

    # section title list
    section_titles = [
        "summary", "objective", "education", "experience", "work experience",
        "skills", "projects", "certifications", "contact", "links", "profile"
    ]

    # defining pattern to match the section titles
    pattern = re.compile(
        rf"(?im)^({'|'.join([re.escape(t) for t in section_titles])})",
        re.MULTILINE
    )

    # helper function to split the content inside a section based on separators
    def split_section_text_to_list(text: str):
        items = re.split(r"\n{2,}|[\n*•\-]\s*|\n\d+\.\s*|\|", text)
        items = [item.strip() for item in items if item.strip()]
        return items

    # read pdf
    doc = fitz.open(pdf_path)
    full_text = "\n".join(page.get_text() for page in doc)

    # Extract all links (from annotations and text)
    annotation_links = []
    for page in doc:
        for link in page.get_links():
            if "uri" in link:
                annotation_links.append(link["uri"])
    annotation_links = list(set(annotation_links))

    text_links = list(set(re.findall(r"https?://[^\s]+", full_text)))
    combined_links = list(set(annotation_links + text_links))

    # locate section titles
    matches = list(pattern.finditer(full_text))

    # header text before first section
    header_text = full_text[: matches[0].start()] if matches else full_text
    header_text = header_text.strip()

    # extract emails
    emails = list(set(re.findall(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", full_text
    )))

    # extract phone numbers
    phone_pattern = re.compile(r"(\+?\d[\d\s\-\(\)]{7,}\d)")
    phones = list(set(phone.strip() for phone in phone_pattern.findall(full_text)))

    # name from header (first non-empty line)
    name = ""
    for line in header_text.splitlines():
        if line.strip():
            name = line.strip()
            break

    # prepare header
    header_data = []
    if name:
        header_data.append(name)
    header_data.extend(emails)
    header_data.extend(phones)
    header_data.extend(combined_links)

    sections_dict = {"header": list(dict.fromkeys(header_data))}

    if matches:
        section_positions = [m.start() for m in matches] + [len(full_text)]
        section_names = [m.group(1).lower() for m in matches]

        for idx, section_name in enumerate(section_names):
            section_start, section_end = section_positions[idx], section_positions[idx + 1]
            section_text = full_text[section_start:section_end]

            # Remove heading line itself
            section_text = '\n'.join(section_text.split('\n')[1:]).strip()

            # Extract links inside this section
            section_links = list(set(re.findall(r"https?://[^\s]+", section_text)))

            # Remove lines that are just links
            cleaned_lines = []
            for line in section_text.splitlines():
                if re.match(r"https?://", line.strip()):
                    continue
                cleaned_lines.append(line)
            section_text = "\n".join(cleaned_lines)

            # Handle specific section types
            if section_name in ["summary", "profile", "objective", "about"]:
                sections_dict[section_name] = section_text.replace('\n', ' ').strip()
            elif section_name in ["skills", "projects", "certifications"]:
                items = re.split(r"\n{1,}|[\n*•\-]\s*|\n\d+\.\s*|;", section_text)
                items = [item.strip() for item in items if item.strip()]
                sections_dict[section_name] = items
            else:
                items = split_section_text_to_list(section_text)
                sections_dict[section_name] = items

            if section_links:
                sections_dict[f"{section_name}_links"] = section_links
    else:
        # No sections found -> fallback
        if full_text.strip():
            sections_dict["full_text"] = full_text.strip()
        if combined_links:
            sections_dict["full_text_links"] = combined_links

    return sections_dict


PROJECT_IGNORE_WORDS = {
    "project link", "link", "live project", "chatbot link",
    "dashboard", "live demo", "certificate", "link", "|"
}

def format_structured_bullets(items):
    structured = []
    current = None
    for item in items:
        item_clean = item.strip()
        if not item_clean or item_clean.lower() in PROJECT_IGNORE_WORDS:
            continue
        if item_clean.startswith(("–", "-")):
            if current:
                current['points'].append(item_clean.lstrip("–-").strip())
            else:
                # Bullet but no heading: use 'misc'
                current = {'name': "misc", 'points': [item_clean.lstrip("–-").strip()]}
                structured.append(current)
        else:
            if current and current['points'] and not current['points'][-1].endswith("."):
                current['points'][-1] += " " + item_clean
            else:
                current = {'name': item_clean, 'points': []}
                structured.append(current)
    return structured


def merge_empty_points_sequential(sections_list):
    merged = []
    i = 0
    while i < len(sections_list):
        current = sections_list[i]
        name_parts = [current['name']]
        points = current['points']

        # Merge names while points are empty and next entries exist
        while not points and i + 1 < len(sections_list):
            i += 1
            next_entry = sections_list[i]
            name_parts.append(next_entry['name'])
            points = next_entry['points']
            # If points found, stop merging further
            if points:
                break
        
        merged.append({'name': " ".join(name_parts).strip(), 'points': points})
        i += 1

    return merged


def save_json_sectionwise(user_id, extracted_dict, base_dir="resume_vectors"):
    user_dir = os.path.join(base_dir, str(user_id))
    if os.path.exists(user_dir):
        shutil.rmtree(user_dir)
    os.makedirs(user_dir, exist_ok=True)

    for section, content in extracted_dict.items():
        if section in {"projects", "certifications", "experience"} and isinstance(content, list):
            formatted = format_structured_bullets(content)
            cleaned = merge_empty_points_sequential(formatted)
            section_data = cleaned
        else:
            section_data = content

        json_path = os.path.join(user_dir, f"{section}.json")
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(section_data, jf, ensure_ascii=False, indent=2)

    return user_dir


def create_section_embeddings(user_id, base_dir="resume_vectors", model_name="sentence-transformers/all-MiniLM-L6-v2"):
    user_dir = os.path.join(base_dir, str(user_id))
    if not os.path.exists(user_dir):
        raise FileNotFoundError(f"User directory {user_dir} does not exist.")

    # Load embedding model once
    embedder = SentenceTransformer(model_name)

    # Delete any existing .npy files in user folder
    npy_files = glob.glob(os.path.join(user_dir, "*.npy"))
    for file in npy_files:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Warning: Failed to remove file {file}: {str(e)}")

    # Find all JSON files to create embeddings for
    json_files = glob.glob(os.path.join(user_dir, "*.json"))

    for json_path in json_files:
        section_name = os.path.splitext(os.path.basename(json_path))[0]

        with open(json_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        texts_to_embed = []

        # Prepare texts depending on structure
        if isinstance(content, list):
            # For list of dicts with 'name' and 'points', combine for embedding
            if content and isinstance(content[0], dict) and "name" in content[0] and "points" in content[0]:
                for entry in content:
                    combined_text = entry["name"]
                    if entry["points"]:
                        combined_text += " " + " ".join(entry["points"])
                    texts_to_embed.append(combined_text)
            else:
                # Flat list of strings (skills, header)
                texts_to_embed = content
        elif isinstance(content, str):
            texts_to_embed = [content]
        else:
            # If unknown format, convert to string and embed
            texts_to_embed = [json.dumps(content)]

        if not texts_to_embed:
            print(f"No texts to embed in section {section_name}, skipping.")
            continue

        # Generate embeddings
        embeddings = embedder.encode(texts_to_embed, convert_to_numpy=True)

        # Save embeddings as .npy file
        npy_path = os.path.join(user_dir, f"{section_name}.npy")

        try:
            np.save(npy_path, embeddings)
            print(f"Saved embeddings for section {section_name} at {npy_path}")
        except Exception as e:
            print(f"Error saving embeddings for section {section_name}: {str(e)}")

    print(f"All section embeddings created in {user_dir}")
    return user_dir


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
        resume.file_path = file_path
        resume.uploaded_at = datetime.datetime.utcnow()
    else:
        resume = Resume(
            user_id=user.user_id,
            filename=filename,
            file_path=file_path,
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
        if faiss_vector_id and faiss_vector_id != vector_meta.faiss_vector_id:
            vector_meta.faiss_vector_id = faiss_vector_id
        if vector_folder_path:
            vector_meta.vector_folder_path = vector_folder_path
        vector_meta.created_at = datetime.datetime.utcnow()
    else:
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

