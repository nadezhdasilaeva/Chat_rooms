from fastapi import FastAPI
import uvicorn
from sqlmodel import SQLModel

from db import engine
from routers import chat, user

from web import input as web_input
from web import register as web_register
from web import login as web_login
from web import chat as web_chat
from web import users as web_users


if __name__ == '__main__':
    SQLModel.metadata.create_all(engine)

app = FastAPI()


app.include_router(user.router)
app.include_router(chat.router)


app.include_router(web_input.router)
app.include_router(web_register.router)
app.include_router(web_login.router)
app.include_router(web_chat.router)
app.include_router(web_users.router)


if __name__ == '__main__':
    uvicorn.run(app, port=8001)