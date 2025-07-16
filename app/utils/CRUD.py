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

# def get_user_by_id(db: Session, user_id: int):
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if not user:
#         raise Exception("User not found!")
#     return user

# def update_user(db: Session, user_id: int, user_update):
#     db_user = db.query(models.User).filter(models.User.id == user_id).first()
#     if not db_user:
#         raise Exception("User not found!")

#     for key, value in user_update.model_dump(exclude_unset=True).items():
#         if value is not None:
#             if key == "password":
#                 value = hash_password(value)
#             setattr(db_user, key, value)

#     db.commit()
#     db.refresh(db_user)
#     return db_user

# def delete_user(db: Session, user_id: int):
#     try:
#         db_user = db.query(models.User).filter(models.User.id == user_id).first()
#         if not db_user:
#             raise Exception("User not found!")
#         if db_user.profile_picture and db_user.profile_picture != "static/profile_pictures/default.png" and db_user.profile_picture is not None:
#                 picture_path = Path(db_user.profile_picture)  # Extract the path to the image file
#                 if picture_path.exists():
#                     os.remove(picture_path)
#         db.delete(db_user)
#         db.commit()
#     except Exception as e:
#         db.rollback()
#         raise Exception(f"{e}")
    
# def add_token_usage(document, db: Session, user_id: int):
#     try:
#         db_user = db.query(models.UserTokenUsage).filter(models.UserTokenUsage.user_id == user_id).first()
#         if not db_user:
#             new_token_entry = models.UserTokenUsage(
#             user_id=user_id,
#             chat_prompt_tokens=int(document["chat_prompt_tokens"]),
#             chat_completion_tokens=int(document["chat_completion_tokens"]),
#             chat_total_tokens=int(document["chat_total_tokens"]),
#             chat_total_cost=float(document["chat_total_cost"]),
#             session_name_prompt_tokens=int(document["session_name_prompt_tokens"]),
#             session_name_completion_tokens=int(document["session_name_completion_tokens"]),
#             session_name_total_tokens=int(document["session_name_total_tokens"]),
#             session_name_cost=float(document["session_name_cost"]),
#             )
#             db.add(new_token_entry)
#             db.commit()
#             db.refresh(new_token_entry)
#         else:
#             db_user.chat_prompt_tokens += int(document["chat_prompt_tokens"])
#             db_user.chat_completion_tokens += int(document["chat_completion_tokens"])
#             db_user.chat_total_tokens += int(document["chat_total_tokens"])
#             db_user.chat_total_cost += float(document["chat_total_cost"])
#             db_user.session_name_prompt_tokens += int(document["session_name_prompt_tokens"])
#             db_user.session_name_completion_tokens += int(document["session_name_completion_tokens"])
#             db_user.session_name_total_tokens += int(document["session_name_total_tokens"])
#             db_user.session_name_cost += float(document["session_name_cost"])
            
#             db.commit()
#             db.refresh(db_user)
#             return db_user
#     except Exception as e:
#         db.rollback()
#         return Exception(f"{e}")
    
# '''
# ADMIN
# '''

# def create_user(db: Session, user: schemas.UserCreate):
#     try:
#         existing_user = (
#             db.query(models.User)
#             .filter((models.User.email == user.email) | (models.User.phone_number == user.phone_number))
#             .first()
#         )
#         if existing_user:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Email or phone number already registered",
#             )

#         user_data = user.model_dump()
#         user_data.pop("password")
#         user_data["profile_picture"] = "default.png"

#         hashed_password = hash_password(user.password)
#         new_user = models.User(**user_data, password=hashed_password)

#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)

#         new_usage = models.UserTokenUsage(user_id=new_user.id)
#         db.add(new_usage)
#         db.commit()
#         db.refresh(new_usage)

#         access_token = create_access_token(data={"sub": new_user.phone_number})
#         refresh_token = create_refresh_token(data={"sub": new_user.phone_number})

#         profile = {}
#         for key, value in user_data.items():
#             profile[key] = value
#         profile["id"] = new_user.id
#         profile["access_token"] = access_token
#         profile["refresh_token"] = refresh_token
#         profile["token_type"] = "bearer"
#         profile["role"] = new_user.role
#         profile["is_active"] = new_user.is_active
#         profile["profile_picture"] = new_user.profile_picture

#         return profile, new_user
#     except HTTPException as e:
#         db.rollback()
#         raise e
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail=f"detail: {e}"
#         )

