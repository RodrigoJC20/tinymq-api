import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import sys
import os

# Add parent directory to path for import of common module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common import Client, Topic, Subscription, MessageLog, ConnectionEvent, ApiConfig

class ApiClient:
    """Client for communicating with the TinyMQ API"""
    
    def __init__(self, api_config: ApiConfig):
        self.api_config = api_config
    
    def login(self) -> bool:
        """Authenticate with the API and get a token"""
        try:
            response = requests.post(
                f"{self.api_config.base_url}/token",
                data={
                    "username": self.api_config.username,
                    "password": self.api_config.password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.api_config.token = data["access_token"]
                # Set token expiry to 55 minutes (a bit less than the server's 60 minutes)
                self.api_config.token_expiry = datetime.now() + timedelta(minutes=55)
                return True
            else:
                print(f"Login failed: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authorization token"""
        return {"Authorization": f"Bearer {self.api_config.token}"}
    
    def ensure_authenticated(self) -> bool:
        """Ensure we have a valid token, attempting login if needed"""
        if not self.api_config.is_token_valid():
            return self.login()
        return True
    
    # Client endpoints
    def get_clients(self, skip: int = 0, limit: int = 100) -> List[Client]:
        """Get a list of clients"""
        if not self.ensure_authenticated():
            return []
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/clients/",
                headers=self._get_headers(),
                params={"skip": skip, "limit": limit}
            )
            
            if response.status_code == 200:
                return [Client(**client_data) for client_data in response.json()]
            else:
                print(f"Failed to get clients: {response.status_code} {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting clients: {str(e)}")
            return []
    
    def get_client(self, client_id: str) -> Optional[Client]:
        """Get a specific client by ID"""
        if not self.ensure_authenticated():
            return None
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/clients/{client_id}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return Client(**response.json())
            else:
                print(f"Failed to get client: {response.status_code} {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting client: {str(e)}")
            return None
    
    def delete_client(self, client_id: str) -> bool:
        """Delete a client"""
        if not self.ensure_authenticated():
            return False
        
        try:
            response = requests.delete(
                f"{self.api_config.base_url}/clients/{client_id}",
                headers=self._get_headers()
            )
            
            return response.status_code == 204
                
        except Exception as e:
            print(f"Error deleting client: {str(e)}")
            return False
    
    def update_client_status(self, client_id: str, active: bool) -> bool:
        """Update a client's active status"""
        if not self.ensure_authenticated():
            return False
        
        try:
            response = requests.patch(
                f"{self.api_config.base_url}/clients/{client_id}",
                headers=self._get_headers(),
                json={"active": active}
            )
            
            return response.status_code == 200
                
        except Exception as e:
            print(f"Error updating client status: {str(e)}")
            return False
    
    # Topic endpoints
    def get_topics(self, skip: int = 0, limit: int = 100) -> List[Topic]:
        """Get a list of topics"""
        if not self.ensure_authenticated():
            return []
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/topics/",
                headers=self._get_headers(),
                params={"skip": skip, "limit": limit}
            )
            
            if response.status_code == 200:
                return [Topic(**topic_data) for topic_data in response.json()]
            else:
                print(f"Failed to get topics: {response.status_code} {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting topics: {str(e)}")
            return []
    
    def get_topic(self, topic_id: int) -> Optional[Topic]:
        """Get a specific topic by ID"""
        if not self.ensure_authenticated():
            return None
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/topics/{topic_id}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return Topic(**response.json())
            else:
                print(f"Failed to get topic: {response.status_code} {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting topic: {str(e)}")
            return None
    
    def get_topics_by_client(self, client_id: str) -> List[Topic]:
        """Get topics owned by a specific client"""
        if not self.ensure_authenticated():
            return []
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/topics/by-client/{client_id}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return [Topic(**topic_data) for topic_data in response.json()]
            else:
                print(f"Failed to get topics: {response.status_code} {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting topics: {str(e)}")
            return []
    
    def delete_topic(self, topic_id: int) -> bool:
        """Delete a topic"""
        if not self.ensure_authenticated():
            return False
        
        try:
            response = requests.delete(
                f"{self.api_config.base_url}/topics/{topic_id}",
                headers=self._get_headers()
            )
            
            return response.status_code == 204
                
        except Exception as e:
            print(f"Error deleting topic: {str(e)}")
            return False
    
    # Subscription endpoints
    def get_subscriptions(self, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Subscription]:
        """Get a list of subscriptions"""
        if not self.ensure_authenticated():
            return []
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/subscriptions/",
                headers=self._get_headers(),
                params={"skip": skip, "limit": limit, "active_only": active_only}
            )
            
            if response.status_code == 200:
                return [Subscription(**sub_data) for sub_data in response.json()]
            else:
                print(f"Failed to get subscriptions: {response.status_code} {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting subscriptions: {str(e)}")
            return []
    
    def get_subscription(self, subscription_id: int) -> Optional[Subscription]:
        """Get a specific subscription by ID"""
        if not self.ensure_authenticated():
            return None
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/subscriptions/{subscription_id}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return Subscription(**response.json())
            else:
                print(f"Failed to get subscription: {response.status_code} {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting subscription: {str(e)}")
            return None
    
    def get_subscriptions_by_client(self, client_id: str, active_only: bool = False) -> List[Subscription]:
        """Get subscriptions for a specific client"""
        if not self.ensure_authenticated():
            return []
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/subscriptions/by-client/{client_id}",
                headers=self._get_headers(),
                params={"active_only": active_only}
            )
            
            if response.status_code == 200:
                return [Subscription(**sub_data) for sub_data in response.json()]
            else:
                print(f"Failed to get subscriptions: {response.status_code} {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting subscriptions: {str(e)}")
            return []
    
    def get_subscriptions_by_topic(self, topic_id: int, active_only: bool = False) -> List[Subscription]:
        """Get subscriptions for a specific topic"""
        if not self.ensure_authenticated():
            return []
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/subscriptions/by-topic/{topic_id}",
                headers=self._get_headers(),
                params={"active_only": active_only}
            )
            
            if response.status_code == 200:
                return [Subscription(**sub_data) for sub_data in response.json()]
            else:
                print(f"Failed to get subscriptions: {response.status_code} {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting subscriptions: {str(e)}")
            return []
    
    def delete_subscription(self, subscription_id: int) -> bool:
        """Delete a subscription"""
        if not self.ensure_authenticated():
            return False
        
        try:
            response = requests.delete(
                f"{self.api_config.base_url}/subscriptions/{subscription_id}",
                headers=self._get_headers()
            )
            
            return response.status_code == 204
                
        except Exception as e:
            print(f"Error deleting subscription: {str(e)}")
            return False
    
    # Message logs endpoints
    def get_messages(self, skip: int = 0, limit: int = 100) -> List[MessageLog]:
        """Get a list of message logs"""
        if not self.ensure_authenticated():
            return []
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/messages/",
                headers=self._get_headers(),
                params={"skip": skip, "limit": limit}
            )
            
            if response.status_code == 200:
                return [MessageLog(**msg_data) for msg_data in response.json()]
            else:
                print(f"Failed to get messages: {response.status_code} {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting messages: {str(e)}")
            return []
        
    def get_message(self, message_id: int) -> Optional[MessageLog]:
        """Get a single message by its ID."""
        if not self.ensure_authenticated():
            return None
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/messages/{message_id}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return MessageLog(**response.json())
            else:
                print(f"Failed to get message: {response.status_code} {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting message: {str(e)}")
            return None
    
    
    def get_messages_by_client(self, client_id: str, skip: int = 0, limit: int = 100) -> List[MessageLog]:
        """Get message logs for a specific client"""
        if not self.ensure_authenticated():
            return []
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/messages/by-client/{client_id}",
                headers=self._get_headers(),
                params={"skip": skip, "limit": limit}
            )
            
            if response.status_code == 200:
                return [MessageLog(**msg_data) for msg_data in response.json()]
            else:
                print(f"Failed to get messages: {response.status_code} {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting messages: {str(e)}")
            return []
    
    def get_messages_by_topic(self, topic_id: int, skip: int = 0, limit: int = 100) -> List[MessageLog]:
        """Get message logs for a specific topic"""
        if not self.ensure_authenticated():
            return []
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/messages/by-topic/{topic_id}",
                headers=self._get_headers(),
                params={"skip": skip, "limit": limit}
            )
            
            if response.status_code == 200:
                return [MessageLog(**msg_data) for msg_data in response.json()]
            else:
                print(f"Failed to get messages: {response.status_code} {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting messages: {str(e)}")
            return []
    
    def delete_message(self, message_id: int) -> bool:
        """Delete a message log"""
        if not self.ensure_authenticated():
            return False
        
        try:
            response = requests.delete(
                f"{self.api_config.base_url}/messages/{message_id}",
                headers=self._get_headers()
            )
            
            return response.status_code == 204
                
        except Exception as e:
            print(f"Error deleting message: {str(e)}")
            return False
    
    # Connection events endpoints
    def get_events(self, skip: int = 0, limit: int = 100, event_type: Optional[str] = None) -> List[ConnectionEvent]:
        """Get a list of connection events"""
        if not self.ensure_authenticated():
            return []
        
        params = {"skip": skip, "limit": limit}
        if event_type:
            params["event_type"] = event_type
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/events/",
                headers=self._get_headers(),
                params=params
            )
            
            if response.status_code == 200:
                return [ConnectionEvent(**event_data) for event_data in response.json()]
            else:
                print(f"Failed to get events: {response.status_code} {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting events: {str(e)}")
            return []
    
    def get_events_by_client(self, client_id: str, skip: int = 0, limit: int = 100, event_type: Optional[str] = None) -> List[ConnectionEvent]:
        """Get connection events for a specific client"""
        if not self.ensure_authenticated():
            return []
        
        params = {"skip": skip, "limit": limit}
        if event_type:
            params["event_type"] = event_type
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/events/by-client/{client_id}",
                headers=self._get_headers(),
                params=params
            )
            
            if response.status_code == 200:
                return [ConnectionEvent(**event_data) for event_data in response.json()]
            else:
                print(f"Failed to get events: {response.status_code} {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting events: {str(e)}")
            return []
    
    def delete_event(self, event_id: int) -> bool:
        """Delete a connection event"""
        if not self.ensure_authenticated():
            return False
        
        try:
            response = requests.delete(
                f"{self.api_config.base_url}/events/{event_id}",
                headers=self._get_headers()
            )
            
            return response.status_code == 204
                
        except Exception as e:
            print(f"Error deleting event: {str(e)}")
            return False
    
    # User management
    def change_password(self, new_password: str) -> bool:
        """Change the admin user's password"""
        if not self.ensure_authenticated():
            return False
        
        try:
            response = requests.put(
                f"{self.api_config.base_url}/auth/me",
                headers=self._get_headers(),
                json={"password": new_password}
            )
            
            if response.status_code == 200:
                # Update stored password
                self.api_config.password = new_password
                return True
            else:
                print(f"Failed to change password: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            print(f"Error changing password: {str(e)}")
            return False
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current user"""
        if not self.ensure_authenticated():
            return None
        
        try:
            response = requests.get(
                f"{self.api_config.base_url}/auth/me",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get user info: {response.status_code} {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting user info: {str(e)}")
            return None