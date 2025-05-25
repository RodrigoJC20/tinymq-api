import tkinter as tk
from tkinter import ttk, messagebox
import threading
from common import MessageLog

class ClientMessagesView(ttk.Frame):
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
        self.load_messages()
    
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
        
        title_label = ttk.Label(header_frame, text=f"Messages for Client: {self.client_id}", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        
        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.load_messages)
        refresh_button.grid(row=0, column=2, padx=5, pady=10)
        
        # Messages list frame
        list_frame = ttk.LabelFrame(self, text="Messages")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Messages table with scrollbar
        self.messages_tree = ttk.Treeview(
            list_frame,
            columns=("id", "topic_id", "payload_preview", "published_at"),
            show="headings",
            selectmode="browse"
        )
        
        self.messages_tree.heading("id", text="ID")
        self.messages_tree.heading("topic_id", text="Topic ID")
        self.messages_tree.heading("payload_preview", text="Payload Preview")
        self.messages_tree.heading("published_at", text="Published At")
        
        self.messages_tree.column("id", width=20)
        self.messages_tree.column("topic_id", width=20)
        self.messages_tree.column("payload_preview", width=300)
        self.messages_tree.column("published_at", width=150)
        
        self.messages_tree.grid(row=0, column=0, sticky="nsew")
        
        # Add scrollbar to treeview
        tree_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.messages_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        self.messages_tree.configure(yscrollcommand=tree_scrollbar.set)
        
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

        ttk.Label(client_details_frame, text="Message Count:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.detail_message_count = ttk.Label(client_details_frame, text="")
        self.detail_message_count.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Update message count
        self.update_message_count()

    def load_messages(self):
        """Loads messages data from API"""
        skip = self.page * self.page_size
        threading.Thread(target=self._fetch_messages, args=(skip,), daemon=True).start()
    
    def _fetch_messages(self, skip):
        """Background thread to fetch messages from API"""
        try:
            messages = self.api_client.get_messages_by_client(self.client_id, skip=skip, limit=self.page_size)
            self.after(0, lambda: self._update_messages_list(messages))
        except Exception as e:
            print(f"Error loading messages: {str(e)}")
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to load messages: {str(e)}"))
    
    def _update_messages_list(self, messages):
        """Updates the messages list treeview with fetched data"""
        # Clear existing items
        for item in self.messages_tree.get_children():
            self.messages_tree.delete(item)
        
        # Add messages to treeview
        for msg in messages:
            self.messages_tree.insert(
                "", "end", 
                values=(msg.id, msg.topic_id, msg.payload_preview or "N/A", msg.published_at)
            )
        
        # Update pagination
        self.update_pagination(len(messages))
    
    def update_pagination(self, item_count):
        """Updates pagination controls"""
        self.page_label.config(text=f"Page {self.page + 1}")
        self.prev_page_btn.state(["disabled"] if self.page == 0 else ["!disabled"])
        self.next_page_btn.state(["disabled"] if item_count < self.page_size else ["!disabled"])
    
    def prev_page(self):
        """Go to previous page of messages"""
        if self.page > 0:
            self.page -= 1
            self.load_messages()
    
    def next_page(self):
        """Go to next page of messages"""
        self.page += 1
        self.load_messages()

    def update_message_count(self):
        """Fetch and update the message count for the client."""
        threading.Thread(target=self._fetch_message_count, daemon=True).start()

    def _fetch_message_count(self):
        try:
            messages = self.api_client.get_messages_by_client(self.client_id)
            self.after(0, lambda: self.detail_message_count.config(text=str(len(messages))))
        except Exception as e:
            print(f"Error fetching message count: {e}")
            self.after(0, lambda: self.detail_message_count.config(text="Error"))
