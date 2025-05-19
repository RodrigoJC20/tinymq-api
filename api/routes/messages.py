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
    # Use explicit column selection to avoid columns that might not exist in the database
    messages = db.query(
        MessageLog.id,
        MessageLog.publisher_client_id,
        MessageLog.topic_id,
        MessageLog.payload_size,
        MessageLog.payload_preview,
        MessageLog.published_at,
        Topic.name.label('topic_name')
    ).join(
        Topic, MessageLog.topic_id == Topic.id, isouter=True
    ).order_by(
        MessageLog.published_at.desc()
    ).offset(skip).limit(limit).all()
    
    # Convert query results to dictionaries
    result = []
    for msg in messages:
        msg_dict = {
            "id": msg.id,
            "publisher_client_id": msg.publisher_client_id,
            "topic_id": msg.topic_id,
            "payload_size": msg.payload_size,
            "payload_preview": msg.payload_preview,
            "payload_data": None,  # Set to None since it doesn't exist in DB
            "published_at": msg.published_at,
            "topic_name": msg.topic_name
        }
        result.append(msg_dict)
    
    return result

@router.get("/{message_id}", response_model=MessageLogDetail)
def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Use explicit column selection to avoid columns that might not exist in the database
    message = db.query(
        MessageLog.id,
        MessageLog.publisher_client_id,
        MessageLog.topic_id,
        MessageLog.payload_size,
        MessageLog.payload_preview,
        MessageLog.published_at,
        Topic.name.label('topic_name')
    ).join(
        Topic, MessageLog.topic_id == Topic.id, isouter=True
    ).filter(
        MessageLog.id == message_id
    ).first()
    
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    
    msg_dict = {
        "id": message.id,
        "publisher_client_id": message.publisher_client_id,
        "topic_id": message.topic_id,
        "payload_size": message.payload_size,
        "payload_preview": message.payload_preview,
        "payload_data": None,  # Set to None since it doesn't exist in DB
        "published_at": message.published_at,
        "topic_name": message.topic_name
    }
    
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
    
    # Get messages published by client using explicit column selection
    messages = db.query(
        MessageLog.id,
        MessageLog.publisher_client_id,
        MessageLog.topic_id,
        MessageLog.payload_size,
        MessageLog.payload_preview,
        MessageLog.published_at,
        Topic.name.label('topic_name')
    ).join(
        Topic, MessageLog.topic_id == Topic.id, isouter=True
    ).filter(
        MessageLog.publisher_client_id == client_id
    ).order_by(
        MessageLog.published_at.desc()
    ).offset(skip).limit(limit).all()
    
    # Convert query results to dictionaries
    result = []
    for msg in messages:
        msg_dict = {
            "id": msg.id,
            "publisher_client_id": msg.publisher_client_id,
            "topic_id": msg.topic_id,
            "payload_size": msg.payload_size,
            "payload_preview": msg.payload_preview,
            "payload_data": None,  # Set to None since it doesn't exist in DB
            "published_at": msg.published_at,
            "topic_name": msg.topic_name
        }
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
    
    # Get messages for topic using explicit column selection
    messages = db.query(
        MessageLog.id,
        MessageLog.publisher_client_id,
        MessageLog.topic_id,
        MessageLog.payload_size,
        MessageLog.payload_preview,
        MessageLog.published_at,
        Topic.name.label('topic_name')
    ).join(
        Topic, MessageLog.topic_id == Topic.id, isouter=True
    ).filter(
        MessageLog.topic_id == topic_id
    ).order_by(
        MessageLog.published_at.desc()
    ).offset(skip).limit(limit).all()
    
    # Convert query results to dictionaries
    result = []
    for msg in messages:
        msg_dict = {
            "id": msg.id,
            "publisher_client_id": msg.publisher_client_id,
            "topic_id": msg.topic_id,
            "payload_size": msg.payload_size,
            "payload_preview": msg.payload_preview,
            "payload_data": None,  # Set to None since it doesn't exist in DB
            "published_at": msg.published_at,
            "topic_name": msg.topic_name
        }
        result.append(msg_dict)
    
    return result 