from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional

from app.core.config import settings
from app.db.database import get_db
from app.db import models

import jwt
from jwt.exceptions import InvalidTokenError

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class Authorization():

    @staticmethod
    def hash_password(password: str):
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def generate_creds(data: dict, expires_delta: Optional[timedelta] = None):
        access = data.copy()
        refresh = data.copy()

        access_expire_delta = expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_expire = datetime.now() + access_expire_delta

        refresh_expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        access.update({"exp": access_expire, "type": "access"})
        access_token = jwt.encode(access, SECRET_KEY, algorithm=ALGORITHM)
        refresh.update({"exp": refresh_expire, "type": "refresh"})
        refresh_token = jwt.encode(refresh, SECRET_KEY, algorithm=ALGORITHM)

        return access_token, refresh_token

    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except InvalidTokenError as e:
            raise e
        
    @staticmethod
    def get_current_user(token = Depends(oauth2_scheme), db = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            if email is None:
                raise credentials_exception
        except InvalidTokenError:
            raise credentials_exception

        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None:
            raise credentials_exception
        return user
        
