import os
import json
from dotenv import load_dotenv
from langchain_cohere import ChatCohere
from langchain_core.messages import HumanMessage
from sqlmodel import Session
from app.models import VectorMeta, User

load_dotenv()
api_key = os.getenv("COHERE_API_KEY")

# Initialize Cohere chat client once
chat = ChatCohere(api_key=api_key, model="command-r-plus-08-2024")


def get_resume_vector_folder(user_email: str, db_session: Session) -> str:
    """
    Retrieve the absolute path to the user's resume vector folder stored in DB.
    Raises ValueError if not found.
    """
    vector_meta = db_session.query(VectorMeta).join(User).filter(User.email == user_email).first()
    if not vector_meta or not vector_meta.vector_folder_path:
        raise ValueError(f"Vector folder path not found for user: {user_email}")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # utils folder
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))  # project root
    resume_vectors_path = os.path.normpath(os.path.join(PROJECT_ROOT, vector_meta.vector_folder_path))
    return resume_vectors_path


def load_resume_header_json(vector_folder_path: str) -> list:
    """
    Loads the header.json file from user's resume vector folder.
    Returns a list from JSON or empty list if cannot load.
    """
    header_json_path = os.path.join(vector_folder_path, "header.json")
    try:
        with open(header_json_path, "r", encoding="utf-8") as f:
            header_data = json.load(f)
        return header_data
    except Exception as e:
        print(f"Warning: Could not load header.json from {header_json_path}: {e}")
        return []


def drafting_email(
    jd_sections: str,
    llm_relevance_response: str,
    user_email: str,
    db_session: Session,
    email_length: int = 120,
    tone: str = "Formal",
    detail_level: str = "Summary",
    closing: str = "Regards",
    candidate_name: str = "Candidate"
) -> str:
    """
    Draft a professional email using JD sections, relevance summary, user's resume metadata,
    and customization parameters.

    Args:
        jd_sections: JSON string or dict of JD sections.
        llm_relevance_response: AI-generated relevance summary string.
        user_email: Candidate's email address to locate resume metadata.
        db_session: SQLModel DB session for querying vector metadata.
        email_length: Desired word count for the email.
        tone: Tone/style of the email (e.g., Formal, Friendly).
        detail_level: Summary or Detailed email style.
        closing: Custom closing line for the email.
        candidate_name: Candidate's name to personalize the email.

    Returns:
        Drafted email string from LLM.
    """

    # Get vector folder path from DB for user
    vector_folder_path = get_resume_vector_folder(user_email, db_session)
    
    # Load user's header.json metadata
    header_data = load_resume_header_json(vector_folder_path)

    # Extract candidate info
    candidate_name = header_data[0] if len(header_data) > 0 else candidate_name
    candidate_email = header_data[1] if len(header_data) > 1 else user_email
    candidate_phone = header_data[2] if len(header_data) > 2 else "N/A"
    links_list = header_data[3:] if len(header_data) > 3 else []

    # Convert JD sections to string if dict
    if isinstance(jd_sections, dict):
        jd_sections_str = json.dumps(jd_sections, indent=2)
    else:
        jd_sections_str = jd_sections

    # Compose prompt for LLM with customization params
    prompt = f"""
You are a smart AI assistant.

Draft a professional, convincing job application email on behalf of {candidate_name} (email: {candidate_email}, phone: {candidate_phone}).
Make the email approximately {email_length} words long.
Write with a {tone.lower()} tone.
Make the content {detail_level.lower()} and relevant to the position.

Given these job description sections:
{jd_sections_str}

Candidate's relevance summary:
{llm_relevance_response}

Candidate relevant projects, certifications, social and portfolio links:
{links_list}

Please mention relevant projects or certifications explicitly,
and include links such as GitHub, portfolio, LinkedIn, certifications where relevant.
Use "{closing}" as the closing line for the email.
Also include a subject line with the candidate's name and position applied for.
"""

    messages = [HumanMessage(content=prompt)]
    response = chat.invoke(messages)
    return response.content
