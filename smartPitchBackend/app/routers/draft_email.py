from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.utils.auth_bearer import JWTBearer
from app.utils.auth_handler import decode_access_token
from app.database import get_db
from app.utils.draft_email_utils import drafting_email


router = APIRouter()


class DraftEmailRequest(BaseModel):
    jd_sections: dict
    llm_relevance_summary: str
    candidate_name: str
    email_length: int = 120          # New param for desired word count
    tone: str = "Formal"             # New param for tone/style
    detail_level: str = "Summary"    # New param: Summary or Detailed
    closing: str = "Regards"         # New param for email closing line


@router.post("/draft-email", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_200_OK)
async def draft_email_endpoint(
    request: DraftEmailRequest,
    token: str = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token.")
    user_email = payload["sub"]

    try:
        email_draft = drafting_email(
            jd_sections=request.jd_sections,
            llm_relevance_response=request.llm_relevance_summary,
            user_email=user_email,
            db_session=db,
            email_length=request.email_length,
            tone=request.tone,
            detail_level=request.detail_level,
            closing=request.closing,
            candidate_name=request.candidate_name,
        )
        return {"email_draft": email_draft}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
