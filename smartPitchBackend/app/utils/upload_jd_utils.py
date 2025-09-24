import os
import tempfile
import shutil
import fitz  # PyMuPDF for PDF
import re
import json
import numpy as np
import glob
from sentence_transformers import SentenceTransformer
import os
import json
import numpy as np
from sqlmodel import Session
from app.models import VectorMeta, User
from typing import Dict, List, Optional


def load_jd(file=None, text=None):
    """
    Extract JD text either from a pasted string or an uploaded PDF file.
    Returns (jd_text, file_type, temp_path)
    file_type: "text" or "pdf"
    temp_path: the temporary file's path if created, otherwise None (to allow cleanup)
    """
    if text:
        return text, "text", None

    if file:
        suffix = os.path.splitext(file.filename)[-1].lower()
        if suffix != ".pdf":
            raise ValueError("Only .pdf files are supported for JD upload.")
        temp_fd, temp_path = tempfile.mkstemp(suffix=suffix)    #Create a temporary file to save the uploaded PDF file
        with os.fdopen(temp_fd, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        try:
            doc = fitz.open(temp_path)
            jd_text = "\n".join(page.get_text() for page in doc)
        except Exception as e:
            os.remove(temp_path)
            raise e
        return jd_text, "pdf", temp_path

    raise ValueError("No file or JD text provided.")


def split_section_content(text: str) -> list:
    """
    Split the section content into list of meaningful points,
    respects bullets (*, -, •), numbered lists (1., 2., etc.) and
    joins continuation lines.
    """
    if not text:
        return []

    bullets_pattern = re.compile(r'^\s*([\*\-\u2022]|\d+\.)\s+', re.MULTILINE)
    lines = text.split('\n')
    items = []
    current_item = ""

    for line in lines:
        if bullets_pattern.match(line):
            if current_item:
                items.append(current_item.strip())
            current_item = bullets_pattern.sub('', line).strip()
        else:
            if current_item:
                current_item += " " + line.strip()
            else:
                current_item = line.strip()

    if current_item:
        items.append(current_item.strip())

    return items

def extract_jd_sections(jd_text: str) -> dict:
    """
    Extract JD sections by splitting on common headings,
    ignoring case and optional escape chars around headers.
    Returns dict of {section_name: list_of_points}.
    """
    section_headers = [
        "Key Responsibilities", "Required Qualifications", "Preferred Qualification", "What We Offer",
        "Job Title", "Role", "Position", "Summary", "About the Company", "Qualifications",
        "Company Description","Professional & Technical Skills","Location" "Responsibilities", "Duties", "What You'll Do", "Requirements",
        "Mandatory Qualifications","Role Overview","Skills", "Basic Qualifications", "Nice to Have", "Desired Skills",
        "Compensation", "Salary", "Perks", "Benefits", "Location", "Work Location",
        "How to Apply", "Application Process", "Contact Information","Required Skills and Experience"
    ]

    escaped_headers = [re.escape(h) for h in section_headers]

    header_pattern = re.compile(
        r"^\s*[\\/]*\s*(" + "|".join(escaped_headers) + r")\s*[\\/]*\s*:?\s*$",
        re.MULTILINE | re.IGNORECASE
    )

    matches = list(header_pattern.finditer(jd_text))
    if not matches:
        return {"full_text": split_section_content(jd_text.strip())}

    section_positions = [m.start() for m in matches] + [len(jd_text)]
    section_names = [m.group(1).strip() for m in matches]

    sections = {}
    for i, header in enumerate(section_names):
        start = section_positions[i]
        end = section_positions[i + 1]
        block_lines = jd_text[start:end].splitlines()
        
        # Remove the first line, which is usually the header line
        content_lines = block_lines[1:]  
        
        # strip empty lines and whitespace
        points = [line.strip() for line in content_lines if line.strip()]
        
        key = header.lower().replace(" ", "_")
        sections[key] = points
        

    return sections


def create_jd_json_files(jd_sections: dict) -> dict:
    """
    Given jd_sections dictionary {section_name: list_of_points}, create 
    temporary JSON files for each section.

    Returns a dictionary mapping section_name to JSON file path.
    """

    temp_dir = tempfile.mkdtemp(prefix="jd_json_")

    file_paths = {}

    for section, content in jd_sections.items():
        file_path = os.path.join(temp_dir, f"{section}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        file_paths[section] = file_path

    return file_paths

def create_jd_section_embeddings(jd_json_dir: str, 
                                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> str:
    """
    Create vector embeddings for each section JSON file in jd_json_dir.
    Save embeddings as .npy files in the same directory.
    
    Args:
        jd_json_dir: path to directory where sectionwise JD JSON files are located
        model_name: SentenceTransformer model name
    
    Returns:
        The directory path where the embeddings were saved.
    """
    if not os.path.exists(jd_json_dir):
        raise FileNotFoundError(f"JD JSON directory {jd_json_dir} does not exist.")

    embedder = SentenceTransformer(model_name)

    # Clean out old .npy embedding files if any
    existing_npy_files = glob.glob(os.path.join(jd_json_dir, "*.npy"))
    for npy_file in existing_npy_files:
        try:
            os.remove(npy_file)
        except Exception as e:
            print(f"Warning: Unable to remove old embedding file {npy_file}: {e}")

    # Find all section json files
    json_files = glob.glob(os.path.join(jd_json_dir, "*.json"))
    for json_file in json_files:
        section_name = os.path.splitext(os.path.basename(json_file))[0]

        with open(json_file, "r", encoding="utf-8") as jf:
            content = json.load(jf)

        # Prepare texts for embedding based on content structure
        texts_to_embed = []
        if isinstance(content, list):
            # check if list of dict with 'name' and 'points'
            if content and isinstance(content[0], dict) and "name" in content[0] and "points" in content[0]:
                for entry in content:
                    combined = entry["name"]
                    if entry["points"]:
                        combined += " " + " ".join(entry["points"])
                    texts_to_embed.append(combined)
            else:
                # list of strings
                texts_to_embed = content
        elif isinstance(content, str):
            texts_to_embed = [content]
        else:
            # fallback: serialize and embed as string
            texts_to_embed = [json.dumps(content)]

        if not texts_to_embed:
            print(f"No content to embed for section {section_name}, skipping.")
            continue

        # Generate embeddings numpy array
        embeddings = embedder.encode(texts_to_embed, convert_to_numpy=True)

        # Save embedding as .npy file named by section
        npy_path = os.path.join(jd_json_dir, f"{section_name}.npy")
        try:
            np.save(npy_path, embeddings)
            print(f"Saved JD embeddings for section {section_name} at {npy_path}")
        except Exception as e:
            print(f"Error saving embeddings for section {section_name}: {e}")

    print(f"All JD section embeddings created in {jd_json_dir}")
    return jd_json_dir



from numpy.linalg import norm

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    if norm(v1) == 0 or norm(v2) == 0:
        return 0.0
    return np.dot(v1, v2) / (norm(v1) * norm(v2))


def relevance_search(
    user_email: str,
    jd_json_dir: str,
    jd_embedding_dir: str,
    db_session: Session,
    jd_section_map: Optional[Dict[str, List[str]]] = None,
    resume_section_titles: Optional[List[str]] = None,
) -> Dict[str, Dict[str, List[str]]]:
    """
    Perform hybrid similarity search between JD embeddings and Resume embeddings.
    Args:
        user_email: The user's email to find resume vector folder path.
        jd_json_dir: Folder path with JD section JSON chunk files.
        jd_embedding_dir: Folder path with JD section .npy embedding files.
        db_session: SQLAlchemy session to query VectorMeta.
        jd_section_map: Mapping from JD sections to list of resume sections.
        resume_section_titles: List of all expected resume section titles.

    Returns:
        Dict of {jd_section: {resume_section: [relevant chunks]}}
    """

    if jd_section_map is None:
        jd_section_map = {
            "required_qualifications": ["skills", "education", "experience"],
            "preferred_qualification": ["skills", "education", "experience"],
            "role": ["skills", "education", "experience"],
            "key_responsibilities": ["skills", "projects", "experience"],
            "professional_technical_skills": ["skills", "education", "experience"],
            "nice_to_have": ["skills", "projects", "experience"],
            "desired_skills": ["skills", "projects", "experience"],
            "responsibilities": ["skills", "projects", "experience"],
            "duties": ["skills", "projects", "experience"],
            "what_you_ll_do": ["skills", "projects", "experience"],
            
        }

    if resume_section_titles is None:
        resume_section_titles = [
            "summary", "objective", "education", "experience", "work_experience",
            "skills", "projects", "certifications", "contact", "links", "profile"
        ]

    # Get user's vector folder relative path from DB
    vector_meta = db_session.query(VectorMeta).join(User).filter(User.email == user_email).first()

    if not vector_meta or not vector_meta.vector_folder_path:
        raise ValueError(f"Vector folder path not found for user: {user_email}")

    # Compose absolute resume vectors folder path based on current location
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # utils folder
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))  # adjust to root
    resume_vectors_path = os.path.normpath(os.path.join(PROJECT_ROOT, vector_meta.vector_folder_path))

    results = {}

    for jd_section, mapped_resume_sections in jd_section_map.items():
        # Load JD section embedding
        jd_embedding_path = os.path.join(jd_embedding_dir, f"{jd_section}.npy")
        jd_json_path = os.path.join(jd_json_dir, f"{jd_section}.json")

        if not os.path.exists(jd_embedding_path) or not os.path.exists(jd_json_path):
            continue

        jd_embedding = np.load(jd_embedding_path)
        with open(jd_json_path, "r", encoding="utf-8") as f:
            jd_chunks = json.load(f)

        # Accumulate resume relevant chunks per resume section
        relevant_resume_chunks = {}

        for resume_section in mapped_resume_sections:
            resume_npy_path = os.path.join(resume_vectors_path, f"{resume_section}.npy")
            resume_json_path = os.path.join(resume_vectors_path, f"{resume_section}.json")

            if not os.path.exists(resume_npy_path) or not os.path.exists(resume_json_path):
                continue

            # Load resume embeddings and chunks
            resume_embeddings = np.load(resume_npy_path)
            with open(resume_json_path, "r", encoding="utf-8") as f:
                resume_chunks = json.load(f)

            # Ensure JD embedding and resume embeddings shapes
            if len(jd_embedding.shape) == 1:
                jd_embedding = jd_embedding.reshape(1, -1)
            if len(resume_embeddings.shape) == 1:
                resume_embeddings = resume_embeddings.reshape(1, -1)

            # Compute cosine similarity from JD section vector vs all resume section vectors
            similar_scores = []
            for idx, r_vec in enumerate(resume_embeddings):
                score = cosine_similarity(jd_embedding[0], r_vec)
                similar_scores.append((score, idx))

            # Sort by score descending and take top-k (e.g., top 3 or more)
            top_k = 3
            top_matches = sorted(similar_scores, key=lambda x: x[0], reverse=True)[:top_k]

            # Extract corresponding resume chunks text for top matches
            matched_chunks = []
            for score, idx in top_matches:
                # Defensive chunk extraction considering content structure
                if isinstance(resume_chunks, list):
                    if idx < len(resume_chunks):
                        matched_chunks.append(resume_chunks[idx])
                elif isinstance(resume_chunks, str):
                    matched_chunks.append(resume_chunks)
                else:
                    # fallback case: stringifying content
                    matched_chunks.append(str(resume_chunks))

            relevant_resume_chunks[resume_section] = matched_chunks

        if relevant_resume_chunks:
            results[jd_section] = relevant_resume_chunks

    return results
