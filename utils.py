from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jwt import encode, decode, PyJWTError
from sqlmodel import select, Session
from datetime import timedelta, datetime
from hashlib import sha256
from cryptography.fernet import Fernet

from config import SECRET_KEY, ALGORITHM, ENCRYPTION_KEY
from db import get_session
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_error = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}, )


def create_access_token(data: dict, exp: timedelta = None):
    to_encode = data.copy()
    if exp:
        expire = datetime.utcnow() + exp
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_error
        user = session.exec(select(User).where(User.id == user_id)).first()
        if user is None:
            raise credentials_error
        return user
    except PyJWTError as e:
        if "Signature has expired" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        raise credentials_error


def hash_password(password: str):
    return sha256(password.encode()).hexdigest()


key = Fernet.generate_key()
print(key.decode())

fernet = Fernet(ENCRYPTION_KEY)

def encrypt_message(message: str) -> bytes:
    return fernet.encrypt(message.encode('utf-8'))

def decrypt_message(encrypted_message: bytes) -> str:
    return fernet.decrypt(encrypted_message).decode('utf-8')
