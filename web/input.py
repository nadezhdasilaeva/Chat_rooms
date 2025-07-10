from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jwt import decode, PyJWTError
from sqlmodel import Session, select

from config import SECRET_KEY, ALGORITHM
from models import User, Chat
from db import get_session


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/")
def input(request: Request):
    return templates.TemplateResponse("mainpage.html", {"request": request})


@router.get("/home")
async def home(request: Request, db: Session = Depends(get_session)):
    try:
        token = request.cookies.get("access_token")
        if not token:
            response = RedirectResponse(url="/login?token_expired=true", status_code=302)
            return response
        
        scheme, _, param = token.partition(" ")
        try:
            payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        except PyJWTError as e:
            if "Signature has expired" in str(e):
                response = RedirectResponse(url="/login?token_expired=true", status_code=302)
                response.delete_cookie(key="access_token")
                response.delete_cookie(key="role")
                return response
            # else:
            #     response = RedirectResponse(url="/login?token_expired=true", status_code=302)
            #     response.delete_cookie(key="access_token")
            #     response.delete_cookie(key="role")
            #     return response

        user_id = payload.get("sub")
        user = db.exec(select(User).where(User.id == user_id)).first()

        users = db.exec(select(User)).all()
        chats = db.exec(select(Chat)).all()
        
        return templates.TemplateResponse("homepage.html", {"request": request, "user": user, "users": users, "chats": chats})
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        response = RedirectResponse(url="/login?token_expired=true", status_code=302)
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="role")
        return response
