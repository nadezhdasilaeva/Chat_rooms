from pydantic import BaseModel, EmailStr
from sqlmodel import Field
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserCreate(BaseModel):
    email: EmailStr = Field(default='Email')  # почта
    phone: PhoneNumber = Field(default='+78005553535')
    name: str = Field(default='Имя')  # имя
    password: str = Field(default='Password')
    complete_password: str = Field(default='Confirm the password')


class UserUpdate(BaseModel):
    email: EmailStr = Field(default='Email')
    phone: PhoneNumber = Field(default='+78005553535')
    password: str = Field(default='Password')
    complete_password: str = Field(default='Confirm the password')


class GetUser(BaseModel):
    email: EmailStr
    name: str


class Email(BaseModel):
    email: str


class CreateNewPassword(BaseModel):
    email: EmailStr = Field(default='Email')
    password: str = Field(default='Password')
    complete_password: str = Field(default='Confirm the password')


class MessageCreate(BaseModel):
    sender_user_id: int
    recipient_user_id: int
    message: str

class ChatCreate(BaseModel):
    title: str
    topic: str

class ChatMessageCreate(BaseModel):
    chat_id: int
    sender_id: int
    message_text: str

