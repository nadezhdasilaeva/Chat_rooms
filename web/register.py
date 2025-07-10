from datetime import datetime
from fastapi import APIRouter, Request, Depends, responses, status
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from db import get_session
from models import User
from utils import  hash_password

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get('/register')
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post('/register')
async def register_user(request: Request, db: Session = Depends(get_session)):
    form = await request.form()
    name = form.get('name')
    email = form.get("email")
    password = form.get("password")
    phone = form.get("phone")
    complete_password = form.get("complete_password")

    errors = []
    if len(password) < 6:
        errors.append('Пароль должен состоять от 6 и более символов!')
    if password != complete_password:
        errors.append("Неверное повторение пароля!")

    if errors:
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors})


    duplicate_email = db.exec(select(User).where(User.email == email)).first()
    if duplicate_email:
        errors.append("Email уже занят")


    duplicate_phone = db.exec(select(User).where(User.phone == phone)).first()
    if duplicate_phone:
        errors.append("Телефон уже занят")

    if errors:
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors})

    user = User(
        email=email,
        phone=phone,
        name=name,
        hash_password=hash_password(password),
        role='user',
        date_reg=datetime.utcnow()
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    msg = 'Вы зарегистрированы! Войдите в аккаунт!'
    return templates.TemplateResponse("register.html", {"request": request, "msg": msg})