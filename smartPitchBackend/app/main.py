from fastapi import FastAPI
from app.routers import auth
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

origins = [
    "http://localhost:3000",  
]

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


#uvicorn app.main:app --reload

