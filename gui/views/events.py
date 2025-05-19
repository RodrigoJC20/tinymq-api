import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from gui.api_client import ApiClient
from common import ConnectionEvent, Client

class EventsView(ttk.Frame):
    def __init__(self, parent, api_client, show_view_callback):
        super().__init__(parent)
        self.parent = parent
        self.api_client = api_client
        self.show_view_callback = show_view_callback
        
        # Pagination variables
        self.page = 0
        self.page_size = 20
        self.total_events = 0
        
        # Filter variables
        self.event_type_var = tk.StringVar(value="ALL")
        
        # Selected event for details
        self.selected_event = None
        
        # Setup UI components
        self.setup_ui()
        
        # Load initial data
        self.load_events()
    
    def setup_ui(self):
        # Configure the grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Header frame - Title and control buttons
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        header_frame.columnconfigure(1, weight=1)
        
        back_button = ttk.Button(header_frame, text="< Back", command=lambda: self.show_view_callback("dashboard"))
        back_button.grid(row=0, column=0, sticky="w", padx=5, pady=10)
        
        title_label = ttk.Label(header_frame, text="TinyMQ Connection Events", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        
        # Event type filter
        filter_frame = ttk.Frame(header_frame)
        filter_frame.grid(row=0, column=2, padx=5, pady=10)
        
        ttk.Label(filter_frame, text="Event Type:").grid(row=0, column=0, padx=2)
        
        event_type_combobox = ttk.Combobox(
            filter_frame, 
            textvariable=self.event_type_var,
            values=["ALL", "CONNECT", "DISCONNECT"],
            width=12,
            state="readonly"
        )
        event_type_combobox.grid(row=0, column=1, padx=2)
        event_type_combobox.bind("<<ComboboxSelected>>", lambda e: self.load_events())
        
        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.load_events)
        refresh_button.grid(row=0, column=3, padx=5, pady=10)
        
        # Main content - split into top event list and bottom event details
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=3)  # Event list gets more space
        content_frame.rowconfigure(1, weight=2)  # Event details gets less space
        
        # Event list frame with Treeview
        list_frame = ttk.LabelFrame(content_frame, text="Connection Events")
        list_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Events table with scrollbar
        self.events_tree = ttk.Treeview(
            list_frame,
            columns=("id", "client_id", "event_type", "ip_address", "port", "timestamp"),
            show="headings",
            selectmode="browse"
        )
        
        self.events_tree.heading("id", text="ID")
        self.events_tree.heading("client_id", text="Client ID")
        self.events_tree.heading("event_type", text="Event Type")
        self.events_tree.heading("ip_address", text="IP Address")
        self.events_tree.heading("port", text="Port")
        self.events_tree.heading("timestamp", text="Timestamp")
        
        self.events_tree.column("id", width=50)
        self.events_tree.column("client_id", width=180)
        self.events_tree.column("event_type", width=100)
        self.events_tree.column("ip_address", width=120)
        self.events_tree.column("port", width=70)
        self.events_tree.column("timestamp", width=150)
        
        self.events_tree.grid(row=0, column=0, sticky="nsew")
        self.events_tree.bind("<<TreeviewSelect>>", self.on_event_selected)
        
        # Add scrollbar to treeview
        tree_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.events_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        self.events_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Pagination frame
        pagination_frame = ttk.Frame(list_frame)
        pagination_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.prev_page_btn = ttk.Button(pagination_frame, text="Previous", command=self.prev_page)
        self.prev_page_btn.grid(row=0, column=0, padx=5)
        
        self.page_label = ttk.Label(pagination_frame, text="Page 1")
        self.page_label.grid(row=0, column=1, padx=5)
        
        self.next_page_btn = ttk.Button(pagination_frame, text="Next", command=self.next_page)
        self.next_page_btn.grid(row=0, column=2, padx=5)
        
        # Event details frame
        details_frame = ttk.LabelFrame(content_frame, text="Event Details")
        details_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        details_frame.columnconfigure(1, weight=1)
        
        # Event details content
        ttk.Label(details_frame, text="Event ID:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.detail_event_id = ttk.Label(details_frame, text="")
        self.detail_event_id.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Client ID:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.detail_client_id = ttk.Label(details_frame, text="")
        self.detail_client_id.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Event Type:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.detail_event_type = ttk.Label(details_frame, text="")
        self.detail_event_type.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="IP Address:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.detail_ip_address = ttk.Label(details_frame, text="")
        self.detail_ip_address.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Port:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.detail_port = ttk.Label(details_frame, text="")
        self.detail_port.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Timestamp:").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        self.detail_timestamp = ttk.Label(details_frame, text="")
        self.detail_timestamp.grid(row=5, column=1, sticky="w", padx=5, pady=2)
        
        # Action buttons
        action_frame = ttk.Frame(details_frame)
        action_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        view_client_btn = ttk.Button(
            action_frame, 
            text="View Client", 
            command=self.view_client
        )
        view_client_btn.grid(row=0, column=0, padx=5)
        
        view_client_events_btn = ttk.Button(
            action_frame, 
            text="View All Client Events", 
            command=self.view_client_events
        )
        view_client_events_btn.grid(row=0, column=1, padx=5)
        
        # Status bar
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky="w")
        
        # Initially disable event actions
        self.update_detail_buttons_state(False)
    
    def load_events(self):
        """Loads connection event data from API"""
        self.status_var.set("Loading connection events...")
        self.update_idletasks()
        
        # Clear selected event
        self.selected_event = None
        self.clear_event_details()
        
        # Calculate skip based on page and page size
        skip = self.page * self.page_size
        
        # Get event type filter
        event_type = None if self.event_type_var.get() == "ALL" else self.event_type_var.get()
        
        # Start loading in background thread
        threading.Thread(
            target=self._fetch_events, 
            args=(skip, event_type), 
            daemon=True
        ).start()
    
    def _fetch_events(self, skip, event_type):
        """Background thread to fetch events from API"""
        events = self.api_client.get_events(
            skip=skip, 
            limit=self.page_size, 
            event_type=event_type
        )
        
        # Update UI in main thread
        self.after(0, lambda: self._update_event_list(events))
    
    def _update_event_list(self, events):
        """Updates the events treeview with data"""
        # Clear existing entries
        for row in self.events_tree.get_children():
            self.events_tree.delete(row)
            
        # Add events to treeview
        for event in events:
            # Format the timestamp if it exists
            timestamp = event.timestamp
            if timestamp:
                # Format date for display
                if isinstance(timestamp, str):
                    # If it's a string, it's likely ISO format
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except ValueError:
                        pass
                
                if isinstance(timestamp, datetime):
                    timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            # Insert into treeview
            self.events_tree.insert(
                "", "end", 
                values=(
                    event.id, 
                    event.client_id, 
                    event.event_type,
                    event.ip_address,
                    event.port,
                    timestamp
                )
            )
            
        # Update status
        if events:
            self.status_var.set(f"Loaded {len(events)} connection events")
        else:
            self.status_var.set("No connection events found")
            
        # Update pagination buttons
        self.update_pagination()
    
    def update_pagination(self):
        """Update pagination controls based on current page"""
        self.page_label.config(text=f"Page {self.page + 1}")
        
        # Enable/disable prev button based on current page
        if self.page > 0:
            self.prev_page_btn.state(["!disabled"])
        else:
            self.prev_page_btn.state(["disabled"])
            
        # Logic for next button could depend on if we know there are more pages
        # For now, we'll disable it if we received fewer items than the page size
        children_count = len(self.events_tree.get_children())
        if children_count < self.page_size:
            self.next_page_btn.state(["disabled"])
        else:
            self.next_page_btn.state(["!disabled"])
    
    def prev_page(self):
        """Go to previous page of events"""
        if self.page > 0:
            self.page -= 1
            self.load_events()
    
    def next_page(self):
        """Go to next page of events"""
        self.page += 1
        self.load_events()
    
    def on_event_selected(self, event):
        """Handle event selection in treeview"""
        selected_items = self.events_tree.selection()
        if selected_items:
            # Get event ID from the first column of the selected row
            item_values = self.events_tree.item(selected_items[0], "values")
            event_id = int(item_values[0])
            
            # Fetch event details in background
            self.status_var.set("Loading event details...")
            threading.Thread(target=self._fetch_event_details, args=(event_id,), daemon=True).start()
        else:
            self.clear_event_details()
            self.update_detail_buttons_state(False)
    
    def _fetch_event_details(self, event_id):
        """Background thread to fetch event details"""
        event = self.api_client.get_event(event_id)
        
        if event:
            # Update UI in main thread
            self.after(0, lambda: self.update_event_details(event))
        else:
            self.after(0, lambda: self.status_var.set("Failed to load event details"))
    
    def update_event_details(self, event):
        """Update the event details panel with event data"""
        self.selected_event = event
        
        # Format the timestamp if it exists
        timestamp = event.timestamp
        if timestamp:
            # Format date for display
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    pass
            
            if isinstance(timestamp, datetime):
                timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        # Update detail labels
        self.detail_event_id.config(text=str(event.id))
        self.detail_client_id.config(text=event.client_id)
        self.detail_event_type.config(text=event.event_type)
        self.detail_ip_address.config(text=event.ip_address or "Unknown")
        self.detail_port.config(text=str(event.port or "Unknown"))
        self.detail_timestamp.config(text=timestamp or "Unknown")
        
        # Enable action buttons
        self.update_detail_buttons_state(True)
        
        self.status_var.set("Event details loaded")
    
    def clear_event_details(self):
        """Clear the event details panel"""
        self.detail_event_id.config(text="")
        self.detail_client_id.config(text="")
        self.detail_event_type.config(text="")
        self.detail_ip_address.config(text="")
        self.detail_port.config(text="")
        self.detail_timestamp.config(text="")
        
        # Disable action buttons
        self.update_detail_buttons_state(False)
    
    def update_detail_buttons_state(self, enabled):
        """Enable or disable the detail action buttons"""
        state = ["!disabled"] if enabled else ["disabled"]
        
        # Get all buttons in the action frame
        action_frame = self.winfo_children()[1].winfo_children()[1].winfo_children()[6]
        for child in action_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.state(state)
    
    def view_client(self):
        """Navigate to the client details view for this event's client"""
        if self.selected_event:
            # This would normally transition to the client view
            # For now, just show a message
            messagebox.showinfo(
                "View Client", 
                f"View client '{self.selected_event.client_id}'\n"
                f"This navigation feature is not yet implemented."
            )
    
    def view_client_events(self):
        """Filter events to only show those for this client"""
        if self.selected_event:
            # This would normally filter the events view to only show events for this client
            # For now, just show a message
            messagebox.showinfo(
                "View Client Events", 
                f"Filter events for client '{self.selected_event.client_id}'\n"
                f"This filtering feature is not yet implemented."
            ) 