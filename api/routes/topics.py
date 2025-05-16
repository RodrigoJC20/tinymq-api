from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import get_db, Topic, User, Client
from ..auth import get_current_active_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(
    prefix="/topics",
    tags=["topics"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)

# Pydantic models
class TopicBase(BaseModel):
    name: str
    owner_client_id: str

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Routes
@router.get("/", response_model=List[TopicResponse])
def get_topics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    topics = db.query(Topic).offset(skip).limit(limit).all()
    return topics

@router.get("/{topic_id}", response_model=TopicResponse)
def get_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.delete("/{topic_id}", status_code=204)
def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Delete topic (this will cascade to related records due to FK constraints)
    db.delete(topic)
    db.commit()
    
    return None

@router.get("/by-name/{name}", response_model=TopicResponse)
def get_topic_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    topic = db.query(Topic).filter(Topic.name == name).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.get("/by-client/{client_id}", response_model=List[TopicResponse])
def get_topics_by_client(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if client exists
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get topics owned by client
    topics = db.query(Topic).filter(Topic.owner_client_id == client_id).all()
    return topics 