from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import Authorization
from app.db import schemas, models
from app.db.database import get_db
from app.utils import CRUD

from typing import List

router = APIRouter()

@router.post("/signin", status_code=status.HTTP_201_CREATED, tags=["Users"])
def signin(data: schemas.UserCreate, db = Depends(get_db)):

    try:
        existing_user = db.query(models.User).filter((models.User.email == data.email.lower())).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        new_user = CRUD.User.create(db, data)
        access_token, refresh_token = Authorization.generate_creds(data = {"sub" : new_user.email})

        return {"access_token" : access_token, "refresh_token" : refresh_token}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"detail: {e}"
        )
    
@router.post("/signup", status_code=status.HTTP_200_OK, tags=["Users"])
def signup(data: schemas.UserSignup, db = Depends(get_db)):

    try:
        user = db.query(models.User).filter(models.User.email == data.email.lower()).first()
        if not user or not Authorization.verify_password(data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email or password."
            )

        if Authorization.verify_password(data.password, user.password):
            access_token, refresh_token = Authorization.generate_creds(data={"sub": user.email})

            return {"access_token": access_token, "refresh_tokken": refresh_token}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"detail: {e}"
        )
    
@router.get("/get-sessions", status_code=status.HTTP_200_OK, tags=["Users"])
def get_sessions(db = Depends(get_db), current_user = Depends(Authorization.get_current_user)):

    try:
        sessions = CRUD.ChatHistory.get_sessions(db, current_user.id)
        if not sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No sessions found."
            )
        return {"sessions": sessions}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"detail: {e}"
        )
    
@router.get("/get-session-history/{session_id}", response_model=List[schemas.SessionHistoryResponse], tags=["Users"])
def get_session_history(session_id: str, db = Depends(get_db), current_user = Depends(Authorization.get_current_user)):

    try:
        session_history = CRUD.ChatHistory.get_session_history(db, session_id)
        if not session_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session history not found."
            )
        return session_history

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"detail: {e}"
        )