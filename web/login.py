from fastapi import APIRouter, Request, Depends, responses, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from db import get_session
from models import User
from utils import create_access_token, hash_password


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/login")
def login(request: Request):
    access_token = request.cookies.get("access_token")
    if access_token:
        return RedirectResponse(url="/home", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_session)):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    errors = []
    if len(password) < 6:
        errors.append("Пароль должен состоять от 6 и более символов!")
        return templates.TemplateResponse("login.html", {"request": request, "errors": errors})
    user = db.exec(select(User).where(User.email == email)).first()
    if not user or not user.verify_password(password):
        errors.append("Неверны почта или пароль!")
        return templates.TemplateResponse("login.html", {"request": request, "errors": errors})
    if user.role == "BAN":
        errors.append("Пользователь заблокирован!")
        return templates.TemplateResponse("login.html", {"request": request, "errors": errors})
    else:
        access_token = create_access_token(data={"sub": user.id})
        response = RedirectResponse(url="/home", status_code=302)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        response.set_cookie(key="role", value=user.role, httponly=True)
        return response
        return response


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="role")
    return response


@router.get("/create_new_password")
def create_new_password(request: Request):
    return templates.TemplateResponse("create_new_password.html", {"request": request})


@router.post("/create_new_password")
async def create_new_password(request: Request, db: Session = Depends(get_session)):
    errors = []
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    complete_password = form.get("complete_password")
    user = db.exec(select(User).where(User.email == email)).first()
    if not user:
        errors.append("Пользователь не найден!")
        return templates.TemplateResponse("create_new_password.html", {"request": request, "errors": errors})
    if password != complete_password:
        errors.append("Некорректный пароль")
        return templates.TemplateResponse("create_new_password.html", {"request": request, "errors": errors})
    user.sqlmodel_update({'hash_password': hash_password(password)})
    db.add(user)
    db.commit()
    db.refresh(user)
    return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
