from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..models import get_db, ConnectionEvent, User, Client
from ..auth import get_current_active_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(
    prefix="/events",
    tags=["connection events"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)

# Pydantic models
class ConnectionEventBase(BaseModel):
    client_id: str
    event_type: str
    ip_address: Optional[str] = None
    port: Optional[int] = None

class ConnectionEventResponse(ConnectionEventBase):
    id: int
    timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ClientResponse(BaseModel):
    id: int
    client_id: str
    last_connected: Optional[datetime] = None
    last_ip: Optional[str] = None
    last_port: Optional[int] = None
    connection_count: int = 0

    class Config:
        from_attributes = True

# Routes
@router.get("/", response_model=List[ConnectionEventResponse])
def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    event_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(ConnectionEvent).order_by(ConnectionEvent.timestamp.desc())
    
    if event_type:
        query = query.filter(ConnectionEvent.event_type == event_type)
    
    events = query.offset(skip).limit(limit).all()
    return events

@router.get("/{event_id}", response_model=ConnectionEventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    event = db.query(ConnectionEvent).filter(ConnectionEvent.id == event_id).first()
    
    if event is None:
        raise HTTPException(status_code=404, detail="Connection event not found")
    
    return event

@router.delete("/{event_id}", status_code=204)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    event = db.query(ConnectionEvent).filter(ConnectionEvent.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Connection event not found")
    
    db.delete(event)
    db.commit()
    
    return None

@router.get("/by-client/{client_id}", response_model=List[ConnectionEventResponse])
def get_events_by_client(
    client_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    event_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if client exists
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get events for client
    query = db.query(ConnectionEvent).filter(
        ConnectionEvent.client_id == client_id
    ).order_by(ConnectionEvent.timestamp.desc())
    
    if event_type:
        query = query.filter(ConnectionEvent.event_type == event_type)
        
    events = query.offset(skip).limit(limit).all()
    
    return events

@router.get("/{event_id}/client", response_model=ClientResponse)
def get_client_by_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    event = db.query(ConnectionEvent).filter(ConnectionEvent.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    client = db.query(Client).filter(Client.client_id == event.client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return client

@router.get("/{client_id}/all-events", response_model=List[ConnectionEventResponse])
def get_all_events_by_client(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    events = db.query(ConnectionEvent).filter(ConnectionEvent.client_id == client_id).order_by(ConnectionEvent.timestamp.desc()).all()
    return events