from fastapi import APIRouter, Request, Depends, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from jwt import decode
from sqlmodel import Session, select
from datetime import datetime

from config import SECRET_KEY, ALGORITHM
from models import User, Chat, ChatMessage
from db import get_session
from routers.chat import manager
from utils import encrypt_message, decrypt_message


templates = Jinja2Templates(directory='templates')
router = APIRouter(include_in_schema=False)


@router.websocket("/ws/{chat_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, client_id: int, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.id == client_id)).first()
    if not user:
        await websocket.close(code=1008, reason="Пользователь не найден!")
        return
    username = user.name
    user_id = user.id
    await manager.connect(websocket, chat_id, client_id)
    await manager.broadcast(f"Присоединился к чату.", chat_id, user_id, username, datetime.utcnow())

    try:
        while True:
            data = await websocket.receive_text()
            encrypted_message = encrypt_message(data)
            chat_message = ChatMessage(
                chat_id=chat_id, 
                sender_id=user_id, 
                message_text=encrypted_message
            )
            db.add(chat_message)
            db.commit()
            db.refresh(chat_message)
            await manager.broadcast(data, chat_id, user_id, username, chat_message.timestamp)

    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_id, client_id)
        await manager.broadcast(f"Покинул чат", chat_id, user_id, username, datetime.utcnow())

@router.get("/join_chat/{chat_id}", response_class=HTMLResponse)
async def join_chat(request: Request, chat_id: int, db: Session=Depends(get_session)):
    token = request.cookies.get("access_token")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    scheme, _, param = token.partition(" ")
    payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
    client_id = payload.get("sub")
    user = db.exec(select(User).where(User.id == client_id)).first()
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    
    messages = db.exec(select(ChatMessage).where(ChatMessage.chat_id == chat_id).order_by(ChatMessage.timestamp)).all()
    
    decrypted_messages = []
    for msg in messages:
        decrypted_text = decrypt_message(msg.message_text)
        decrypted_messages.append({
            "id": msg.id,
            "chat_id": msg.chat_id,
            "sender_id": msg.sender_id,
            "message_text": decrypted_text,
            "timestamp": msg.timestamp,
            "sender": msg.sender
        })
    
    return templates.TemplateResponse("chat.html", {
        "request": request, 
        "chat": chat, 
        "user": user, 
        "messages": decrypted_messages
    })
