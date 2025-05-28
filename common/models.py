from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

@dataclass
class Client:
    id: int
    client_id: str
    last_connected: Optional[datetime] = None
    last_ip: Optional[str] = None
    last_port: Optional[int] = None
    connection_count: int = 0
    active: bool = False

@dataclass
class Topic:
    id: int
    name: str
    owner_client_id: str
    created_at: Optional[datetime] = None
    publish: bool = False

@dataclass
class Subscription:
    id: int
    client_id: str
    topic_id: int
    topic_name: Optional[str] = None
    subscribed_at: Optional[datetime] = None
    active: bool = True

@dataclass
class MessageLog:
    id: int
    publisher_client_id: str
    topic_id: int
    payload_size: int
    topic_name: Optional[str] = None
    payload_preview: Optional[str] = None
    payload_data: Optional[Dict[str, Any]] = None
    published_at: Optional[datetime] = None

@dataclass
class ConnectionEvent:
    id: int
    client_id: str
    event_type: str
    ip_address: Optional[str] = None
    port: Optional[int] = None
    timestamp: Optional[datetime] = None

@dataclass
class AdminRequest:
    id: int
    topic_id: Optional[int] = None
    requester_client_id: Optional[str] = None
    status: Optional[str] = None  # 'pending', 'approved', 'rejected', 'revoked'
    request_timestamp: Optional[datetime] = None
    response_timestamp: Optional[datetime] = None

@dataclass
class AdminSensorConfig:
    topic_id: int
    sensor_name: str
    active: bool = True
    set_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    activable: bool = False

@dataclass
class TopicAdmin:
    topic_id: int
    admin_client_id: str
    granted_at: Optional[datetime] = None

@dataclass
class ApiConfig:
    host: str
    port: int
    username: str
    password: str
    token: Optional[str] = None
    token_expiry: Optional[datetime] = None

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def is_token_valid(self) -> bool:
        if not self.token or not self.token_expiry:
            return False
        return datetime.now() < self.token_expiry 