from app.database import Base, engine

# IMPORT ALL YOUR MODELS 
from app import models  # This imports models.py where all models are defined

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("All tables created or verified.")

if __name__ == "__main__":
    create_tables()
