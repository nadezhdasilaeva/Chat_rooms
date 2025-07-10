from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from jwt import decode

from models import User
from db import get_session
from config import SECRET_KEY, ALGORITHM



router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/account")
def account(request: Request, db: Session = Depends(get_session)):
    token = request.cookies.get("access_token")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    else:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        return templates.TemplateResponse("account.html", {"request": request, "user": user})


@router.get("/edit_account")
def edit_account(request: Request, db: Session = Depends(get_session)):
    token = request.cookies.get("access_token")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    else:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        return templates.TemplateResponse("edit_account.html", {"request": request, "user": user})


@router.post("/edit_account")
async def update_account(request: Request, db: Session = Depends(get_session)):
    form_data = await request.form()
    token = request.cookies.get("access_token")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    else:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        
        new_name = form_data.get("name")
        new_email = form_data.get("email")
        new_phone = form_data.get("phone")


        duplicate_email = db.exec(select(User).where(User.email == new_email).where(User.id != id)).first()
        if duplicate_email:
            errors = ["Email уже занят другим пользователем."]
            return templates.TemplateResponse("edit_account.html", {"request": request, "user": user, "errors": errors})


        duplicate_phone = db.exec(select(User).where(User.phone == new_phone).where(User.id != id)).first()
        if duplicate_phone:
            errors = ["Телефон уже занят другим пользователем."]
            return templates.TemplateResponse("edit_account.html", {"request": request, "user": user, "errors": errors})


        user.name = new_name
        user.email = new_email
        user.phone = new_phone
        db.commit()

        return RedirectResponse(url="/account", status_code=302)