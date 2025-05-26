import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os
from datetime import datetime
from dateutil.parser import parse

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from gui.api_client import ApiClient

class DashboardView(ttk.Frame):
    def __init__(self, parent, api_client, show_view_callback):
        super().__init__(parent)
        self.parent = parent
        self.api_client = api_client
        self.show_view_callback = show_view_callback
        
        # Data for dashboard
        self.client_count = tk.StringVar(value="0")
        self.topic_count = tk.StringVar(value="0")
        self.message_count = tk.StringVar(value="0")
        self.active_subscriptions = tk.StringVar(value="0")
        self.last_updated = tk.StringVar(value="Never")
        
        # Setup UI components
        self.setup_ui()
        
        # Start data refresh
        self.refresh_data()
        
        # Setup auto-refresh timer
        self.refresh_timer = None
        self.start_auto_refresh()
    
    def setup_ui(self):
        # Configure the grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Header frame - Title and control buttons
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        header_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(header_frame, text="TinyMQ Monitor Dashboard", font=("Helvetica", 18, "bold"))
        title_label.grid(row=0, column=0, sticky="w", padx=5, pady=10)
        
        # Refresh button
        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.refresh_data)
        refresh_button.grid(row=0, column=2, padx=5)
        
        # Settings button
        settings_button = ttk.Button(header_frame, text="Settings", command=self.show_settings)
        settings_button.grid(row=0, column=3, padx=5)
        
        # Logout button
        logout_button = ttk.Button(header_frame, text="Logout", command=self.logout)
        logout_button.grid(row=0, column=4, padx=5)
        
        # Main content area - split into left navigation and right content
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Navigation panel on the left
        nav_frame = ttk.LabelFrame(content_frame, text="Navigation")
        nav_frame.grid(row=0, column=0, sticky="ns", padx=5, pady=5)
        
        # Navigation buttons
        btn_clients = ttk.Button(
            nav_frame, text="Clients", width=15, 
            command=lambda: self.show_view_callback("clients")
        )
        btn_clients.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        btn_topics = ttk.Button(
            nav_frame, text="Topics", width=15,
            command=lambda: self.show_view_callback("topics")
        )
        btn_topics.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        btn_subscriptions = ttk.Button(
            nav_frame, text="Subscriptions", width=15,
            command=lambda: self.show_view_callback("subscriptions")
        )
        btn_subscriptions.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        btn_messages = ttk.Button(
            nav_frame, text="Message Logs", width=15,
            command=lambda: self.show_view_callback("messages")
        )
        btn_messages.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        
        btn_events = ttk.Button(
            nav_frame, text="Connection Events", width=15,
            command=lambda: self.show_view_callback("events")
        )
        btn_events.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        
        # Dashboard content on the right
        dashboard_frame = ttk.Frame(content_frame)
        dashboard_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        dashboard_frame.columnconfigure(0, weight=1)
        dashboard_frame.columnconfigure(1, weight=1)
        
        # Summary stats cards
        self.create_stat_card(dashboard_frame, 0, 0, "Connected Clients", self.client_count)
        self.create_stat_card(dashboard_frame, 0, 1, "Active Topics", self.topic_count)
        self.create_stat_card(dashboard_frame, 1, 0, "Messages Published", self.message_count)
        self.create_stat_card(dashboard_frame, 1, 1, "Active Subscriptions", self.active_subscriptions)
        
        # Recent activity frame
        activity_frame = ttk.LabelFrame(dashboard_frame, text="Recent Activity")
        activity_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=10)
        activity_frame.columnconfigure(0, weight=1)
        activity_frame.rowconfigure(0, weight=1)
        
        # Activity list with scrollbar
        self.activity_tree = ttk.Treeview(
            activity_frame,
            columns=("timestamp", "client", "event"),
            show="headings"
        )
        self.activity_tree.heading("timestamp", text="Timestamp")
        self.activity_tree.heading("client", text="Client ID")
        self.activity_tree.heading("event", text="Event")
        
        self.activity_tree.column("timestamp", width=150)
        self.activity_tree.column("client", width=150)
        self.activity_tree.column("event", width=200)
        
        self.activity_tree.grid(row=0, column=0, sticky="nsew")
        
        activity_scrollbar = ttk.Scrollbar(activity_frame, orient="vertical", command=self.activity_tree.yview)
        activity_scrollbar.grid(row=0, column=1, sticky="ns")
        self.activity_tree.configure(yscrollcommand=activity_scrollbar.set)
        
        # Last updated status
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        status_frame.columnconfigure(0, weight=1)
        
        status_label = ttk.Label(status_frame, text="Last updated:")
        status_label.grid(row=0, column=0, sticky="w", padx=5)
        
        update_time_label = ttk.Label(status_frame, textvariable=self.last_updated)
        update_time_label.grid(row=0, column=1, sticky="w", padx=5)
    
    def create_stat_card(self, parent, row, col, title, value_var):
        """Creates a card to display a statistic"""
        card_frame = ttk.LabelFrame(parent, text=title)
        card_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        
        value_label = ttk.Label(
            card_frame, 
            textvariable=value_var, 
            font=("Helvetica", 24, "bold"),
            anchor="center"
        )
        value_label.pack(fill="both", expand=True, padx=20, pady=20)
        
        return card_frame
    
    def refresh_data(self):
        """Refreshes all dashboard data"""
        try:
            # Start data fetching in a separate thread to avoid UI freezing
            threading.Thread(target=self._load_data, daemon=True).start()
        except Exception as e:
            print(f"Error starting refresh thread: {e}")
    
    def _load_data(self):
        """Loads data from API in background thread"""
        try:
            # Get client count
            clients = self.api_client.get_clients()
            
            # Make sure the view still exists before updating UI elements
            if not self.winfo_exists():
                return
                
            self.client_count.set(str(len(clients)))
            
            # Get topic count
            topics = self.api_client.get_topics()
            if not self.winfo_exists():
                return
            self.topic_count.set(str(len(topics)))
            
            # Get message count (get first 100 messages)
            messages = self.api_client.get_messages()
            if not self.winfo_exists():
                return
            self.message_count.set(str(len(messages)))
            
            # Get subscription count (just active ones)
            subscriptions = self.api_client.get_subscriptions(active_only=True)
            if not self.winfo_exists():
                return
            self.active_subscriptions.set(str(len(subscriptions)))
            
            # Get recent activity (last 10 connection events)
            events = self.api_client.get_events(limit=10)
            if not self.winfo_exists():
                return
            self._update_activity_list(events)
            
            # Update last updated time
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not self.winfo_exists():
                return
            self.last_updated.set(now)
            
        except Exception as e:
            error_message = str(e)
            print(f"Error refreshing data: {error_message}")
            # Store error message in a variable that can be accessed by the lambda
            if self.winfo_exists():
                self.after(0, lambda error=error_message: messagebox.showerror("Refresh Error", f"Error loading dashboard data: {error}"))
    
    def _update_activity_list(self, events):
        """Updates the activity tree with connection events"""
        try:
            # Check if treeview still exists
            if not self.winfo_exists() or not hasattr(self, 'activity_tree') or not self.activity_tree.winfo_exists():
                return
                
            # Clear existing items
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)
            
            # Add new events
            for event in events:
                # Handle timestamp consistently
                if isinstance(event.timestamp, str) and event.timestamp:
                    try:
                        # Try to parse the string to datetime
                        timestamp = parse(event.timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        # If parsing fails, just use the string as is
                        timestamp = event.timestamp
                elif hasattr(event.timestamp, 'strftime'):
                    # It's already a datetime object
                    timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    # It's None or some other type
                    timestamp = "N/A"
                    
                self.activity_tree.insert(
                    "", "end", 
                    values=(timestamp, event.client_id, event.event_type)
                )
        except tk.TclError as e:
            # Handle Tcl/Tk errors
            print(f"Tk error updating activity list: {e}")
        except Exception as e:
            print(f"Error updating activity list: {e}")
    
    def start_auto_refresh(self, interval=1000):
        """Starts auto-refresh timer"""
        if self.refresh_timer is not None:
            self.after_cancel(self.refresh_timer)
        
        self.refresh_timer = self.after(interval, self._auto_refresh)
    
    def _auto_refresh(self):
        """Auto refresh handler"""
        # Only refresh if the view still exists
        if self.winfo_exists():
            self.refresh_data()
            self.start_auto_refresh()
        else:
            # View was destroyed, don't schedule more refreshes
            self.refresh_timer = None
    
    def show_settings(self):
        """Shows settings dialog"""
        self.show_view_callback("settings")
    
    def logout(self):
        """Handles logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.show_view_callback("login")
    
    def on_destroy(self):
        """Clean up when view is destroyed"""
        try:
            if self.refresh_timer is not None:
                self.after_cancel(self.refresh_timer)
                self.refresh_timer = None
        except tk.TclError:
            # Widget might already be destroyed
            pass 