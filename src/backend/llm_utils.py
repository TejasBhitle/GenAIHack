from typing import Callable
import time


def handle_project_init(project_id: int, input_files, db, callback: Callable):
    time.sleep(15) # mock LLM Call

    callback(project_id, db)


def handle_question(project_id, chat_id, question: str, db, callback: Callable):
    time.sleep(10) # mock LLM Call
    
    callback(project_id, chat_id, "Answer from LLM", db)


