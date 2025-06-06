import tkinter as tk
from tkinter import ttk, messagebox
import threading
from common import Subscription
from dateutil.parser import parse

class TopicSubscriptionsView(ttk.Frame):
    def __init__(self, parent, api_client, topic_id, show_view_callback):
        super().__init__(parent)
        self.parent = parent
        self.api_client = api_client
        self.topic_id = topic_id
        self.show_view_callback = show_view_callback
        
        # Pagination variables
        self.page = 0
        self.page_size = 20
        
        # Setup UI components
        self.setup_ui()
        
        # Load initial data
        self.load_subscriptions()
    
    def setup_ui(self):
        # Configure the grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Header frame
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        header_frame.columnconfigure(1, weight=1)
        
        back_button = ttk.Button(header_frame, text="< Back", command=lambda: self.show_view_callback("topics"))
        back_button.grid(row=0, column=0, sticky="w", padx=5, pady=10)
        
        title_label = ttk.Label(header_frame, text=f"Subscriptions for Topic: {self.topic_id}", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        
        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.load_subscriptions)
        refresh_button.grid(row=0, column=2, padx=5, pady=10)
        
        # Subscriptions list frame
        list_frame = ttk.LabelFrame(self, text="Subscriptions")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Subscriptions table with scrollbar
        self.subscriptions_tree = ttk.Treeview(
            list_frame,
            columns=("id", "client_id", "subscribed_at", "active"),
            show="headings",
            selectmode="browse"
        )
        
        self.subscriptions_tree.heading("id", text="ID")
        self.subscriptions_tree.heading("client_id", text="Client ID")
        self.subscriptions_tree.heading("subscribed_at", text="Subscribed At")
        self.subscriptions_tree.heading("active", text="Active")
        
        self.subscriptions_tree.column("id", width=50)
        self.subscriptions_tree.column("client_id", width=200)
        self.subscriptions_tree.column("subscribed_at", width=150)
        self.subscriptions_tree.column("active", width=80)
        
        self.subscriptions_tree.grid(row=0, column=0, sticky="nsew")
        
        # Add scrollbar to treeview
        tree_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.subscriptions_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        self.subscriptions_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Pagination frame
        pagination_frame = ttk.Frame(list_frame)
        pagination_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.prev_page_btn = ttk.Button(pagination_frame, text="Previous", command=self.prev_page)
        self.prev_page_btn.grid(row=0, column=0, padx=5)
        
        self.page_label = ttk.Label(pagination_frame, text="Page 1")
        self.page_label.grid(row=0, column=1, padx=5)
        
        self.next_page_btn = ttk.Button(pagination_frame, text="Next", command=self.next_page)
        self.next_page_btn.grid(row=0, column=2, padx=5)

        # Status bar
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky="w")
    
    def load_subscriptions(self):
        """Loads subscriptions data from API"""
        skip = self.page * self.page_size
        threading.Thread(target=self._fetch_subscriptions, args=(skip,), daemon=True).start()
    
    def _fetch_subscriptions(self, skip):
        """Background thread to fetch subscriptions from API"""
        try:
            subscriptions = self.api_client.get_subscriptions_by_topic(self.topic_id, skip=skip, limit=self.page_size)
            self.after(0, lambda: self._update_subscriptions_list(subscriptions))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to load subscriptions: {e}"))
    
    def _update_subscriptions_list(self, subscriptions):
        """Updates the subscriptions list treeview with fetched data"""
        # Clear existing items
        for item in self.subscriptions_tree.get_children():
            self.subscriptions_tree.delete(item)

        # parse dates and format them
        for sub in subscriptions:
            if isinstance(sub.subscribed_at, str):
                sub.subscribed_at = parse(sub.subscribed_at).strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(sub.active, bool):
                sub.active = "Yes" if sub.active else "No"
        
        # Add subscriptions to treeview
        for sub in subscriptions:
            self.subscriptions_tree.insert(
                "", "end", 
                values=(sub.id, sub.client_id, sub.subscribed_at, sub.active)
            )
        
        # update status 
        if subscriptions:
            self.status_var.set(f"Loaded {len(subscriptions)} subscriptions.")
        else:
            self.status_var.set("No subscriptions found.")
        
        # Update pagination
        self.update_pagination(len(subscriptions))
    
    def update_pagination(self, item_count):
        """Updates pagination controls"""
        self.page_label.config(text=f"Page {self.page + 1}")
        self.prev_page_btn.state(["disabled"] if self.page == 0 else ["!disabled"])
        self.next_page_btn.state(["disabled"] if item_count < self.page_size else ["!disabled"])
    
    def prev_page(self):
        """Go to previous page of subscriptions"""
        if self.page > 0:
            self.page -= 1
            self.load_subscriptions()
    
    def next_page(self):
        """Go to next page of subscriptions"""
        self.page += 1
        self.load_subscriptions()
