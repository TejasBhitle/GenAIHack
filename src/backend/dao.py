from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Boolean, String, Text, ForeignKey
from sqlalchemy.orm import relationship

import os
import shutil

# from models import Project, Chat



BACKEND_DIR = "../backend_hosted_files"
os.makedirs(BACKEND_DIR, exist_ok=True)

# Database setup
DATABASE_URL = f"sqlite:///{BACKEND_DIR}/sqlite.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def upload_pdf_files(files):
    file_paths = []
    os.makedirs(f"{BACKEND_DIR}/project_files", exist_ok=True)
    for file in files:
        file_path = os.path.join(f"{BACKEND_DIR}/project_files", file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_paths.append(file_path)
    return file_paths


def project_create(name: str, description: str, files, db: SessionLocal):
    project = Project(name=name, description=description, input_files=",".join(files))
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_all_projects(db: SessionLocal):
    return db.query(Project).all()


def get_project(project_id: int, db: SessionLocal):
    return db.query(Project).filter(Project.id == project_id).first()


def update_project_status(project_id: int, is_ready: Boolean, db: SessionLocal):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise Exception("Project not found")
    
    project.is_ready = is_ready
    db.commit()
    db.refresh(project)
    return project

def project_delete(project_id: int, db: SessionLocal):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise Exception("Project not found")
    
    db.delete(project)
    db.commit()

def chat_create(question: str, answer: str, project_id: int, db: SessionLocal):

    chat = Chat(question=question, answer=answer, project_id=project_id)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def get_all_chats(project_id: int, db: SessionLocal):
    return db.query(Chat).filter(Chat.project_id == project_id).all()


def update_chat_answer(chat_id: int, new_answer: str, db: SessionLocal):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise Exception("Chat not found")
    
    chat.answer = new_answer
    db.commit()
    db.refresh(chat)
    return chat

def chat_delete(chat_id: int, db: SessionLocal):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise Exception("Chat not found")
    
    db.delete(chat)
    db.commit()

# Models
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    input_files = Column(Text)  # Comma-separated file paths
    is_ready = Column(Boolean, unique=False, default=False)

    chats = relationship("Chat", back_populates="project")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text)
    answer = Column(Text)
    project_id = Column(Integer, ForeignKey("projects.id"))

    project = relationship("Project", back_populates="chats")

Base.metadata.create_all(bind=engine)