import os
import glob
from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.utils.auth_bearer import JWTBearer
from app.utils.auth_handler import decode_access_token
from app.database import get_db

from app.utils.upload_jd_utils import (
    load_jd,
    extract_jd_sections,
    create_jd_json_files,
    create_jd_section_embeddings,
    relevance_search  # import the new relevance_search function
)

router = APIRouter()

@router.post("/jd", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def upload_jd(
    file: Optional[UploadFile] = File(None),
    jd_text: Optional[str] = Form(None),
    token: str = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    if not file and not jd_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide either JD file or pasted text.")
    if file and jd_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide only JD text or only a file, not both.")

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or missing user info.")
    user_email = payload["sub"]

    temp_path = None
    relevance_results = None
    try:
        jd_raw_text, filetype, temp_path = load_jd(file=file, text=jd_text)
        jd_sections = extract_jd_sections(jd_raw_text)

        # Create JSON files for sections
        jd_json_files = create_jd_json_files(jd_sections)

        # Create embeddings from the JSON files
        jd_json_dir = os.path.dirname(next(iter(jd_json_files.values())))
        jd_embedding_dir = create_jd_section_embeddings(jd_json_dir)

        # List section-wise embedding .npy files
        embedding_files_glob = glob.glob(os.path.join(jd_embedding_dir, "*.npy"))
        jd_embedding_files = {
            os.path.splitext(os.path.basename(f))[0]: f
            for f in embedding_files_glob
        }

        # Now run relevance search combining resume vectors and JD vectors
        relevance_results = relevance_search(
            user_email=user_email,
            jd_json_dir=jd_json_dir,
            jd_embedding_dir=jd_embedding_dir,
            db_session=db
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

    return {
        "user_email": user_email,
        "jd_sections": jd_sections,
        "jd_json_files": jd_json_files,
        "jd_embedding_dir": jd_embedding_dir,
        "jd_embedding_files": jd_embedding_files,
        "relevance_results": relevance_results,  # the output of your relevance_search function
        "file_type": filetype,
    }
