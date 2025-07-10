from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from hashlib import sha256


class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    hash_password: str
    role: str = Field(default='user')
    email: str
    phone: str
    name: str
    date_reg: datetime = Field(default=datetime.utcnow())

    # Добавляем связь с ChatMessage
    sent_messages: List["ChatMessage"] = Relationship(back_populates="sender")

    def verify_password(self, password: str):
        return self.hash_password == sha256(password.encode()).hexdigest()

    def ban_user(self):
        self.role = 'BAN'

    def super_user(self):
        self.role = 'super_user'

    def user_user(self):
        self.role = 'user'


# class Message(SQLModel, table=True):
#     id: Optional[int] = Field(primary_key=True, default=None)
#     sender_user_id: int = Field(foreign_key='user.id')
#     recipient_user_id: int = Field(foreign_key='user.id')
#     enc_message: bytes
#     date_create: datetime = Field(default=datetime.utcnow())
#     date_last_update: datetime = Field(default=datetime.utcnow())
#     changed: bool = Field(default=False)


class Chat(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    title: str
    topic: str
    date_reg: datetime = Field(default=datetime.utcnow())

    # Добавляем связь с ChatMessage
    messages: List["ChatMessage"] = Relationship(back_populates="chat")


class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    chat_id: int = Field(foreign_key="chat.id")
    sender_id: int = Field(foreign_key="user.id")
    message_text: bytes  # Теперь храним бинарные данные
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    chat: Chat = Relationship(back_populates="messages")
    sender: User = Relationship(back_populates="sent_messages")

    def decrypted_text(self) -> str:
        from utils import decrypt_message
        return decrypt_message(self.message_text)