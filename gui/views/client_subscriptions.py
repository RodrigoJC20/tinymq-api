import tkinter as tk
from tkinter import ttk, messagebox
import threading
from common import Subscription

class ClientSubscriptionsView(ttk.Frame):
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
        self.load_subscriptions()
    
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
        
        title_label = ttk.Label(header_frame, text=f"Subscriptions for Client: {self.client_id}", font=("Helvetica", 16, "bold"))
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
            columns=("id", "topic_id", "topic_name", "subscribed_at", "active"),
            show="headings",
            selectmode="browse"
        )
        
        self.subscriptions_tree.heading("id", text="ID")
        self.subscriptions_tree.heading("topic_id", text="Topic ID")
        self.subscriptions_tree.heading("topic_name", text="Topic Name")
        self.subscriptions_tree.heading("subscribed_at", text="Subscribed At")
        self.subscriptions_tree.heading("active", text="Active")
        
        self.subscriptions_tree.column("id", width=50)
        self.subscriptions_tree.column("topic_id", width=100)
        self.subscriptions_tree.column("topic_name", width=200)
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
        
        # Client details frame
        client_details_frame = ttk.LabelFrame(self, text="Client Details")
        client_details_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=10) 
        client_details_frame.columnconfigure(1, weight=1)

        ttk.Label(client_details_frame, text="Client ID:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.detail_client_id = ttk.Label(client_details_frame, text=self.client_id)
        self.detail_client_id.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(client_details_frame, text="Subscription Count:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.detail_subscription_count = ttk.Label(client_details_frame, text="")
        self.detail_subscription_count.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Update subscription count
        self.update_subscription_count()

    def load_subscriptions(self):
        """Loads subscriptions data from API"""
        skip = self.page * self.page_size
        threading.Thread(target=self._fetch_subscriptions, args=(skip,), daemon=True).start()
    
    def _fetch_subscriptions(self, skip):
        """Background thread to fetch subscriptions from API"""
        try:
            subscriptions = self.api_client.get_subscriptions_by_client(self.client_id, skip=skip, limit=self.page_size)
            self.after(0, lambda: self._update_subscriptions_list(subscriptions))
        except Exception as e:
            print(f"Error loading subscriptions: {str(e)}")
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to load subscriptions: {str(e)}"))
    
    def _update_subscriptions_list(self, subscriptions):
        """Updates the subscriptions list treeview with fetched data"""
        # Clear existing items
        for item in self.subscriptions_tree.get_children():
            self.subscriptions_tree.delete(item)
        
        # Add subscriptions to treeview
        for sub in subscriptions:
            self.subscriptions_tree.insert(
                "", "end", 
                values=(sub.id, sub.topic_id, sub.topic_name, sub.subscribed_at, sub.active)
            )
        
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

    def update_subscription_count(self):
        """Fetch and update the subscription count for the client."""
        threading.Thread(target=self._fetch_subscription_count, daemon=True).start()

    def _fetch_subscription_count(self):
        try:
            subscriptions = self.api_client.get_subscriptions_by_client(self.client_id)
            self.after(0, lambda: self.detail_subscription_count.config(text=str(len(subscriptions))))
        except Exception as e:
            print(f"Error fetching subscription count: {e}")
            self.after(0, lambda: self.detail_subscription_count.config(text="Error"))
