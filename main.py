from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from teacher_assistant_bot import TeacherAssistant  




app = FastAPI()
ta = TeacherAssistant() 

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask(request: QuestionRequest):
    result = ta.teacher_assitant_(request.question)
    return JSONResponse(content=result)
