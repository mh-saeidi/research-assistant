from fastapi import Form
from pydantic import BaseModel
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from enum import Enum

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