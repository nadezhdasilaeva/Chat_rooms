from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from sqlmodel import Session, select
from jwt import decode
from typing import Optional

from models import User
from db import get_session
from config import SECRET_KEY, ALGORITHM


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/all_users")
def all_users(request: Request, db: Session=Depends(get_session)):
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if token and (role == "super_user"):
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        users = db.query(User).all()
        return templates.TemplateResponse("all_users.html", {"request": request, "users": users, "user": user})
    if token and (not role == "super_user"):
        response = RedirectResponse(url="/home", status_code=302)
        return response
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response


@router.post("/BAN_user/{id}")
def BAN_user(request: Request, id: int, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    if role != "super_user":
        response = RedirectResponse(url="/home", status_code=302)
        return response
    user = db.exec(select(User).where(User.id == id)).first()
    if not user:
        errors.append("Пользователь не найден")
        return templates.TemplateResponse("all_users.html", {"request": request, "errors": errors, "user": user})
    user.ban_user()
    db.add(user)
    db.commit()
    db.refresh(user)
    users = db.query(User).all()
    response = RedirectResponse(url="/all_users", status_code=302)
    return response


@router.post("/un_BAN_user/{id}")
def un_BAN_user(request: Request, id: int, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    if role != "super_user":
        response = RedirectResponse(url="/home", status_code=302)
        return response
    user = db.exec(select(User).where(User.id == id)).first()
    if not user:
        errors.append("Пользователь не найден")
        return templates.TemplateResponse("all_users.html", {"request": request, "errors": errors, "user": user})
    user.user_user()
    db.add(user)
    db.commit()
    db.refresh(user)
    users = db.query(User).all()
    response = RedirectResponse(url="/all_users", status_code=302)
    return response


@router.get("/search_all_users")
def search_users(request: Request, query: Optional[str], db: Session = Depends(get_session)):
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    users = db.query(User).filter(User.email.contains(query)).all()
    if token and (role == "super_user"):
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        return templates.TemplateResponse("all_users.html", {"request": request, "users": users, "user": user})
    else:
        response = RedirectResponse(url="/", status_code=302)
        return response