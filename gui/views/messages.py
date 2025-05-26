import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from gui.api_client import ApiClient
from common import MessageLog, Topic, Client

class MessagesView(ttk.Frame):
    def __init__(self, parent, api_client, show_view_callback):
        super().__init__(parent)
        self.parent = parent
        self.api_client = api_client
        self.show_view_callback = show_view_callback
        
        # Pagination variables
        self.page = 0
        self.page_size = 20
        self.total_messages = 0
        
        # Selected message for details
        self.selected_message = None
        
        # Auto-refresh variables
        self.auto_refresh_job = None
        self.is_refreshing = False
        
        # Setup UI components
        self.setup_ui()
        
        # Load initial data
        self.load_messages()
        
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
        
        title_label = ttk.Label(header_frame, text="TinyMQ Message Logs", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        
        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.load_messages)
        refresh_button.grid(row=0, column=2, padx=5, pady=10)
        
        # Main content - split into top message list and bottom message details
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=3)  # Message list gets more space
        content_frame.rowconfigure(1, weight=2)  # Message details gets less space
        
        # Message list frame with Treeview
        list_frame = ttk.LabelFrame(content_frame, text="Message List")
        list_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Messages table with scrollbar
        self.messages_tree = ttk.Treeview(
            list_frame,
            columns=("id", "publisher", "topic", "published_at", "size"),
            show="headings",
            selectmode="browse"
        )
        
        self.messages_tree.heading("id", text="ID")
        self.messages_tree.heading("publisher", text="Publisher")
        self.messages_tree.heading("topic", text="Topic")
        self.messages_tree.heading("published_at", text="Published At")
        self.messages_tree.heading("size", text="Size (bytes)")
        
        self.messages_tree.column("id", width=50)
        self.messages_tree.column("publisher", width=180)
        self.messages_tree.column("topic", width=180)
        self.messages_tree.column("published_at", width=150)
        self.messages_tree.column("size", width=100)
        
        self.messages_tree.grid(row=0, column=0, sticky="nsew")
        self.messages_tree.bind("<<TreeviewSelect>>", self.on_message_selected)
        
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
        
        # Message details frame
        details_frame = ttk.LabelFrame(content_frame, text="Message Details")
        details_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        details_frame.columnconfigure(1, weight=1)
        
        # Message details content
        ttk.Label(details_frame, text="Message ID:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.detail_msg_id = ttk.Label(details_frame, text="")
        self.detail_msg_id.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Publisher:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.detail_publisher = ttk.Label(details_frame, text="")
        self.detail_publisher.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Topic:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.detail_topic = ttk.Label(details_frame, text="")
        self.detail_topic.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Topic ID:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.detail_topic_id = ttk.Label(details_frame, text="")
        self.detail_topic_id.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Published At:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.detail_published_at = ttk.Label(details_frame, text="")
        self.detail_published_at.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Payload Size:").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        self.detail_payload_size = ttk.Label(details_frame, text="")
        self.detail_payload_size.grid(row=5, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Payload Preview:").grid(row=6, column=0, sticky="ne", padx=5, pady=2)
        
        # Frame for payload preview with scrollbars
        payload_frame = ttk.Frame(details_frame)
        payload_frame.grid(row=6, column=1, sticky="nsew", padx=5, pady=2)
        payload_frame.columnconfigure(0, weight=1)
        payload_frame.rowconfigure(0, weight=1)
        
        # Text widget for payload preview (read-only)
        self.payload_text = tk.Text(payload_frame, height=4, width=40, wrap="word", state="disabled")
        self.payload_text.grid(row=0, column=0, sticky="nsew")
        
        payload_scrollbar = ttk.Scrollbar(payload_frame, orient="vertical", command=self.payload_text.yview)
        payload_scrollbar.grid(row=0, column=1, sticky="ns")
        self.payload_text.configure(yscrollcommand=payload_scrollbar.set)
        
        # Action buttons
        action_frame = ttk.Frame(details_frame)
        action_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        view_publisher_btn = ttk.Button(
            action_frame, 
            text="View Publisher", 
            command=self.view_publisher
        )
        view_publisher_btn.grid(row=0, column=0, padx=5)
        
        view_topic_btn = ttk.Button(
            action_frame, 
            text="View Topic", 
            command=self.view_topic
        )
        view_topic_btn.grid(row=0, column=1, padx=5)
        
        # Status bar
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky="w")
        
        # Initially disable message actions
        self.update_detail_buttons_state(False)
    
    def load_messages(self):
        """Loads message data from API"""
        if not self.winfo_exists():
            return
            
        self.status_var.set("Loading messages...")
        self.update_idletasks()
        
        # Clear selected message only if this is not an auto-refresh
        if not hasattr(self, '_auto_refresh_in_progress'):
            self.selected_message = None
            self.clear_message_details()
        
        # Calculate skip based on page and page size
        skip = self.page * self.page_size
        
        # Start loading in background thread
        threading.Thread(target=self._fetch_messages, args=(skip,), daemon=True).start()
    
    def _fetch_messages(self, skip):
        """Background thread to fetch messages from API"""
        try:
            messages = self.api_client.get_messages(skip=skip, limit=self.page_size)
            
            if self.winfo_exists(): # Check if view still exists
                self.after(0, lambda: self._update_message_list(messages))
                self.after(0, lambda: self.status_var.set(f"Loaded {len(messages)} messages"))
            
            if self.is_refreshing and self.winfo_exists():
                self.auto_refresh_job = threading.Timer(1.0, self.load_messages)
                self.auto_refresh_job.start()
                
        except Exception as e:
            print(f"Error loading messages: {str(e)}")
            if self.winfo_exists(): # Check if view still exists
                self.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to load messages: {str(e)}"))
            
            if self.is_refreshing and self.winfo_exists():
                self.auto_refresh_job = threading.Timer(1.0, self.load_messages)
                self.auto_refresh_job.start()
    
    def _update_message_list(self, messages):
        """Updates the messages treeview with data"""
        if not self.winfo_exists() or not hasattr(self, 'messages_tree') or not self.messages_tree.winfo_exists():
            return
        try:
            for row in self.messages_tree.get_children():
                self.messages_tree.delete(row)
            for msg in messages:
                published_at = msg.published_at
                if published_at:
                    if isinstance(published_at, str):
                        try:
                            published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        except ValueError:
                            pass
                    if isinstance(published_at, datetime):
                        published_at = published_at.strftime("%Y-%m-%d %H:%M:%S")
                topic_name = getattr(msg, 'topic_name', str(msg.topic_id))
                self.messages_tree.insert(
                    "", "end", 
                    values=(msg.id, msg.publisher_client_id, topic_name, published_at, msg.payload_size)
                )
            if self.winfo_exists(): # Check before updating status and pagination
                if hasattr(self, 'status_var') and self.status_var.winfo_exists():
                    if messages:
                        self.status_var.set(f"Loaded {len(messages)} messages")
                    else:
                        self.status_var.set("No messages found")
                self.update_pagination()
        except tk.TclError as e:
            print(f"Tk error updating message list: {e}")
        except Exception as e:
            print(f"Error updating message list: {e}")
    
    def update_pagination(self):
        """Update pagination controls based on current page"""
        if not self.winfo_exists():
            return
        try:
            if hasattr(self, 'page_label') and self.page_label.winfo_exists():
                self.page_label.config(text=f"Page {self.page + 1}")
            if hasattr(self, 'prev_page_btn') and self.prev_page_btn.winfo_exists():
                if self.page > 0:
                    self.prev_page_btn.state(["!disabled"])
                else:
                    self.prev_page_btn.state(["disabled"])
            if hasattr(self, 'next_page_btn') and self.next_page_btn.winfo_exists() and hasattr(self, 'messages_tree') and self.messages_tree.winfo_exists():
                client_count = len(self.messages_tree.get_children())
                if client_count < self.page_size:
                    self.next_page_btn.state(["disabled"])
                else:
                    self.next_page_btn.state(["!disabled"])
        except tk.TclError as e:
            print(f"Tk error updating pagination: {e}")
        except Exception as e:
            print(f"Error updating pagination: {e}")
    
    def prev_page(self):
        """Go to previous page of messages"""
        if self.page > 0:
            self.page -= 1
            self.load_messages()
    
    def next_page(self):
        """Go to next page of messages"""
        self.page += 1
        self.load_messages()
    
    def on_message_selected(self, event):
        """Handle message selection in treeview"""
        selected_items = self.messages_tree.selection()
        if selected_items:
            # Get message ID from the first column of the selected row
            item_values = self.messages_tree.item(selected_items[0], "values")
            message_id = int(item_values[0])
            
            # Fetch message details in background
            self.status_var.set("Loading message details...")
            threading.Thread(target=self._fetch_message_details, args=(message_id,), daemon=True).start()
        else:
            self.clear_message_details()
            self.update_detail_buttons_state(False)
    
    def _fetch_message_details(self, message_id):
        """Background thread to fetch message details"""
        try:
            message = self.api_client.get_message(message_id)
            if self.winfo_exists(): # Check if view still exists
                if message:
                    self.after(0, lambda: self.update_message_details(message))
                else:
                    self.after(0, lambda: self.status_var.set("Failed to load message details"))
        except Exception as e:
            print(f"Error fetching message details: {e}")
            if self.winfo_exists():
                self.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
    
    def update_message_details(self, message):
        """Update the message details panel with message data"""
        if not self.winfo_exists():
            return
        self.selected_message = message
        published_at = message.published_at
        if published_at:
            if isinstance(published_at, str):
                try:
                    published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                except ValueError:
                    pass
            if isinstance(published_at, datetime):
                published_at = published_at.strftime("%Y-%m-%d %H:%M:%S")
        
        if hasattr(self, 'detail_msg_id') and self.detail_msg_id.winfo_exists():
            self.detail_msg_id.config(text=str(message.id))
        if hasattr(self, 'detail_publisher') and self.detail_publisher.winfo_exists():
            self.detail_publisher.config(text=message.publisher_client_id)
        topic_name = getattr(message, 'topic_name', "Unknown")
        if hasattr(self, 'detail_topic') and self.detail_topic.winfo_exists():
            self.detail_topic.config(text=topic_name)
        if hasattr(self, 'detail_topic_id') and self.detail_topic_id.winfo_exists():
            self.detail_topic_id.config(text=str(message.topic_id))
        if hasattr(self, 'detail_published_at') and self.detail_published_at.winfo_exists():
            self.detail_published_at.config(text=published_at or "Unknown")
        if hasattr(self, 'detail_payload_size') and self.detail_payload_size.winfo_exists():
            self.detail_payload_size.config(text=f"{message.payload_size} bytes")
        
        if hasattr(self, 'payload_text') and self.payload_text.winfo_exists():
            self.payload_text.config(state="normal")
            self.payload_text.delete(1.0, tk.END)
            if hasattr(message, 'payload_preview') and message.payload_preview:
                self.payload_text.insert(tk.END, message.payload_preview)
            else:
                self.payload_text.insert(tk.END, "(No payload preview available)")
            self.payload_text.config(state="disabled")
        
        self.update_detail_buttons_state(True)
        if hasattr(self, 'status_var') and self.status_var.winfo_exists():
            self.status_var.set("Message details loaded")
    
    def clear_message_details(self):
        """Clear the message details panel"""
        if not self.winfo_exists():
            return
        if hasattr(self, 'detail_msg_id') and self.detail_msg_id.winfo_exists():
            self.detail_msg_id.config(text="")
        if hasattr(self, 'detail_publisher') and self.detail_publisher.winfo_exists():
            self.detail_publisher.config(text="")
        if hasattr(self, 'detail_topic') and self.detail_topic.winfo_exists():
            self.detail_topic.config(text="")
        if hasattr(self, 'detail_topic_id') and self.detail_topic_id.winfo_exists():
            self.detail_topic_id.config(text="")
        if hasattr(self, 'detail_published_at') and self.detail_published_at.winfo_exists():
            self.detail_published_at.config(text="")
        if hasattr(self, 'detail_payload_size') and self.detail_payload_size.winfo_exists():
            self.detail_payload_size.config(text="")
        if hasattr(self, 'payload_text') and self.payload_text.winfo_exists():
            self.payload_text.config(state="normal")
            self.payload_text.delete(1.0, tk.END)
            self.payload_text.config(state="disabled")
        self.update_detail_buttons_state(False)
    
    def update_detail_buttons_state(self, enabled):
        """Enable or disable the detail action buttons"""
        state = ["!disabled"] if enabled else ["disabled"]
        
        # Get all buttons in the action frame
        action_frame = self.winfo_children()[1].winfo_children()[1].winfo_children()[7]
        for child in action_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.state(state)
    
    def view_publisher(self):
        """Navigate to the client details view for this message's publisher"""
        if self.selected_message:
            # This would normally transition to the client view
            # For now, just show a message
            messagebox.showinfo("View Publisher", 
                              f"View client '{self.selected_message.publisher_client_id}'\n"
                              f"This navigation feature is not yet implemented.")
    
    def view_topic(self):
        """Navigate to the topic details view for this message's topic"""
        if self.selected_message:
            # This would normally transition to the topic view
            # For now, just show a message
            topic_name = getattr(self.selected_message, 'topic_name', f"ID: {self.selected_message.topic_id}")
            messagebox.showinfo("View Topic", 
                              f"View topic '{topic_name}'\n"
                              f"This navigation feature is not yet implemented.")

    def start_auto_refresh(self):
        """Start auto-refresh"""
        self.is_refreshing = True
        self.load_messages()

    def stop_auto_refresh(self):
        """Stop auto-refresh"""
        self.is_refreshing = False
        if self.auto_refresh_job:
            self.auto_refresh_job.cancel()
        self.auto_refresh_job = None
    
    def on_destroy(self):
        """Called when the view is being destroyed"""
        self.stop_auto_refresh() 