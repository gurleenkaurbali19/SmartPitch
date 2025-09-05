from fastapi import FastAPI
from app.routers import auth

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Include the auth router
app.include_router(auth.router, prefix="/auth", tags=["auth"])


#uvicorn app.main:app --reload

