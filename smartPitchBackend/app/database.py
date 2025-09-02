from sqlalchemy import create_engine  # For connecting to the database
from sqlalchemy.ext.declarative import declarative_base  # To create base class for ORM models
from sqlalchemy.orm import sessionmaker  # To create DB session factory

# Database URL - SQLite file in current folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./smartpitch.db"  

# Create the database engine - connects SQLAlchemy to SQLite database file
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# autocommit=False means you manually commit changes to save them
# autoflush=False means changes are only sent to DB when commit or flush called
# bind=engine connects sessions to the database engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that database models will inherit
# It keeps track of all models and mappings to tables
Base = declarative_base()
