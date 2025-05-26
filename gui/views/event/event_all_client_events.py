import tkinter as tk
from tkinter import ttk
import threading
from datetime import datetime

class EventAllClientEventsView(ttk.Frame):
    def __init__(self, parent, api_client, client_id, show_view_callback):
        super().__init__(parent)
        self.api_client = api_client
        self.client_id = client_id
        self.show_view_callback = show_view_callback
        self.status_var = tk.StringVar(value="Ready")
        
        # Pagination variables
        self.page = 0
        self.page_size = 20  # Limit of events per page
        
        self.setup_ui()
        self.load_all_events()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)  # Allow the table to expand vertically

        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(15, 5))
        header_frame.columnconfigure(1, weight=1)

        back_button = ttk.Button(header_frame, text="< Back", command=lambda: self.show_view_callback("events"))
        back_button.grid(row=0, column=0, sticky="w", padx=5, pady=10)

        title_label = ttk.Label(header_frame, text="All Client Events", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=1, sticky="w", padx=5, pady=10)

        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.load_all_events)
        refresh_button.grid(row=0, column=2, padx=5, pady=10)

        events_frame = ttk.LabelFrame(self, text="Client Events")
        events_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        events_frame.columnconfigure(0, weight=1)
        events_frame.rowconfigure(0, weight=1)

        self.events_tree = ttk.Treeview(
            events_frame,
            columns=("id", "event_type", "ip_address", "port", "timestamp"),
            show="headings",
            selectmode="browse"
        )
        self.events_tree.heading("id", text="ID")
        self.events_tree.heading("event_type", text="Event Type")
        self.events_tree.heading("ip_address", text="IP Address")
        self.events_tree.heading("port", text="Port")
        self.events_tree.heading("timestamp", text="Timestamp")

        self.events_tree.column("id", width=50)
        self.events_tree.column("event_type", width=100)
        self.events_tree.column("ip_address", width=120)
        self.events_tree.column("port", width=70)
        self.events_tree.column("timestamp", width=150)

        self.events_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(events_frame, orient="vertical", command=self.events_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.events_tree.configure(yscrollcommand=scrollbar.set)

        # Pagination controls
        pagination_frame = ttk.Frame(self)
        pagination_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        pagination_frame.columnconfigure(1, weight=1)

        self.prev_page_btn = ttk.Button(pagination_frame, text="Previous", command=self.prev_page)
        self.prev_page_btn.grid(row=0, column=0, padx=5)

        self.page_label = ttk.Label(pagination_frame, text="Page 1")
        self.page_label.grid(row=0, column=1, padx=5)

        self.next_page_btn = ttk.Button(pagination_frame, text="Next", command=self.next_page)
        self.next_page_btn.grid(row=0, column=2, padx=5)

        status_label = ttk.Label(pagination_frame, textvariable=self.status_var)
        status_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=5)

    def load_all_events(self):
        """Load events for the current page."""
        self.status_var.set("Loading client events...")
        threading.Thread(target=self._fetch_all_events, daemon=True).start()

    def _fetch_all_events(self):
        """Fetch events from the API for the current page."""
        skip = self.page * self.page_size
        events = self.api_client.get_all_events_by_client(self.client_id, skip=skip, limit=self.page_size)
        if events:
            self.after(0, lambda: self._update_event_list(events))
            self.after(0, lambda: self.status_var.set(f"Loaded {len(events)} client events"))
        else:
            self.after(0, lambda: self.status_var.set("No more events to load"))

    def _update_event_list(self, events):
        """Update the events treeview with the fetched data."""
        for row in self.events_tree.get_children():
            self.events_tree.delete(row)

        for event in events:
            # Convert timestamp to datetime if it's a string
            timestamp = event.timestamp
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    timestamp = None

            # Format the timestamp for display
            formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else "N/A"

            # Insert the event into the treeview
            self.events_tree.insert("", "end", values=(
                event.id,
                event.event_type,
                event.ip_address,
                event.port,
                formatted_timestamp
            ))

        # Update pagination controls
        self.update_pagination(len(events))

    def update_pagination(self, events_count):
        """Update the pagination controls based on the current page and events count."""
        self.page_label.config(text=f"Page {self.page + 1}")

        # Enable/disable previous button
        if self.page > 0:
            self.prev_page_btn.state(["!disabled"])
        else:
            self.prev_page_btn.state(["disabled"])

        # Enable/disable next button
        if events_count < self.page_size:
            self.next_page_btn.state(["disabled"])
        else:
            self.next_page_btn.state(["!disabled"])

    def prev_page(self):
        """Go to the previous page."""
        if self.page > 0:
            self.page -= 1
            self.load_all_events()

    def next_page(self):
        """Go to the next page."""
        self.page += 1
        self.load_all_events()
