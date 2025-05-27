from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, create_engine, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSONB
import datetime
from .config import DATABASE_URL

# Create SQLAlchemy engine and session factory
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Admin user table for API authentication
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    last_login = Column(DateTime)

# TinyMQ database tables

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, unique=True, index=True)
    last_connected = Column(DateTime)
    last_ip = Column(String)
    last_port = Column(Integer)
    connection_count = Column(Integer, default=1)
    active = Column(Boolean, default=False)
    
    # Relationships
    topics = relationship("Topic", back_populates="owner", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="client", cascade="all, delete-orphan")
    messages = relationship("MessageLog", back_populates="publisher", cascade="all, delete-orphan")
    connection_events = relationship("ConnectionEvent", back_populates="client", cascade="all, delete-orphan")

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    owner_client_id = Column(String, ForeignKey("clients.client_id"))
    created_at = Column(DateTime)
    
    # Relationships
    owner = relationship("Client", back_populates="topics")
    subscriptions = relationship("Subscription", back_populates="topic")
    messages = relationship("MessageLog", back_populates="topic")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    subscribed_at = Column(DateTime)
    active = Column(Boolean, default=True)
    
    # Relationships
    client = relationship("Client", back_populates="subscriptions")
    topic = relationship("Topic", back_populates="subscriptions")

class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, index=True)
    publisher_client_id = Column(String, ForeignKey("clients.client_id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    payload_size = Column(Integer, nullable=False)
    payload_preview = Column(String, nullable=True)
    # payload_data = Column(JSONB, nullable=True)
    published_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    publisher = relationship("Client", back_populates="messages")
    topic = relationship("Topic", back_populates="messages")

class ConnectionEvent(Base):
    __tablename__ = "connection_events"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"))
    event_type = Column(String)  # 'CONNECT' or 'DISCONNECT'
    ip_address = Column(String)
    port = Column(Integer)
    timestamp = Column(DateTime)
    
    # Relationships
    client = relationship("Client", back_populates="connection_events")

# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()