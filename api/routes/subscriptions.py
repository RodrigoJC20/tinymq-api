from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..models import get_db, Subscription, User, Client, Topic
from ..auth import get_current_active_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)

# Pydantic models
class SubscriptionBase(BaseModel):
    client_id: str
    topic_id: int
    active: bool = True

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionResponse(SubscriptionBase):
    id: int
    subscribed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SubscriptionDetail(SubscriptionResponse):
    topic_name: Optional[str] = None
    
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

class TopicResponse(BaseModel):
    id: int
    name: str
    owner_client_id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SubscriptionStatusUpdate(BaseModel):
    active: bool

# Routes
@router.get("/", response_model=List[SubscriptionDetail])
def get_subscriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Subscription).options(joinedload(Subscription.topic))
    
    if active_only:
        query = query.filter(Subscription.active == True)
    
    subscriptions = query.offset(skip).limit(limit).all()
    
    # Manually add topic_name to response
    result = []
    for sub in subscriptions:
        sub_dict = SubscriptionResponse.model_validate(sub).model_dump()
        sub_dict["topic_name"] = sub.topic.name if sub.topic else None
        result.append(sub_dict)
    
    return result

@router.get("/{subscription_id}", response_model=SubscriptionDetail)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    subscription = db.query(Subscription).options(
        joinedload(Subscription.topic)
    ).filter(Subscription.id == subscription_id).first()
    
    if subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Manually add topic_name to response
    sub_dict = SubscriptionResponse.model_validate(subscription).model_dump()
    sub_dict["topic_name"] = subscription.topic.name if subscription.topic else None
    
    return sub_dict

@router.delete("/{subscription_id}", status_code=204)
def delete_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    db.delete(subscription)
    db.commit()
    
    return None

@router.get("/by-client/{client_id}", response_model=List[SubscriptionDetail])
def get_subscriptions_by_client(
    client_id: str,
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if client exists
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get subscriptions for client
    query = db.query(Subscription).options(
        joinedload(Subscription.topic)
    ).filter(Subscription.client_id == client_id)
    
    if active_only:
        query = query.filter(Subscription.active == True)
    
    subscriptions = query.all()
    
    # Manually add topic_name to response
    result = []
    for sub in subscriptions:
        sub_dict = SubscriptionResponse.model_validate(sub).model_dump()
        sub_dict["topic_name"] = sub.topic.name if sub.topic else None
        result.append(sub_dict)
    
    return result

@router.get("/by-topic/{topic_id}", response_model=List[SubscriptionDetail])
def get_subscriptions_by_topic(
    topic_id: int,
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if topic exists
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get subscriptions for topic
    query = db.query(Subscription).options(
        joinedload(Subscription.topic)
    ).filter(Subscription.topic_id == topic_id)
    
    if active_only:
        query = query.filter(Subscription.active == True)
        
    subscriptions = query.all()
    
    # Manually add topic_name to response
    result = []
    for sub in subscriptions:
        sub_dict = SubscriptionResponse.model_validate(sub).model_dump()
        sub_dict["topic_name"] = sub.topic.name if sub.topic else None
        result.append(sub_dict)
    
    return result

@router.get("/{subscription_id}/client", response_model=ClientResponse)
def get_client_by_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    client = db.query(Client).filter(Client.client_id == subscription.client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return client

@router.get("/{subscription_id}/topic", response_model=TopicResponse)
def get_topic_by_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    topic = db.query(Topic).filter(Topic.id == subscription.topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return topic

@router.put("/{subscription_id}/status", status_code=200)
def update_subscription_status(
    subscription_id: int,
    status_update: SubscriptionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    subscription.active = status_update.active
    db.commit()
    return {"message": "Subscription status updated successfully"}