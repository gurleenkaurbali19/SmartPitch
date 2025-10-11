from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import datetime


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    vectors = relationship("VectorMeta", back_populates="user", cascade="all, delete-orphan")
   


class Resume(Base):
    __tablename__ = "resumes"

    res_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=True)  # store path to resume file
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="resumes")
    vectors = relationship("VectorMeta", back_populates="resume", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint('user_id', name='unique_resume_per_user'),)


class VectorMeta(Base):
    __tablename__ = "vector_meta"

    vector_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.res_id"), nullable=True, index=True)
    faiss_vector_id = Column(String, unique=True, nullable=False)
    vector_folder_path = Column(String, nullable=True)  # New: store path to vector embeddings folder
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="vectors")
    resume = relationship("Resume", back_populates="vectors")

    __table_args__ = (
        UniqueConstraint("user_id", "resume_id", name="uq_user_resume_vector"),
    )