# class Log():

#     user_mapping = {
#     "first_name": lambda v: f"نام: {v}",
#     "last_name": lambda v: f"نام خانوادگی: {v}",
#     "email": lambda v: f"ایمیل: {v}",
#     "country_code": lambda v: f"کد کشور: {v}",
#     "phone_number": lambda v: f"شماره تماس: {v}",
#     "profile_picture": lambda v: f"عکس پروفایل: {v}",
#     "business_industry": lambda v: f"صنعت کسب و کار: {v}",
#     "role": lambda v: f"نقش: {v}",
#     "is_active": lambda v: f"کاربر فعال: {v}",
#     "password": lambda v: f"رمز عبور: {v}"
#     }

#     @classmethod
#     def create_user(cls, new_user: models.User, creator: models.User, db: Session, request: Request = None):
#         try:
#             ip, device = extract_request_meta(request) if request else (None, None)
#             description = f"کابر با آیدی {new_user.id}، نام: {new_user.first_name} نام خانوادگی: {new_user.last_name} توسط {creator.first_name} {creator.last_name} ایجاد شد."
#             log = models.Log(
#                 user_id = new_user.id,
#                 user_name = new_user.first_name,
#                 user_last_name = new_user.last_name,
#                 user_role = new_user.role,
#                 user_device_type = device,
#                 user_ip = ip,
#                 description = description,
#                 category = models.LogCategory.create
#             )
#             db.add(log)
#             db.commit()
#             db.refresh(log)
#             print(log.description)
#         except Exception as e:
#             db.rollback()
#             raise Exception(f"{e}")
        
#     @classmethod
#     def update_user(cls, user: models.User, creator: models.User, detail: schemas.UserFullUpdate, db: Session, request: Request = None):
#         description = f"اطلاعات کاربر با آیدی {user.id} توسط {creator.first_name} {creator.last_name} بروز شد."
#         extra_parts = [cls.user_mapping[key](value) for key, value in detail.model_dump(exclude_unset=True).items() if key in cls.user_mapping and value is not None]
#         for i, part in enumerate(extra_parts):
#             if part.startswith("رمز عبور:"):
#                 extra_parts[i] = "رمز عبور: True"

#         description = description + (" | " + "، ".join(extra_parts) if extra_parts else "")
#         try:
#             ip, device = extract_request_meta(request) if request else (None, None)
#             log = models.Log(
#                 user_id = user.id,
#                 user_name = user.first_name,
#                 user_last_name = user.last_name,
#                 user_role = user.role,
#                 user_device_type = device,
#                 user_ip = ip,
#                 description = description,
#                 category = models.LogCategory.update
#             )
#             db.add(log)
#             db.commit()
#             db.refresh(log)
#             print(log.description)
#         except Exception as e:
#             db.rollback()
#             raise Exception(f"{e}")
        
#     @classmethod
#     def delete_user(cls, user: models.User, creator: models.User, db: Session, request: Request = None):
#         description = f"کاربر با آیدی {user.id}، نام {user.first_name}، نام خانوادگی {user.last_name} توسط {creator.first_name} {creator.last_name} حذف شد."
#         try:
#             ip, device = extract_request_meta(request) if request else (None, None)
#             log = models.Log(
#                 user_id = user.id,
#                 user_name = user.first_name,
#                 user_last_name = user.last_name,
#                 user_role = user.role,
#                 user_device_type = device,
#                 user_ip = ip,
#                 description = description,
#                 category = models.LogCategory.delete
#             )
#             db.add(log)
#             db.commit()
#             db.refresh(log)
#             print(log.description)
#         except Exception as e:
#             db.rollback()
#             raise Exception(f"{e}")
        
#     @classmethod
#     def delete_chat_history(cls, user: models.User, session_id: str, session_name: str, creator: models.User, db: Session, request: Request = None):
#         description = f"تاریخچه چت {session_name} کاربر {user.id} با آیدی {session_id} توسط {creator.first_name} {creator.last_name} حذف شد."
#         try:
#             ip, device = extract_request_meta(request) if request else (None, None)
#             log = models.Log(
#                 user_id = user.id,
#                 user_name = user.first_name,
#                 user_last_name = user.last_name,
#                 user_role = user.role,
#                 user_device_type = device,
#                 user_ip = ip,
#                 description = description,
#                 category = models.LogCategory.delete
#             )
#             db.add(log)
#             db.commit()
#             db.refresh(log)
#             print(log.description)
#         except Exception as e:
#             db.rollback()
#             raise Exception(f"{e}")
        
