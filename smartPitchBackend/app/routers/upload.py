from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.auth_bearer import JWTBearer
from app.utils.auth_handler import decode_access_token
from app.utils.upload_utils import (
    save_resume_file,
    extract_text_from_pdf,
    generate_embeddings_for_sections,
    save_embeddings,
    update_resume_record,
    update_vector_meta_record
)
from app.database import get_db
import os
from app.utils.upload_utils import RESUME_VECTORS_DIR
from app.models import VectorMeta

router = APIRouter()

@router.post("/resume", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    token: str = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed.")

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or missing user info.")
    user_email = payload["sub"]

    file_path = save_resume_file(user_email, file)

    sections_dict = extract_text_from_pdf(file_path)

    embeddings_dict = generate_embeddings_for_sections(sections_dict)

    save_embeddings(user_email, embeddings_dict)

    resume_record = update_resume_record(db, user_email, f"{user_email}.pdf", file_path)

    # Check if a VectorMeta record exists for user + resume
    existing_vector_meta = db.query(VectorMeta).filter(
        VectorMeta.user_id == resume_record.user_id,
        VectorMeta.resume_id == resume_record.res_id
    ).first()

    faiss_vector_id_to_use = existing_vector_meta.faiss_vector_id if existing_vector_meta else None

    vector_folder_path = os.path.join(RESUME_VECTORS_DIR, user_email)
    _ = update_vector_meta_record(
        db,
        user_email,
        resume_record.res_id,
        faiss_vector_id=faiss_vector_id_to_use,
        vector_folder_path=vector_folder_path,
    )

    return {"detail": f"Resume uploaded and processed successfully for user {user_email}."}
