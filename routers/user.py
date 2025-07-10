from fastapi import APIRouter, HTTPException, Response, Depends
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordRequestForm

from db import get_session
from models import User
from utils import create_access_token, hash_password, verify_access_token
from schemas import UserCreate, UserUpdate, CreateNewPassword, GetUser


router = APIRouter(tags=['user'],
                   responses={404: {"description": "Not found"}})


@router.post('/login/')
async def login_user(response: Response,
                     session: Session = Depends(get_session),
                     data: OAuth2PasswordRequestForm = Depends()
                     ):
    user = session.exec(select(User).where(
        User.email == data.username)).first()  # так как нет username как такогого, мы будем использовать email
    if not user or not user.verify_password(data.password):
        raise HTTPException(status_code=401,
                            detail='Incorrect email or password',
                            headers={"WWW-Authenticate": "Bearer"}
                            )
    access_token = create_access_token(data={"sub": str(user.id)})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post('/register/')
def reg_user(user: UserCreate,
             session: Session = Depends(get_session)
            ):
    temp_user = session.exec(select(User).where(User.email == user.email)).first()
    if temp_user:
        raise HTTPException(status_code=400,
                            detail='Email is busy')
    if user.password != user.complete_password:
        raise HTTPException(status_code=401, detail='Incorrect password')
    if session.exec(select(User).where(User.phone == user.phone)).first():
        raise HTTPException(status_code=400, detail='Phone is busy')
    hashed_password = hash_password(user.password)
    db_user = User(email=user.email,
                   phone=user.phone,
                   hash_password=hashed_password,
                   name=user.name,
                   )
    session.add(db_user)
    session.commit()
    raise HTTPException(status_code=201)


@router.post('/token')
def login_user_for_token(response: Response,
                         session: Session = Depends(get_session),
                         data: OAuth2PasswordRequestForm = Depends()
                         ):
    user = session.exec(select(User).where(
        User.email == data.username)).first()  # так как нет username как такогого, мы будем использовать email
    if not user or not user.verify_password(data.password):
        raise HTTPException(status_code=401,
                            detail='Incorrect email or password',
                            headers={"WWW-Authenticate": "Bearer"}
                            )
    access_token = create_access_token(data={"sub": str(user.id)})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


@router.put('/update/')
def update_user_data(data: UserUpdate,
                     session: Session = Depends(get_session),
                     user: User = Depends(verify_access_token)
                     ):
    if session.exec(select(User).where(User.email == data.email)).first() and session.exec(
            select(User).where(User.email == data.email)).first().id != user.id:
        raise HTTPException(status_code=400, detail='Email is busy')
    if data.password != data.complete_password:
        raise HTTPException(status_code=401, detail='Incorrect password')
    if session.exec(select(User).where(User.phone == data.phone)).first() and session.exec(
            select(User).where(User.email == data.email)).first().id != user.id:
        raise HTTPException(status_code=400, detail='Phone is busy')
    user.email = data.email
    user.phone = data.phone
    user.hash_password = hash_password(data.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)


@router.put('/create_new_password/')
def create_new_password(data: CreateNewPassword, session: Session = Depends(get_session)):
    temp_user = session.exec(select(User).where(User.email == data.email)).first()
    if not temp_user:
        raise HTTPException(status_code=400, detail='Incorrect email')
    if data.password != data.complete_password:
        raise HTTPException(status_code=401, detail='Incorrect password')
    temp_user.sqlmodel_update({'hash_password': hash_password(data.password)})
    session.add(temp_user)
    session.commit()
    session.refresh(temp_user)
    raise HTTPException(status_code=200)


@router.get('/me/', response_model=GetUser)
def user_me(user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if not session.exec(select(User).where(User.id == user.id)).first():
        raise HTTPException(status_code=404)
    return user