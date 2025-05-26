import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from ttkthemes import ThemedTk

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import views
from gui.views.login import LoginView
from gui.views.dashboard import DashboardView
from gui.views.client.clients import ClientsView
from gui.views.settings import SettingsView
from gui.views.topic.topics import TopicsView
from gui.views.subscription.subscriptions import SubscriptionsView
from gui.views.message.messages import MessagesView
from gui.views.event.events import EventsView
from gui.views.client.client_topics import ClientTopicsView
from gui.views.client.client_subscriptions import ClientSubscriptionsView
from gui.views.client.client_messages import ClientMessagesView
from gui.views.client.client_events import ClientEventsView
from gui.views.topic.topic_subscriptions import TopicSubscriptionsView
from gui.views.topic.topic_messages import TopicMessagesView
from gui.views.topic.topic_client import TopicClientView
from gui.views.subscription.subscription_client import SubscriptionClientView
from gui.views.subscription.subscription_topic import SubscriptionTopicView
from gui.views.message.message_publisher import MessagePublisherView
from gui.views.message.message_topic import MessageTopicView
from gui.views.event.event_all_client_events import EventAllClientEventsView
from gui.views.event.event_client import EventClientView

class TinyMQMonitorApp:
    """Main TinyMQ Monitor application"""
    
    def __init__(self):
        # Create themed root window
        self.root = ThemedTk(theme="arc")  # Modern and clean theme
        self.root.title("TinyMQ Monitor")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure styles
        self.setup_styles()
        
        # Current view
        self.current_view = None
        self.api_client = None
        
        # Setup main container frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Show login view initially
        self.show_view("login")
    
    def setup_styles(self):
        """Set up custom styles for the application"""
        style = ttk.Style()
        
        # Custom button styles
        style.configure(
            "Accent.TButton", 
            background="#4a6cd4",
            foreground="#ffffff"
        )
        
        style.configure(
            "Danger.TButton",
            background="#d9534f",
            foreground="#ffffff"
        )
        
        # Add more custom styles as needed
    
    def show_view(self, view_name, **kwargs):
        """Switch to a different view"""
        # Destroy current view if it exists
        if self.current_view is not None:
            # Clean up resources if needed
            if hasattr(self.current_view, 'on_destroy'):
                self.current_view.on_destroy()
            self.current_view.destroy()
        
        # Create the new view
        if view_name == "login":
            self.current_view = LoginView(self.main_frame, self.on_login_success)
        elif view_name == "dashboard":
            self.current_view = DashboardView(self.main_frame, self.api_client, self.show_view)
        elif view_name == "clients":
            self.current_view = ClientsView(self.main_frame, self.api_client, self.show_view)
        elif view_name == "settings":
            self.current_view = SettingsView(self.main_frame, self.api_client, self.show_view)
        elif view_name == "topics":
            self.current_view = TopicsView(self.main_frame, self.api_client, self.show_view)
        elif view_name == "subscriptions":
            self.current_view = SubscriptionsView(self.main_frame, self.api_client, self.show_view)
        elif view_name == "messages":
            self.current_view = MessagesView(self.main_frame, self.api_client, self.show_view)
        elif view_name == "events":
            self.current_view = EventsView(self.main_frame, self.api_client, self.show_view)
        elif view_name == "client_topics":
            self.current_view = ClientTopicsView(self.main_frame, self.api_client, kwargs["client_id"], self.show_view)
        elif view_name == "client_subscriptions":
            self.current_view = ClientSubscriptionsView(self.main_frame, self.api_client, kwargs["client_id"], self.show_view)
        elif view_name == "client_messages":
            self.current_view = ClientMessagesView(self.main_frame, self.api_client, kwargs["client_id"], self.show_view)
        elif view_name == "client_events":
            self.current_view = ClientEventsView(self.main_frame, self.api_client, kwargs["client_id"], self.show_view)
        elif view_name == "topic_subscriptions":
            self.current_view = TopicSubscriptionsView(self.main_frame, self.api_client, kwargs["topic_id"], self.show_view)
        elif view_name == "topic_messages":
            self.current_view = TopicMessagesView(self.main_frame, self.api_client, kwargs["topic_id"], self.show_view)
        elif view_name == "topic_client":
            self.current_view = TopicClientView(self.main_frame, self.api_client, kwargs["topic_id"], self.show_view)
        elif view_name == "subscription_client":
            self.current_view = SubscriptionClientView(self.main_frame, self.api_client, kwargs["subscription_id"], self.show_view)
        elif view_name == "subscription_topic":
            self.current_view = SubscriptionTopicView(self.main_frame, self.api_client, kwargs["subscription_id"], self.show_view)
        elif view_name == "message_publisher":
            self.current_view = MessagePublisherView(self.main_frame, self.api_client, kwargs["message_id"], self.show_view)
        elif view_name == "message_topic":
            self.current_view = MessageTopicView(self.main_frame, self.api_client, kwargs["message_id"], self.show_view)
        elif view_name == "event_all_client_events": 
            self.current_view = EventAllClientEventsView(self.main_frame, self.api_client, kwargs["client_id"], self.show_view)
        elif view_name == "event_client":
            self.current_view = EventClientView(self.main_frame, self.api_client, kwargs["event_id"], self.show_view)
        else:
            # Handle unknown views
            messagebox.showerror("Error", f"Unknown view: {view_name}")
            return
        
        # Configure and show the view
        self.current_view.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    def on_login_success(self, api_client):
        """Called when login is successful"""
        self.api_client = api_client
        self.show_view("dashboard")
    
    def show_not_implemented(self, feature_name):
        """Shows a message for not implemented features"""
        messagebox.showinfo(
            "Not Implemented", 
            f"The {feature_name} view is not implemented yet.\n\nCheck back in a future version!"
        )
        
        # Show dashboard instead
        self.show_view("dashboard")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = TinyMQMonitorApp()
    app.run()