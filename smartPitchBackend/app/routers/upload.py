from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.auth_bearer import JWTBearer
from app.utils.auth_handler import decode_access_token
from app.utils.upload_utils import (
    save_resume_file,
    extract_text_from_pdf,
    save_json_sectionwise,
    create_section_embeddings,
)
from app.database import get_db
from app.models import Resume
from app.utils.upload_utils import update_resume_record, update_vector_meta_record
import os

router = APIRouter()

@router.post("/resume", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    token: str = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed.")

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or missing user info.")
    user_email = payload["sub"]

    # Save the uploaded resume PDF locally
    file_path = save_resume_file(user_email, file)

    # Extract the sections dictionary from the saved PDF
    sections_dict = extract_text_from_pdf(file_path)

    # Save each section as a JSON file under resume_vectors/user_email/
    saved_folder_path = save_json_sectionwise(user_email, sections_dict)

    # Create section-wise embeddings and save as .npy files in the same folder
    create_section_embeddings(user_email)

    # Update or insert resume metadata record
    resume = update_resume_record(db, user_email, file.filename, file_path)

    # Update or insert vector meta record with path info and generated faiss_vector_id
    vector_meta = update_vector_meta_record(
        db,
        user_email,
        resume.res_id,
        vector_folder_path=saved_folder_path
    )

    return {
        "user_email": user_email,
        "resume_file_path": str(file_path),
        "extracted_sections": sections_dict,
        "json_sections_folder": saved_folder_path,
        "embedding_files_folder": saved_folder_path,
        "resume_id": resume.res_id,
        "vector_meta_id": vector_meta.vector_id,
    }