#     @classmethod
#     def login_user(cls, user: models.User, db: Session, request: Request = None):
#         description = f"کاربر با آیدی {user.id}، نام {user.first_name}، نام خانوادگی {user.last_name} وارد شد."
#         try:
#             ip, device = extract_request_meta(request) if request else (None, None)
#             log = models.Log(
#                 user_id = user.id,
#                 user_name = user.first_name,
#                 user_last_name = user.last_name,
#                 user_role = user.role,
#                 user_device_type = device,
#                 user_ip = ip,
#                 description = description,
#                 category = models.LogCategory.entry
#             )
#             db.add(log)
#             db.commit()
#             db.refresh(log)
#             print(log.description)
#         except Exception as e:
#             db.rollback()
#             raise Exception(f"{e}")
        
#     @classmethod
#     def signup_user(cls, user: models.User, db: Session, request: Request = None):
#         description = f"کاربر با آیدی {user.id}، نام {user.first_name}، نام خانوادگی {user.last_name} ثبت نام شد."
#         try:
#             ip, device = extract_request_meta(request) if request else (None, None)
#             log = models.Log(
#                 user_id = user.id,
#                 user_name = user.first_name,
#                 user_last_name = user.last_name,
#                 user_role = user.role,
#                 user_device_type = device,
#                 user_ip = ip,
#                 description = description,
#                 category = models.LogCategory.create
#             )
#             db.add(log)
#             db.commit()
#             db.refresh(log)
#             print(log.description)
#         except Exception as e:
#             db.rollback()
#             raise Exception(f"{e}")
        
#     @classmethod
#     def change_phone_user(cls, user: models.User, db: Session, request: Request = None):
#         description = f"شماره تلفن کاربر با آیدی {user.id}، نام {user.first_name}، نام خانوادگی {user.last_name} تغییر یافت."
#         try:
#             ip, device = extract_request_meta(request) if request else (None, None)
#             log = models.Log(
#                 user_id = user.id,
#                 user_name = user.first_name,
#                 user_last_name = user.last_name,
#                 user_role = user.role,
#                 user_device_type = device,
#                 user_ip = ip,
#                 description = description,
#                 category = models.LogCategory.update
#             )
#             db.add(log)
#             db.commit()
#             db.refresh(log)
#             print(log.description)
#         except Exception as e:
#             db.rollback()
#             raise Exception(f"{e}")
        
#     @classmethod
#     def change_email_user(cls, user: models.User, db: Session, request: Request = None):
#         description = f"ایمیل کاربر با آیدی {user.id}، نام {user.first_name}، نام خانوادگی {user.last_name} تغییر یافت."
#         try:
#             ip, device = extract_request_meta(request) if request else (None, None)
#             log = models.Log(
#                 user_id = user.id,
#                 user_name = user.first_name,
#                 user_last_name = user.last_name,
#                 user_role = user.role,
#                 user_device_type = device,
#                 user_ip = ip,
#                 description = description,
#                 category = models.LogCategory.update
#             )
#             db.add(log)
#             db.commit()
#             db.refresh(log)
#             print(log.description)
#         except Exception as e:
#             db.rollback()
#             raise Exception(f"{e}")
        
#     @classmethod
#     def delete_chat_history_user(cls, user: models.User, session_id: str, session_name: str, db: Session, request: Request = None):
#         description = f"تاریخچه چت {session_name} کاربر با آیدی {user.id}، نام {user.first_name}، نام خانوادگی {user.last_name} و آیدی چت {session_id} حذف شد."
#         try:
#             ip, device = extract_request_meta(request) if request else (None, None)
#             log = models.Log(
#                 user_id = user.id,
#                 user_name = user.first_name,
#                 user_last_name = user.last_name,
#                 user_role = user.role,
#                 user_device_type = device,
#                 user_ip = ip,
#                 description = description,
#                 category = models.LogCategory.delete
#             )
#             db.add(log)
#             db.commit()
#             db.refresh(log)
#             print(log.description)
#         except Exception as e:
#             db.rollback()
#             raise Exception(f"{e}")
    
#     @classmethod
#     def read_logs(cls, db: Session, init: int = 0, limit: int = None):
#         if limit:
#             logs = db.query(models.Log).offset(init).limit(limit).all()
#         else:
#             logs = db.query(models.Log).all()
#         return logs