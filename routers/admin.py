from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from config import PASS_ADMIN, EMAIL_ADMIN
from db import get_session
from models import User
from schemas import GetUserForAdmin
from utils import hash_password, verify_access_token


router = APIRouter(prefix='/admin', tags=['admin'],
                   responses={404: {"description": "Not found"}})


@router.post('/create_first_admin/')
def create_admin(session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.role == 'super_user')).first():
        raise HTTPException(status_code=400)
    hash_pass = hash_password(PASS_ADMIN)
    user = User(email=EMAIL_ADMIN,
                hash_password=hash_pass,
                name='admin',
                phone='+7 (800) 055-65-35',
                )
    user.super_user()
    session.add(user)
    session.commit()
    raise HTTPException(status_code=201)


@router.get('/get_all_user/', response_model=List[GetUserForAdmin])
def get_all_user(user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if user.role != 'super_user':
        raise HTTPException(status_code=403)
    users = session.exec(select(User)).all()
    return users


@router.put('/BAN_user/{user_id}')
def get_no_verify_user(user_id: int, su_user: User = Depends(verify_access_token),
                       session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.role == 'BAN':
        raise HTTPException(status_code=400, detail='The user has already been blocked')
    user.ban_user()
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)


@router.put('/un_BAN_user/{user_id}')
def get_no_verify_user(user_id: int, su_user: User = Depends(verify_access_token),
                       session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.role != 'BAN':
        raise HTTPException(status_code=400, detail='The user is not blocked')
    user.user_user()
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)