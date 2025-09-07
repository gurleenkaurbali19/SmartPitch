from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.auth_bearer import JWTBearer
from app.utils.auth_handler import decode_access_token
from app.utils.upload_utils import (
    save_resume_file,
    extract_text_from_pdf,
    generate_embedding,
    save_embedding,
    update_resume_record,
    update_vector_meta_record
)
from app.database import get_db

router = APIRouter()

@router.post("/resume", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    token: str = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    # Check file content type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed.")

    # Decode JWT token to get user email
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or missing user info.")
    user_email = payload["sub"]

    # Save uploaded resume PDF
    file_path = save_resume_file(user_email, file)

    # Extract text from the saved PDF file
    text = extract_text_from_pdf(file_path)

    # Generate vector embeddings from text
    embedding = generate_embedding(text)

    # Save embeddings as numpy file
    save_embedding(user_email, embedding)

    # Update the resume metadata record in DB
    resume_record = update_resume_record(db, user_email, f"{user_email}.pdf")

    # Update the vector_meta metadata record in DB linked to the resume
    _ = update_vector_meta_record(db, user_email, resume_record.res_id)

    return {"detail": f"Resume uploaded and processed successfully for user {user_email}."}
