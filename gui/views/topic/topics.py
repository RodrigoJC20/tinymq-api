import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from gui.api_client import ApiClient
from common import Topic, Client

class TopicsView(ttk.Frame):
    def __init__(self, parent, api_client, show_view_callback):
        super().__init__(parent)
        self.parent = parent
        self.api_client = api_client
        self.show_view_callback = show_view_callback
        
        # Pagination variables
        self.page = 0
        self.page_size = 20
        self.total_topics = 0
        
        # Selected topic for details
        self.selected_topic = None
        
        # Auto-refresh variables
        self.auto_refresh_job = None
        self.is_refreshing = False
        
        # Setup UI components
        self.setup_ui()
        
        # Load initial data
        self.load_topics()
        
        # Start auto-refresh
        self.start_auto_refresh()
    
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
        
        title_label = ttk.Label(header_frame, text="TinyMQ Topics", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        
        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.load_topics)
        refresh_button.grid(row=0, column=2, padx=5, pady=10)
        
        # Main content - split into top topic list and bottom topic details
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=3)  # Topic list gets more space
        content_frame.rowconfigure(1, weight=2)  # Topic details gets less space
        
        # Topic list frame with Treeview
        list_frame = ttk.LabelFrame(content_frame, text="Topic List")
        list_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Topics table with scrollbar
        self.topics_tree = ttk.Treeview(
            list_frame,
            columns=("id", "name", "owner_client_id", "created_at"),
            show="headings",
            selectmode="browse"
        )
        
        self.topics_tree.heading("id", text="ID")
        self.topics_tree.heading("name", text="Topic Name")
        self.topics_tree.heading("owner_client_id", text="Owner Client")
        self.topics_tree.heading("created_at", text="Created At")
        
        self.topics_tree.column("id", width=50)
        self.topics_tree.column("name", width=250)
        self.topics_tree.column("owner_client_id", width=200)
        self.topics_tree.column("created_at", width=150)
        
        self.topics_tree.grid(row=0, column=0, sticky="nsew")
        self.topics_tree.bind("<<TreeviewSelect>>", self.on_topic_selected)
        
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
        
        # Topic details frame
        details_frame = ttk.LabelFrame(content_frame, text="Topic Details")
        details_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        details_frame.columnconfigure(1, weight=1)
        
        # Topic details content
        ttk.Label(details_frame, text="Topic ID:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.detail_topic_id = ttk.Label(details_frame, text="")
        self.detail_topic_id.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Topic Name:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.detail_name = ttk.Label(details_frame, text="")
        self.detail_name.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Owner Client:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.detail_owner = ttk.Label(details_frame, text="")
        self.detail_owner.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Created At:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.detail_created_at = ttk.Label(details_frame, text="")
        self.detail_created_at.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        # Subscription count (will be fetched when a topic is selected)
        ttk.Label(details_frame, text="Subscriptions:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.detail_subscription_count = ttk.Label(details_frame, text="")
        self.detail_subscription_count.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        
        # Action buttons
        action_frame = ttk.Frame(details_frame)
        action_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        view_subscriptions_btn = ttk.Button(
            action_frame, 
            text="View Subscriptions", 
            command=lambda: self.show_view_callback("topic_subscriptions", topic_id=self.selected_topic.id)
        )
        view_subscriptions_btn.grid(row=0, column=0, padx=5)
        
        view_messages_btn = ttk.Button(
            action_frame, 
            text="View Messages", 
            command=lambda: self.show_view_callback("topic_messages", topic_id=self.selected_topic.id)
        )
        view_messages_btn.grid(row=0, column=1, padx=5)
        
        view_owner_btn = ttk.Button(
            action_frame, 
            text="View Owner Client", 
            command=lambda: self.show_view_callback("topic_client", topic_id=self.selected_topic.id)
        )
        view_owner_btn.grid(row=0, column=2, padx=5)
        
        delete_btn = ttk.Button(
            action_frame, 
            text="Remove Topic", 
            command=self.delete_topic
        )
        delete_btn.grid(row=0, column=3, padx=5)
        
        # Status bar
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky="w")
        
        # Initially disable topic actions
        self.update_detail_buttons_state(False)
    
    def load_topics(self):
        """Loads topic data from API"""
        if not self.winfo_exists():
            return
            
        self.status_var.set("Loading topics...")
        self.update_idletasks()
        
        # Store currently selected topic ID to restore after refresh
        selected_topic_id = None
        if self.selected_topic:
            selected_topic_id = self.selected_topic.id
        
        # Calculate skip based on page and page size
        skip = self.page * self.page_size
        
        # Start loading in background thread
        threading.Thread(target=self._fetch_topics, args=(skip, selected_topic_id), daemon=True).start()
    
    def _fetch_topics(self, skip, selected_topic_id=None):
        """Background thread to fetch topics from API"""
        try:
            topics = self.api_client.get_topics(skip=skip, limit=self.page_size)
            
            if self.winfo_exists(): # Check if view still exists
                self.after(0, lambda: self._update_topic_list(topics, selected_topic_id))
                self.after(0, lambda: self.status_var.set(f"Loaded {len(topics)} topics"))
            
            if self.is_refreshing and self.winfo_exists():
                self.auto_refresh_job = threading.Timer(1.0, self.load_topics)
                self.auto_refresh_job.start()
                
        except Exception as e:
            print(f"Error loading topics: {str(e)}")
            if self.winfo_exists(): # Check if view still exists
                self.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to load topics: {str(e)}"))
            
            if self.is_refreshing and self.winfo_exists():
                self.auto_refresh_job = threading.Timer(1.0, self.load_topics)
                self.auto_refresh_job.start()
    
    def _update_topic_list(self, topics, selected_topic_id=None):
        """Updates the topics treeview with data"""
        if not self.winfo_exists() or not hasattr(self, 'topics_tree') or not self.topics_tree.winfo_exists():
            return

        for row in self.topics_tree.get_children():
            self.topics_tree.delete(row)
        
        item_to_select = None
        for topic in topics:
            created_at = topic.created_at
            if created_at:
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    except ValueError:
                        pass
                if isinstance(created_at, datetime):
                    created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
            
            item = self.topics_tree.insert(
                "", "end", 
                values=(topic.id, topic.name, topic.owner_client_id, created_at)
            )
            if selected_topic_id and topic.id == selected_topic_id:
                item_to_select = item
        
        if item_to_select and self.topics_tree.exists(item_to_select):
            self.topics_tree.selection_set(item_to_select)
            self.topics_tree.focus(item_to_select)
            
        if self.winfo_exists(): # Check before updating status and pagination
            if topics:
                self.status_var.set(f"Loaded {len(topics)} topics")
            else:
                self.status_var.set("No topics found")
            self.update_pagination()
    
    def update_pagination(self):
        """Update pagination controls based on current page"""
        if not self.winfo_exists():
            return
        if hasattr(self, 'page_label') and self.page_label.winfo_exists():
            self.page_label.config(text=f"Page {self.page + 1}")
        
        if hasattr(self, 'prev_page_btn') and self.prev_page_btn.winfo_exists():
            if self.page > 0:
                self.prev_page_btn.state(["!disabled"])
            else:
                self.prev_page_btn.state(["disabled"])
            
        if hasattr(self, 'next_page_btn') and self.next_page_btn.winfo_exists() and hasattr(self, 'topics_tree') and self.topics_tree.winfo_exists():
            children_count = len(self.topics_tree.get_children())
            if children_count < self.page_size:
                self.next_page_btn.state(["disabled"])
            else:
                self.next_page_btn.state(["!disabled"])
    
    def prev_page(self):
        """Go to previous page of topics"""
        if self.page > 0:
            self.page -= 1
            self.load_topics()
    
    def next_page(self):
        """Go to next page of topics"""
        self.page += 1
        self.load_topics()
    
    def on_topic_selected(self, event):
        """Handle topic selection in treeview"""
        selected_items = self.topics_tree.selection()
        if selected_items:
            # Get topic ID from the first column of the selected row
            item_values = self.topics_tree.item(selected_items[0], "values")
            topic_id = int(item_values[0])
            
            # Fetch topic details in background
            self.status_var.set("Loading topic details...")
            threading.Thread(target=self._fetch_topic_details, args=(topic_id,), daemon=True).start()
        else:
            self.clear_topic_details()
    
    def _fetch_topic_details(self, topic_id):
        """Background thread to fetch topic details"""
        try:
            topic = self.api_client.get_topic(topic_id)
            
            if self.winfo_exists(): # Check if view still exists
                if topic:
                    subscriptions = self.api_client.get_subscriptions_by_topic(topic_id)
                    subscription_count = len(subscriptions)
                    self.after(0, lambda: self.update_topic_details(topic, subscription_count))
                else:
                    self.after(0, lambda: self.status_var.set("Failed to load topic details"))
        except Exception as e:
            print(f"Error fetching topic details: {e}")
            if self.winfo_exists():
                 self.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
    
    def update_topic_details(self, topic, subscription_count):
        """Update the topic details panel with topic data"""
        if not self.winfo_exists():
            return
        self.selected_topic = topic
        created_at = topic.created_at
        if created_at:
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except ValueError:
                    pass
            if isinstance(created_at, datetime):
                created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
        
        if hasattr(self, 'detail_topic_id') and self.detail_topic_id.winfo_exists():
            self.detail_topic_id.config(text=str(topic.id))
        if hasattr(self, 'detail_name') and self.detail_name.winfo_exists():
            self.detail_name.config(text=topic.name)
        if hasattr(self, 'detail_owner') and self.detail_owner.winfo_exists():
            self.detail_owner.config(text=topic.owner_client_id)
        if hasattr(self, 'detail_created_at') and self.detail_created_at.winfo_exists():
            self.detail_created_at.config(text=created_at or "Unknown")
        if hasattr(self, 'detail_subscription_count') and self.detail_subscription_count.winfo_exists():
            self.detail_subscription_count.config(text=str(subscription_count))
        
        self.update_detail_buttons_state(True)
        if hasattr(self, 'status_var'):  # Removed .winfo_exists()
            self.status_var.set("Topic details loaded")
    
    def clear_topic_details(self):
        """Clear the topic details panel"""
        if not self.winfo_exists():
            return
        if hasattr(self, 'detail_topic_id') and self.detail_topic_id.winfo_exists():
            self.detail_topic_id.config(text="")
        if hasattr(self, 'detail_name') and self.detail_name.winfo_exists():
            self.detail_name.config(text="")
        if hasattr(self, 'detail_owner') and self.detail_owner.winfo_exists():
            self.detail_owner.config(text="")
        if hasattr(self, 'detail_created_at') and self.detail_created_at.winfo_exists():
            self.detail_created_at.config(text="")
        if hasattr(self, 'detail_subscription_count') and self.detail_subscription_count.winfo_exists():
            self.detail_subscription_count.config(text="")
        self.update_detail_buttons_state(False)
    
    def update_detail_buttons_state(self, enabled):
        """Enable or disable the detail action buttons"""
        state = ["!disabled"] if enabled else ["disabled"]
        
        # Get reference to action frame directly
        try:
            # Find the action frame which is in the details frame
            content_frame = self.winfo_children()[1]  # This should be the content_frame
            if content_frame and hasattr(content_frame, 'winfo_children'):
                details_frame = None
                # Look for details_frame (LabelFrame with text "Topic Details")
                for child in content_frame.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Topic Details":
                        details_frame = child
                        break
                
                if details_frame:
                    # Look for the action_frame which is a regular Frame in the details_frame
                    for child in details_frame.winfo_children():
                        if isinstance(child, ttk.Frame):
                            # This should be the action_frame
                            for button in child.winfo_children():
                                if isinstance(button, ttk.Button):
                                    button.state(state)
        except (IndexError, AttributeError) as e:
            print(f"Error updating button states: {e}")
            # If there's an error, fail silently - the buttons just won't be enabled/disabled
    
    def view_topic_subscriptions(self):
        """View subscriptions for the selected topic"""
        if self.selected_topic:
            # TODO: Implement view transition to subscriptions filtered by this topic
            messagebox.showinfo("View Subscriptions", 
                               f"View subscriptions for topic '{self.selected_topic.name}'\n"
                               f"This feature is not yet implemented.")
    
    def view_topic_messages(self):
        """View messages for the selected topic"""
        if self.selected_topic:
            # TODO: Implement view transition to messages filtered by this topic
            messagebox.showinfo("View Messages", 
                               f"View messages for topic '{self.selected_topic.name}'\n"
                               f"This feature is not yet implemented.")
    
    def view_owner_client(self):
        """View the owner client of this topic"""
        if self.selected_topic:
            # TODO: Implement view transition to client details
            messagebox.showinfo("View Owner", 
                               f"View client '{self.selected_topic.owner_client_id}'\n"
                               f"This feature is not yet implemented.")
    
    def delete_topic(self):
        """Delete the selected topic"""
        if not self.selected_topic:
            return
            
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete topic '{self.selected_topic.name}'?\n"
            "This will also delete all associated subscriptions and message logs.",
            icon="warning"
        )
        
        if confirm:
            self.status_var.set("Deleting topic...")
            threading.Thread(target=self._delete_topic_thread, daemon=True).start()
    
    def _delete_topic_thread(self):
        """Background thread to delete a topic"""
        if not self.selected_topic:
            return
            
        success = self.api_client.delete_topic(self.selected_topic.id)
        
        if success:
            # Reload topics after deletion
            self.after(0, lambda: self.status_var.set(f"Topic '{self.selected_topic.name}' deleted successfully"))
            self.after(0, self.load_topics)
        else:
            self.after(0, lambda: messagebox.showerror(
                "Delete Failed", 
                f"Failed to delete topic '{self.selected_topic.name}'"
            ))
            self.after(0, lambda: self.status_var.set("Delete failed"))

    def start_auto_refresh(self):
        """Start auto-refresh job"""
        if not self.is_refreshing:
            self.is_refreshing = True
            self._schedule_auto_refresh()

    def _schedule_auto_refresh(self):
        """Schedule the next auto-refresh"""
        if self.is_refreshing and self.winfo_exists():
            self.after(1000, self.load_topics)  # Schedule load_topics to run every 1 second

    def stop_auto_refresh(self):
        """Stop auto-refresh job"""
        self.is_refreshing = False
    
    def on_destroy(self):
        """Called when the view is being destroyed"""
        self.stop_auto_refresh()