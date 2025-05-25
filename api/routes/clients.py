from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import get_db, Client, User, Subscription, MessageLog, ConnectionEvent
from ..auth import get_current_active_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for data validation and serialization
class ClientBase(BaseModel):
    client_id: str
    last_ip: Optional[str] = None
    last_port: Optional[int] = None

class ClientCreate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: int
    last_connected: Optional[datetime] = None
    connection_count: int = 0

    class Config:
        from_attributes = True

class SubscriptionResponse(BaseModel):
    id: int
    client_id: str
    topic_id: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class MessageLogResponse(BaseModel):
    id: int
    client_id: str
    topic_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConnectionEventResponse(BaseModel):
    id: int
    client_id: str
    event_type: str
    timestamp: datetime

    class Config:
        from_attributes = True

# Routes
@router.get("/", response_model=List[ClientResponse])
def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    clients = db.query(Client).offset(skip).limit(limit).all()
    return clients

@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.delete("/{client_id}", status_code=204)
def delete_client(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Delete client (this will cascade to related records due to FK constraints)
    db.delete(client)
    db.commit()
    
    return None

@router.get("/{client_id}/subscriptions", response_model=List[SubscriptionResponse])
def get_subscriptions_by_client(
    client_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    subscriptions = db.query(Subscription).filter(Subscription.client_id == client_id).offset(skip).limit(limit).all()
    return subscriptions

@router.get("/{client_id}/messages", response_model=List[MessageLogResponse])
def get_messages_by_client(
    client_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    messages = db.query(MessageLog).filter(MessageLog.client_id == client_id).offset(skip).limit(limit).all()
    return messages

@router.get("/{client_id}/events", response_model=List[ConnectionEventResponse])
def get_events_by_client(
    client_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    events = db.query(ConnectionEvent).filter(ConnectionEvent.client_id == client_id).offset(skip).limit(limit).all()
    return events