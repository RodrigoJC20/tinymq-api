import tkinter as tk
from tkinter import ttk, messagebox
import threading
from common import Topic

class ClientTopicsView(ttk.Frame):
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
        self.load_topics()
    
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
        
        title_label = ttk.Label(header_frame, text=f"Topics for Client: {self.client_id}", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        
        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.load_topics)
        refresh_button.grid(row=0, column=2, padx=5, pady=10)
        
        # Topics list frame
        list_frame = ttk.LabelFrame(self, text="Topics")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Topics table with scrollbar
        self.topics_tree = ttk.Treeview(
            list_frame,
            columns=("id", "name", "created_at"),
            show="headings",
            selectmode="browse"
        )
        
        self.topics_tree.heading("id", text="ID")
        self.topics_tree.heading("name", text="Name")
        self.topics_tree.heading("created_at", text="Created At")
        
        self.topics_tree.column("id", width=50)
        self.topics_tree.column("name", width=200)
        self.topics_tree.column("created_at", width=150)
        
        self.topics_tree.grid(row=0, column=0, sticky="nsew")
        
        # Add scrollbar to treeview
        tree_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.topics_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        self.topics_tree.configure(yscrollcommand=tree_scrollbar.set)
        
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

        ttk.Label(client_details_frame, text="Topic Count:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.detail_topic_count = ttk.Label(client_details_frame, text="")
        self.detail_topic_count.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Update topic count
        self.update_topic_count()

    def load_topics(self):
        """Loads topics data from API"""
        skip = self.page * self.page_size
        threading.Thread(target=self._fetch_topics, args=(skip,), daemon=True).start()
    
    def _fetch_topics(self, skip):
        """Background thread to fetch topics from API"""
        try:
            topics = self.api_client.get_topics_by_client(self.client_id, skip=skip, limit=self.page_size)
            self.after(0, lambda: self._update_topics_list(topics))
        except Exception as e:
            error_message = str(e)  # Capture the error message
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to load topics: {error_message}"))
    
    def _update_topics_list(self, topics):
        """Updates the topics list treeview with fetched data"""
        # Clear existing items
        for item in self.topics_tree.get_children():
            self.topics_tree.delete(item)
        
        # Add topics to treeview
        for topic in topics:
            self.topics_tree.insert(
                "", "end", 
                values=(topic.id, topic.name, topic.created_at)
            )
        
        # Update pagination
        self.update_pagination(len(topics))
    
    def update_pagination(self, item_count):
        """Updates pagination controls"""
        self.page_label.config(text=f"Page {self.page + 1}")
        self.prev_page_btn.state(["disabled"] if self.page == 0 else ["!disabled"])
        self.next_page_btn.state(["disabled"] if item_count < self.page_size else ["!disabled"])
    
    def prev_page(self):
        """Go to previous page of topics"""
        if self.page > 0:
            self.page -= 1
            self.load_topics()
    
    def next_page(self):
        """Go to next page of topics"""
        self.page += 1
        self.load_topics()

    def update_topic_count(self):
        """Fetch and update the topic count for the client."""
        threading.Thread(target=self._fetch_topic_count, daemon=True).start()

    def _fetch_topic_count(self):
        try:
            topics = self.api_client.get_topics_by_client(self.client_id)
            self.after(0, lambda: self.detail_topic_count.config(text=str(len(topics))))
        except Exception as e:
            print(f"Error fetching topic count: {e}")
            self.after(0, lambda: self.detail_topic_count.config(text="Error"))
