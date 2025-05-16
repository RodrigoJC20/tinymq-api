import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from gui.api_client import ApiClient
from common import Client

class ClientsView(ttk.Frame):
    def __init__(self, parent, api_client, show_view_callback):
        super().__init__(parent)
        self.parent = parent
        self.api_client = api_client
        self.show_view_callback = show_view_callback
        
        # Pagination variables
        self.page = 0
        self.page_size = 20
        self.total_clients = 0
        
        # Selected client for details
        self.selected_client = None
        
        # Setup UI components
        self.setup_ui()
        
        # Load initial data
        self.load_clients()
    
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
        
        title_label = ttk.Label(header_frame, text="TinyMQ Connected Clients", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        
        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.load_clients)
        refresh_button.grid(row=0, column=2, padx=5, pady=10)
        
        # Main content - split into top client list and bottom client details
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=3)  # Client list gets more space
        content_frame.rowconfigure(1, weight=2)  # Client details gets less space
        
        # Client list frame with Treeview
        list_frame = ttk.LabelFrame(content_frame, text="Client List")
        list_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Clients table with scrollbar
        self.clients_tree = ttk.Treeview(
            list_frame,
            columns=("id", "client_id", "ip", "port", "last_connected", "count"),
            show="headings",
            selectmode="browse"
        )
        
        self.clients_tree.heading("id", text="ID")
        self.clients_tree.heading("client_id", text="Client ID")
        self.clients_tree.heading("ip", text="Last IP")
        self.clients_tree.heading("port", text="Last Port")
        self.clients_tree.heading("last_connected", text="Last Connected")
        self.clients_tree.heading("count", text="Connection Count")
        
        self.clients_tree.column("id", width=50)
        self.clients_tree.column("client_id", width=200)
        self.clients_tree.column("ip", width=120)
        self.clients_tree.column("port", width=80)
        self.clients_tree.column("last_connected", width=150)
        self.clients_tree.column("count", width=100)
        
        self.clients_tree.grid(row=0, column=0, sticky="nsew")
        self.clients_tree.bind("<<TreeviewSelect>>", self.on_client_selected)
        
        # Add scrollbar to treeview
        tree_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.clients_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        self.clients_tree.configure(yscrollcommand=tree_scrollbar.set)
        
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
        details_frame = ttk.LabelFrame(content_frame, text="Client Details")
        details_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        details_frame.columnconfigure(1, weight=1)
        
        # Client details content
        ttk.Label(details_frame, text="Client ID:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.detail_client_id = ttk.Label(details_frame, text="")
        self.detail_client_id.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Last IP:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.detail_ip = ttk.Label(details_frame, text="")
        self.detail_ip.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Last Port:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.detail_port = ttk.Label(details_frame, text="")
        self.detail_port.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Last Connected:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.detail_last_connected = ttk.Label(details_frame, text="")
        self.detail_last_connected.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Connection Count:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.detail_count = ttk.Label(details_frame, text="")
        self.detail_count.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        
        # Action buttons
        action_frame = ttk.Frame(details_frame)
        action_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        view_topics_btn = ttk.Button(
            action_frame, 
            text="View Topics", 
            command=self.view_client_topics
        )
        view_topics_btn.grid(row=0, column=0, padx=5)
        
        view_subscriptions_btn = ttk.Button(
            action_frame, 
            text="View Subscriptions", 
            command=self.view_client_subscriptions
        )
        view_subscriptions_btn.grid(row=0, column=1, padx=5)
        
        view_messages_btn = ttk.Button(
            action_frame, 
            text="View Messages", 
            command=self.view_client_messages
        )
        view_messages_btn.grid(row=0, column=2, padx=5)
        
        view_events_btn = ttk.Button(
            action_frame, 
            text="View Events", 
            command=self.view_client_events
        )
        view_events_btn.grid(row=0, column=3, padx=5)
        
        delete_btn = ttk.Button(
            action_frame, 
            text="Delete Client", 
            command=self.delete_client,
            style="Danger.TButton"  # This would need a custom style definition
        )
        delete_btn.grid(row=0, column=4, padx=5)
        
        # Status bar
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky="w")
        
        # Initially disable client actions
        self.update_detail_buttons_state(False)
    
    def load_clients(self):
        """Loads client data from API"""
        self.status_var.set("Loading clients...")
        self.update_idletasks()
        
        # Clear selected client
        self.selected_client = None
        self.clear_client_details()
        
        # Calculate skip based on page and page size
        skip = self.page * self.page_size
        
        # Start loading in background thread
        threading.Thread(target=self._fetch_clients, args=(skip,), daemon=True).start()
    
    def _fetch_clients(self, skip):
        """Background thread to fetch clients from API"""
        try:
            clients = self.api_client.get_clients(skip=skip, limit=self.page_size)
            
            # Update UI on main thread
            self.after(0, lambda: self._update_client_list(clients))
            self.after(0, lambda: self.status_var.set(f"Loaded {len(clients)} clients"))
            
        except Exception as e:
            print(f"Error loading clients: {str(e)}")
            self.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to load clients: {str(e)}"))
    
    def _update_client_list(self, clients):
        """Updates the client list treeview with fetched data"""
        # Clear existing items
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)
        
        # Add clients to treeview
        for client in clients:
            last_connected = client.last_connected.strftime("%Y-%m-%d %H:%M:%S") if client.last_connected else "N/A"
            
            self.clients_tree.insert(
                "", "end", 
                values=(
                    client.id, 
                    client.client_id, 
                    client.last_ip or "N/A", 
                    client.last_port or "N/A",
                    last_connected,
                    client.connection_count
                )
            )
        
        # Update pagination
        self.update_pagination()
    
    def update_pagination(self):
        """Updates pagination controls"""
        # Set page label
        self.page_label.config(text=f"Page {self.page + 1}")
        
        # Enable/disable pagination buttons based on page number
        self.prev_page_btn.state(["disabled"] if self.page == 0 else ["!disabled"])
        
        # Next button logic would depend on knowing total count, 
        # or checking if we received a full page of results
        client_count = len(self.clients_tree.get_children())
        self.next_page_btn.state(["disabled"] if client_count < self.page_size else ["!disabled"])
    
    def prev_page(self):
        """Go to previous page of clients"""
        if self.page > 0:
            self.page -= 1
            self.load_clients()
    
    def next_page(self):
        """Go to next page of clients"""
        self.page += 1
        self.load_clients()
    
    def on_client_selected(self, event):
        """Handle client selection in treeview"""
        selected_items = self.clients_tree.selection()
        if not selected_items:
            return
        
        # Get selected item
        selected_item = selected_items[0]
        values = self.clients_tree.item(selected_item, 'values')
        
        if not values:
            return
        
        # Get client ID from selected row
        client_id = values[1]
        
        # Start loading client details in background
        threading.Thread(target=self._fetch_client_details, args=(client_id,), daemon=True).start()
    
    def _fetch_client_details(self, client_id):
        """Background thread to fetch client details"""
        try:
            client = self.api_client.get_client(client_id)
            
            if client:
                # Store the selected client
                self.selected_client = client
                
                # Update UI on main thread
                self.after(0, lambda: self.update_client_details(client))
            else:
                self.after(0, lambda: self.status_var.set(f"Client not found: {client_id}"))
                self.after(0, lambda: self.clear_client_details())
                
        except Exception as e:
            print(f"Error loading client details: {str(e)}")
            self.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
    
    def update_client_details(self, client):
        """Updates the client details panel with selected client info"""
        self.detail_client_id.config(text=client.client_id)
        self.detail_ip.config(text=client.last_ip or "N/A")
        self.detail_port.config(text=str(client.last_port) if client.last_port else "N/A")
        self.detail_last_connected.config(
            text=client.last_connected.strftime("%Y-%m-%d %H:%M:%S") if client.last_connected else "N/A"
        )
        self.detail_count.config(text=str(client.connection_count))
        
        # Enable detail buttons
        self.update_detail_buttons_state(True)
    
    def clear_client_details(self):
        """Clears the client details panel"""
        self.detail_client_id.config(text="")
        self.detail_ip.config(text="")
        self.detail_port.config(text="")
        self.detail_last_connected.config(text="")
        self.detail_count.config(text="")
        
        # Disable detail buttons
        self.update_detail_buttons_state(False)
    
    def update_detail_buttons_state(self, enabled):
        """Updates state of detail action buttons"""
        state = ["!disabled"] if enabled else ["disabled"]
        
        for button in self.winfo_children()[1].winfo_children()[1].winfo_children()[1].winfo_children()[-1].winfo_children():
            if isinstance(button, ttk.Button):
                button.state(state)
    
    def delete_client(self):
        """Deletes the selected client"""
        if not self.selected_client:
            return
        
        if messagebox.askyesno(
            "Delete Client", 
            f"Are you sure you want to delete client '{self.selected_client.client_id}'?\n\nThis will also delete all associated topics, subscriptions, and messages!"
        ):
            threading.Thread(target=self._delete_client_thread, daemon=True).start()
    
    def _delete_client_thread(self):
        """Background thread for client deletion"""
        try:
            success = self.api_client.delete_client(self.selected_client.client_id)
            
            if success:
                self.after(0, lambda: self.status_var.set(f"Client '{self.selected_client.client_id}' deleted successfully"))
                self.after(0, self.load_clients)
            else:
                self.after(0, lambda: self.status_var.set(f"Failed to delete client"))
                self.after(0, lambda: messagebox.showerror("Error", "Failed to delete client."))
                
        except Exception as e:
            print(f"Error deleting client: {str(e)}")
            self.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to delete client: {str(e)}"))
    
    def view_client_topics(self):
        """Navigate to topics view filtered by client"""
        if not self.selected_client:
            return
        
        # This would require passing filter info to topics view
        messagebox.showinfo("Not Implemented", "View topics by client feature coming soon!")
    
    def view_client_subscriptions(self):
        """Navigate to subscriptions view filtered by client"""
        if not self.selected_client:
            return
        
        # This would require passing filter info to subscriptions view
        messagebox.showinfo("Not Implemented", "View subscriptions by client feature coming soon!")
    
    def view_client_messages(self):
        """Navigate to messages view filtered by client"""
        if not self.selected_client:
            return
        
        # This would require passing filter info to messages view
        messagebox.showinfo("Not Implemented", "View messages by client feature coming soon!")
    
    def view_client_events(self):
        """Navigate to events view filtered by client"""
        if not self.selected_client:
            return
        
        # This would require passing filter info to events view
        messagebox.showinfo("Not Implemented", "View events by client feature coming soon!") 