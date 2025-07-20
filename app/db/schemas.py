from fastapi import Form
from pydantic import BaseModel
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from enum import Enum
from uuid import UUID

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class UserSignup(BaseModel):
    email: str
    password: str

class AnalystCreate(BaseModel):
    analyst_number: int
    topic: str
    session_id: Optional[str] = None

class AnalystFeedback(BaseModel):
    feedback: str
    session_id: str

class ChatHistoryCreate(BaseModel):
    session_id: str
    session_name: str
    message: str
    response: str

class SessionHistoryResponse(BaseModel):
    id: int
    user_id: int 
    session_id: str
    session_name: str
    message: str
    response: str 
    created_at: datetime

    class Config:
        from_attributes = True