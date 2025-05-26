import tkinter as tk
from tkinter import ttk, messagebox
import threading
from common import ConnectionEvent
from dateutil.parser import parse

class ClientEventsView(ttk.Frame):
    def __init__(self, parent, api_client, client_id, show_view_callback):
        super().__init__(parent)
        self.parent = parent
        self.api_client = api_client
        self.client_id = client_id
        self.show_view_callback = show_view_callback
        
        # Pagination variables
        self.page = 0
        self.page_size = 20
        
        # Setup UI components
        self.setup_ui()
        
        # Load initial data
        self.load_events()
    
    def setup_ui(self):
        # Configure the grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Header frame
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        header_frame.columnconfigure(1, weight=1)
        
        back_button = ttk.Button(header_frame, text="< Back", command=lambda: self.show_view_callback("clients"))
        back_button.grid(row=0, column=0, sticky="w", padx=5, pady=10)
        
        title_label = ttk.Label(header_frame, text=f"Events for Client: {self.client_id}", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        
        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.load_events)
        refresh_button.grid(row=0, column=2, padx=5, pady=10)
        
        # Events list frame
        list_frame = ttk.LabelFrame(self, text="Events")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Events table with scrollbar
        self.events_tree = ttk.Treeview(
            list_frame,
            columns=("id", "event_type", "timestamp", "ip_address", "port"),
            show="headings",
            selectmode="browse"
        )
        
        self.events_tree.heading("id", text="ID")
        self.events_tree.heading("event_type", text="Event Type")
        self.events_tree.heading("timestamp", text="Timestamp")
        self.events_tree.heading("ip_address", text="IP Address")
        self.events_tree.heading("port", text="Port")
        
        self.events_tree.column("id", width=50)
        self.events_tree.column("event_type", width=150)
        self.events_tree.column("timestamp", width=150)
        self.events_tree.column("ip_address", width=120)
        self.events_tree.column("port", width=80)
        
        self.events_tree.grid(row=0, column=0, sticky="nsew")
        
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
        
        # Client details frame
        client_details_frame = ttk.LabelFrame(self, text="Client Details")
        client_details_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=10) 
        client_details_frame.columnconfigure(1, weight=1)

        ttk.Label(client_details_frame, text="Client ID:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.detail_client_id = ttk.Label(client_details_frame, text=self.client_id)
        self.detail_client_id.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(client_details_frame, text="Event Count:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.detail_event_count = ttk.Label(client_details_frame, text="")
        self.detail_event_count.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Update event count
        self.update_event_count()

    def load_events(self):
        """Loads events data from API"""
        skip = self.page * self.page_size
        threading.Thread(target=self._fetch_events, args=(skip,), daemon=True).start()
    
    def _fetch_events(self, skip):
        """Background thread to fetch events from API"""
        try:
            events = self.api_client.get_events_by_client(self.client_id, skip=skip, limit=self.page_size)
            self.after(0, lambda: self._update_events_list(events))
        except Exception as e:
            print(f"Error loading events: {str(e)}")
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to load events: {str(e)}"))
    
    def _update_events_list(self, events):
        """Updates the events list treeview with fetched data"""
        # Clear existing items
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)

        # Parse timestamp to datetime
        for event in events:
            if isinstance(event.timestamp, str):
                event.timestamp = parse(event.timestamp)
        # Format timestamps
        for event in events:
            event.timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S") if event.timestamp else "N/A"
            self.events_tree.insert(
                "", "end", 
                values=(event.id, event.event_type, event.timestamp, event.ip_address or "N/A", event.port or "N/A")
            )
        
        # Update pagination
        self.update_pagination(len(events))
    
    def update_pagination(self, item_count):
        """Updates pagination controls"""
        self.page_label.config(text=f"Page {self.page + 1}")
        self.prev_page_btn.state(["disabled"] if self.page == 0 else ["!disabled"])
        self.next_page_btn.state(["disabled"] if item_count < self.page_size else ["!disabled"])
    
    def prev_page(self):
        """Go to previous page of events"""
        if self.page > 0:
            self.page -= 1
            self.load_events()
    
    def next_page(self):
        """Go to next page of events"""
        self.page += 1
        self.load_events()

    def update_event_count(self):
        """Fetch and update the event count for the client."""
        threading.Thread(target=self._fetch_event_count, daemon=True).start()

    def _fetch_event_count(self):
        try:
            events = self.api_client.get_events_by_client(self.client_id)
            self.after(0, lambda: self.detail_event_count.config(text=str(len(events))))
        except Exception as e:
            print(f"Error fetching event count: {e}")
            self.after(0, lambda: self.detail_event_count.config(text="Error"))
