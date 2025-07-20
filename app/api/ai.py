from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import Authorization
from app.db import schemas, models
from app.db.database import get_db
from app.utils import CRUD, agent

import uuid

router = APIRouter()

@router.post("/initiate-research", status_code=status.HTTP_201_CREATED, tags=["AI"])
def initiate_research(data: schemas.AnalystCreate, db = Depends(get_db), current_user = Depends(Authorization.get_current_user)):

    try:
        if data.session_id is not None:
            if not data.topic or not data.analyst_number:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing inputs."
                )
            res = agent.generate_analyst(data.analyst_number, data.topic, data.session_id)

            return res
        
        elif data.session_id is None:
            if not data.topic or not data.analyst_number:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing inputs."
                )
            data.session_id = str(uuid.uuid4())
            res = agent.generate_analyst(data.analyst_number, data.topic, data.session_id)

            return {"resault":res, "session_id": data.session_id}

    except HTTPException as e:
        raise e
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    #         detail=f"detail: {e}"
    #     )
    
@router.post("/research-analyst-feedback", status_code=status.HTTP_200_OK, tags=["AI"])
def analyst_feedback(data: schemas.AnalystFeedback, db = Depends(get_db), current_user = Depends(Authorization.get_current_user)):

    try:
        res, topic, session_name, token_usage = agent.analyst_human_feedback(data.feedback, data.session_id)
        if data.feedback == "approve":
            chat_data = schemas.ChatHistoryCreate(
                session_id=data.session_id,
                session_name=session_name,
                message=topic,
                response=res
            )
            CRUD.ChatHistory.create(db, chat_data, current_user)

        return res, token_usage

    except HTTPException as e:
        raise e
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    #         detail=f"detail: {e}"
    #     )