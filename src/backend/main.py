from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form, BackgroundTasks
from pymodels import ProjectResponse, ChatResponse, SimpleResponse
from llm_utils import handle_project_init, handle_question
from typing import List
import dao
import os


app = FastAPI()


@app.post("/projects/create", response_model=ProjectResponse)
async def create_project(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    description: str = Form(...), 
    files: List[UploadFile] = File(...),
    db: dao.SessionLocal = Depends(dao.get_db) 
):
    
    file_paths = dao.upload_pdf_files(files)
    project = dao.project_create(name, description, file_paths, db)

    background_tasks.add_task(handle_project_init, project.id, project.input_files, db,on_llm_response_init)

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        input_files=file_paths,
        is_ready=False
    )

def on_llm_response_init(project_id: int, db: dao.SessionLocal):
    print(f"LLM response for project {project_id} init")
    dao.update_project_status(project_id, True, db)


@app.get("/projects/get_all", response_model=List[ProjectResponse])
async def get_all_projects(
    db: dao.SessionLocal = Depends(dao.get_db)
):
    return [
        ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            is_ready=project.is_ready,
            input_files=project.input_files.split(",")
        )
        for project in dao.get_all_projects(db)
    ]


@app.post("/projects/{project_id}/chats/ask_question", response_model=ChatResponse)
async def ask_question(
    background_tasks: BackgroundTasks,
    project_id: int, 
    question: str = Form(...),
    db: dao.SessionLocal = Depends(dao.get_db)
    ):
    
    project = dao.get_project(project_id, db)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    answer = "..." # Will be updated later from llm in background

    chat = dao.chat_create(question, answer, project_id, db)

    background_tasks.add_task(handle_question, project.id, chat.id, question, db, on_llm_response_question)

    return ChatResponse(
        id=chat.id,
        question=chat.question,
        answer=chat.answer,
        project_id=chat.project_id
    )

def on_llm_response_question(project_id: int, chat_id: int, new_answer: str, db: dao.SessionLocal):
    print(f"LLM response for question [projectID:{project_id}, chatID:{chat_id}]")
    dao.update_chat_answer(chat_id, new_answer, db)


@app.get("/projects/{project_id}/chats/get_all", response_model=List[ChatResponse])
async def get_chat_history(project_id: int, db: dao.SessionLocal = Depends(dao.get_db)):
    return [
        ChatResponse(
            id=chat.id, 
            question=chat.question, 
            answer=chat.answer, 
            project_id=chat.project_id
        ) 
        for chat in dao.get_all_chats(project_id, db)
    ]


@app.get("/projects/{project_id}/delete", response_model=SimpleResponse)
async def project_delete(project_id: int, db: dao.SessionLocal = Depends(dao.get_db)):
    for chat in dao.get_all_chats(project_id, db):
        dao.chat_delete(chat.id, db)
    dao.project_delete(project_id, db)
    return SimpleResponse(msg=f"Project {project_id} deleted successfully")

@app.get("/chats/{chat_id}/delete", response_model=SimpleResponse)
async def chat_delete(chat_id: int, db: dao.SessionLocal = Depends(dao.get_db)):
    dao.chat_delete(chat_id, db)
    return SimpleResponse(msg=f"Chat {chat_id} deleted successfully")

@app.get("/")
async def root():
    return {"message": "Hello World. Go to /docs for API list"}