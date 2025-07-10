from fastapi import APIRouter, WebSocket, Depends, HTTPException
from typing import Dict
from datetime import datetime
from sqlmodel import Session

from schemas import ChatCreate
from db import get_session
from models import Chat


router = APIRouter(tags=['chat'],
                   responses={404: {"description": "Not found"}})


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: int, client_id: int):
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = {}
        self.active_connections[chat_id][client_id] = websocket

    def disconnect(self, websocket: WebSocket, chat_id: int, client_id: int):
        if chat_id in self.active_connections and client_id in self.active_connections[chat_id]:
            del self.active_connections[chat_id][client_id]
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, chat_id: int, sender_id: int, sender_name: str, timestamp: datetime):
        if chat_id in self.active_connections:
            for client_id, connection in self.active_connections[chat_id].items():
                message_with_class = {
                    "text": message,
                    "is_self": client_id == sender_id,
                    "sender_name": sender_name,
                    "timestamp": timestamp.isoformat()
                }
                await connection.send_json(message_with_class)

manager = ConnectionManager()


@router.post("/add_chat")
def add_chat(data: ChatCreate, session: Session = Depends(get_session)):
    chat = Chat(title=data.title,
                topic=data.topic)
    session.add(chat)
    session.commit()
    raise HTTPException(status_code=200)
