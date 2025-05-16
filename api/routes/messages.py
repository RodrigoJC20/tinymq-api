from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
from ..models import get_db, MessageLog, User, Client, Topic
from ..auth import get_current_active_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(
    prefix="/messages",
    tags=["messages"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)

# Pydantic models
class MessageLogBase(BaseModel):
    publisher_client_id: str
    topic_id: int
    payload_size: int
    payload_preview: Optional[str] = None
    payload_data: Optional[Dict[str, Any]] = None

class MessageLogCreate(MessageLogBase):
    pass

class MessageLogResponse(MessageLogBase):
    id: int
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MessageLogDetail(MessageLogResponse):
    topic_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# Routes
@router.get("/", response_model=List[MessageLogDetail])
def get_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    messages = db.query(MessageLog).options(
        joinedload(MessageLog.topic)
    ).order_by(MessageLog.published_at.desc()).offset(skip).limit(limit).all()
    
    # Manually add topic_name to response
    result = []
    for msg in messages:
        msg_dict = MessageLogResponse.model_validate(msg).model_dump()
        msg_dict["topic_name"] = msg.topic.name if msg.topic else None
        result.append(msg_dict)
    
    return result

@router.get("/{message_id}", response_model=MessageLogDetail)
def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    message = db.query(MessageLog).options(
        joinedload(MessageLog.topic)
    ).filter(MessageLog.id == message_id).first()
    
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Manually add topic_name to response
    msg_dict = MessageLogResponse.model_validate(message).model_dump()
    msg_dict["topic_name"] = message.topic.name if message.topic else None
    
    return msg_dict

@router.delete("/{message_id}", status_code=204)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    message = db.query(MessageLog).filter(MessageLog.id == message_id).first()
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    
    db.delete(message)
    db.commit()
    
    return None

@router.get("/by-client/{client_id}", response_model=List[MessageLogDetail])
def get_messages_by_client(
    client_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if client exists
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get messages published by client
    messages = db.query(MessageLog).options(
        joinedload(MessageLog.topic)
    ).filter(
        MessageLog.publisher_client_id == client_id
    ).order_by(
        MessageLog.published_at.desc()
    ).offset(skip).limit(limit).all()
    
    # Manually add topic_name to response
    result = []
    for msg in messages:
        msg_dict = MessageLogResponse.model_validate(msg).model_dump()
        msg_dict["topic_name"] = msg.topic.name if msg.topic else None
        result.append(msg_dict)
    
    return result

@router.get("/by-topic/{topic_id}", response_model=List[MessageLogDetail])
def get_messages_by_topic(
    topic_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if topic exists
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get messages for topic
    messages = db.query(MessageLog).options(
        joinedload(MessageLog.topic)
    ).filter(
        MessageLog.topic_id == topic_id
    ).order_by(
        MessageLog.published_at.desc()
    ).offset(skip).limit(limit).all()
    
    # Manually add topic_name to response
    result = []
    for msg in messages:
        msg_dict = MessageLogResponse.model_validate(msg).model_dump()
        msg_dict["topic_name"] = msg.topic.name if msg.topic else None
        result.append(msg_dict)
    
    return result 