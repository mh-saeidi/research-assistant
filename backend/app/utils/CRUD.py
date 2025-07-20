from app.core.auth import Authorization
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db import models, schemas
from datetime import datetime
import os
from pathlib import Path

class User:

    @staticmethod
    def create(db: Session, data: schemas.UserCreate):
        user_data = data.model_dump()
        user_data["email"]= user_data["email"].lower()
        user_data.pop("password")

        hashed_password = Authorization.hash_password(data.password)
        new_user = models.User(**user_data, password=hashed_password)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user
    
class ChatHistory:

    @staticmethod
    def create(db: Session, data: schemas.ChatHistoryCreate, current_user: models.User):
        chat_data = data.model_dump()
        chat_data["user_id"] = current_user.id

        new_chat = models.ChatHistory(**chat_data)

        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

        return new_chat

    @staticmethod
    def get_sessions(db: Session, user_id: int):
        sessions = db.query(models.ChatHistory).filter(models.ChatHistory.user_id == user_id).all()
        session_dict = {}
        for session in sessions:
            if session.session_id not in session_dict.keys():
                session_dict[session.session_id] = {
                    "session_name": session.session_name,
                    "session_id": session.session_id,
                    "created_at": session.created_at
                }
        sessions = sorted(session_dict.values(), key=lambda x: x["created_at"], reverse=True)
        return sessions
    
    @staticmethod
    def get_session_history(db: Session, session_id: str):
        session_history = db.query(models.ChatHistory).filter(models.ChatHistory.session_id == session_id).all()
        if not session_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session history not found."
            )
        return session_history
