from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, upload, upload_jd
app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Include the auth router
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include the upload router
app.include_router(upload.router, prefix="/upload", tags=["upload"])

#Incllude the upload jd endpoint
app.include_router(upload_jd.router, prefix="/upload", tags=["jd"])


#uvicorn app.main:app --reload

