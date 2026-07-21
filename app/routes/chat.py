from fastapi import APIRouter
from app.chatbot import chatbot
from app.models.chat import ChatRequest

router = APIRouter()

@router.post("/chat")
def chat(data: ChatRequest):
    reply = chatbot(data.message)
    return {
        "reply": reply
    }