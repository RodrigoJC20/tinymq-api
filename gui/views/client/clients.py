import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os
from dateutil.parser import parse

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
        
        # Auto-refresh variables
        self.auto_refresh_job = None
        self.is_refreshing = False
        
        # Setup UI components
        self.setup_ui()
        
        # Load initial data
        self.load_clients()
        
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
            columns=("id", "active", "client_id", "ip", "port", "last_connected", "count"),
            show="headings",
            selectmode="browse"
        )
        
        self.clients_tree.heading("id", text="ID")
        self.clients_tree.heading("active", text="Active")
        self.clients_tree.heading("client_id", text="Client ID")
        self.clients_tree.heading("ip", text="Last IP")
        self.clients_tree.heading("port", text="Last Port")
        self.clients_tree.heading("last_connected", text="Last Connected")
        self.clients_tree.heading("count", text="Connection Count")
        
        self.clients_tree.column("id", width=50, anchor="center")
        self.clients_tree.column("active", width=50, anchor="center")
        self.clients_tree.column("client_id", width=200)
        self.clients_tree.column("ip", width=120)
        self.clients_tree.column("port", width=80)
        self.clients_tree.column("last_connected", width=150)
        self.clients_tree.column("count", width=100)
        
        self.clients_tree.grid(row=0, column=0, sticky="nsew")
        self.clients_tree.bind("<<TreeviewSelect>>", self.on_client_selected)
        
        # Configure tags for connection status (not just active status)
        self.clients_tree.tag_configure("connected", foreground="black")
        self.clients_tree.tag_configure("disconnected", foreground="gray")
        
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
        
        ttk.Label(details_frame, text="Active:").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        self.detail_active = ttk.Label(details_frame, text="")
        self.detail_active.grid(row=5, column=1, sticky="w", padx=5, pady=2)
        
        # Action buttons
        action_frame = ttk.Frame(details_frame)
        action_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
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
        
        self.disconnect_btn = ttk.Button(
            action_frame, 
            text="⚡ Disconnect", 
            command=self.disconnect_client
        )
        self.disconnect_btn.grid(row=0, column=4, padx=5)
        
        delete_btn = ttk.Button(
            action_frame, 
            text="Remove Client", 
            command=self.delete_client
        )
        delete_btn.grid(row=0, column=5, padx=5)
        
        # Status bar
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky="w")
        
        # Initially disable client actions
        self.update_detail_buttons_state(False)
        
        # Also disable disconnect button initially
        if hasattr(self, 'disconnect_btn'):
            self.disconnect_btn.state(["disabled"])
    
    def load_clients(self):
        """Loads client data from API"""
        if not self.winfo_exists():
            return
            
        self.status_var.set("Loading clients...")
        self.update_idletasks()
        
        # Store currently selected client ID to restore after refresh
        selected_client_id = None
        if self.selected_client:
            selected_client_id = self.selected_client.client_id
        
        # Calculate skip based on page and page size
        skip = self.page * self.page_size
        
        # Start loading in background thread
        threading.Thread(target=self._fetch_clients, args=(skip, selected_client_id), daemon=True).start()
    
    def _fetch_clients(self, skip, selected_client_id=None):
        """Background thread to fetch clients from API"""
        try:
            clients = self.api_client.get_clients(skip=skip, limit=self.page_size)
            
            # Update UI on main thread only if widget still exists
            if self.winfo_exists():
                self.after(0, lambda: self._update_client_list(clients, selected_client_id))
                self.after(0, lambda: self.status_var.set(f"Loaded {len(clients)} clients"))
            
            # Schedule next auto-refresh if enabled
            if self.is_refreshing and self.winfo_exists():
                self.auto_refresh_job = threading.Timer(1.0, self.load_clients)
                self.auto_refresh_job.start()
            
        except Exception as e:
            print(f"Error loading clients: {str(e)}")
            if self.winfo_exists():
                self.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to load clients: {str(e)}"))
            
            # Still schedule next refresh even on error
            if self.is_refreshing and self.winfo_exists():
                self.auto_refresh_job = threading.Timer(1.0, self.load_clients)
                self.auto_refresh_job.start()
    
    def _update_client_list(self, clients, selected_client_id=None):
        """Updates the client list treeview with fetched data"""
        # Ensure the treeview widget still exists before trying to update it
        if not self.winfo_exists() or not hasattr(self, 'clients_tree') or not self.clients_tree.winfo_exists():
            return

        # Clear existing items
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)
        
        # Add clients to treeview and track the item to reselect
        item_to_select = None
        
        for client in clients:
            # Check if last_connected is a string and convert to datetime if needed
            if isinstance(client.last_connected, str) and client.last_connected:
                try:
                    # Try to parse the string to datetime
                    last_connected = parse(client.last_connected).strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # If parsing fails, just use the string as is
                    last_connected = client.last_connected
            elif hasattr(client.last_connected, 'strftime'):
                # It's already a datetime object
                last_connected = client.last_connected.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # It's None or some other type
                last_connected = "N/A"
            
            # Create colored dot display for active status
            if client.active:
                active_display = "🟢"  # Green circle emoji for active
            else:
                active_display = "🔴"  # Red circle emoji for inactive
            
            # Determine row color based on connection status
            tag = "connected" if client.active else "disconnected"

            item = self.clients_tree.insert(
                "", "end", 
                values=(
                    client.id,
                    active_display,
                    client.client_id, 
                    client.last_ip or "N/A", 
                    client.last_port or "N/A",
                    last_connected,
                    client.connection_count
                ),
                tags=(tag,)
            )
            
            # Check if this is the previously selected client
            if selected_client_id and client.client_id == selected_client_id:
                item_to_select = item
        
        # Restore selection if we found the previously selected client
        if item_to_select and self.clients_tree.exists(item_to_select): # Check if item still exists
            self.clients_tree.selection_set(item_to_select)
            self.clients_tree.focus(item_to_select)
        
        # Update pagination only if widgets exist
        if self.winfo_exists():
            self.update_pagination()
    
    def update_pagination(self):
        """Updates pagination controls"""
        if not self.winfo_exists():
            return
        # Set page label
        if hasattr(self, 'page_label') and self.page_label.winfo_exists():
            self.page_label.config(text=f"Page {self.page + 1}")
        
        # Enable/disable pagination buttons based on page number
        if hasattr(self, 'prev_page_btn') and self.prev_page_btn.winfo_exists():
            self.prev_page_btn.state(["disabled"] if self.page == 0 else ["!disabled"])
        
        # Next button logic would depend on knowing total count, 
        # or checking if we received a full page of results
        if hasattr(self, 'next_page_btn') and self.next_page_btn.winfo_exists() and hasattr(self, 'clients_tree') and self.clients_tree.winfo_exists():
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
        
        # Get client ID from selected row (index 2 due to "Active" column)
        client_id = values[2]
        
        # Start loading client details in background
        threading.Thread(target=self._fetch_client_details, args=(client_id,), daemon=True).start()
    
    def _fetch_client_details(self, client_id):
        """Background thread to fetch client details"""
        try:
            client = self.api_client.get_client(client_id)
            
            if self.winfo_exists(): # Check if view still exists
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
            if self.winfo_exists(): # Check if view still exists
                self.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
    
    def update_client_details(self, client):
        """Updates the client details panel with selected client info"""
        if not self.winfo_exists(): # Check if view still exists
            return
        # Further checks for individual labels
        if hasattr(self, 'detail_client_id') and self.detail_client_id.winfo_exists():
            self.detail_client_id.config(text=client.client_id)
        if hasattr(self, 'detail_ip') and self.detail_ip.winfo_exists():
            self.detail_ip.config(text=client.last_ip or "N/A")
        if hasattr(self, 'detail_port') and self.detail_port.winfo_exists():
            self.detail_port.config(text=str(client.last_port) if client.last_port else "N/A")
        
        # Handle last_connected consistently with _update_client_list
        if isinstance(client.last_connected, str) and client.last_connected:
            try:
                # Try to parse the string to datetime
                last_connected = parse(client.last_connected).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                last_connected = client.last_connected
        elif hasattr(client.last_connected, 'strftime'):
            last_connected = client.last_connected.strftime("%Y-%m-%d %H:%M:%S")
        else:
            last_connected = "N/A"
        
        if hasattr(self, 'detail_last_connected') and self.detail_last_connected.winfo_exists():
            self.detail_last_connected.config(text=last_connected)
        if hasattr(self, 'detail_count') and self.detail_count.winfo_exists():
            self.detail_count.config(text=str(client.connection_count))
        
        active_text = "🟢 Yes" if client.active else "🔴 No"
        if hasattr(self, 'detail_active') and self.detail_active.winfo_exists():
            self.detail_active.config(text=active_text, foreground="black")
        
        self.update_detail_buttons_state(True)
        
        # Update disconnect button state - only enable for active clients
        if hasattr(self, 'disconnect_btn') and self.disconnect_btn.winfo_exists():
            if client.active:
                self.disconnect_btn.state(["!disabled"])
            else:
                self.disconnect_btn.state(["disabled"])
    
    def clear_client_details(self):
        """Clears the client details panel"""
        if not self.winfo_exists(): # Check if view still exists
            return
        if hasattr(self, 'detail_client_id') and self.detail_client_id.winfo_exists():
            self.detail_client_id.config(text="")
        if hasattr(self, 'detail_ip') and self.detail_ip.winfo_exists():
            self.detail_ip.config(text="")
        if hasattr(self, 'detail_port') and self.detail_port.winfo_exists():
            self.detail_port.config(text="")
        if hasattr(self, 'detail_last_connected') and self.detail_last_connected.winfo_exists():
            self.detail_last_connected.config(text="")
        if hasattr(self, 'detail_count') and self.detail_count.winfo_exists():
            self.detail_count.config(text="")
        if hasattr(self, 'detail_active') and self.detail_active.winfo_exists():
            self.detail_active.config(text="", foreground="black")
        
        self.update_detail_buttons_state(False)
        
        # Also disable disconnect button when no client is selected
        if hasattr(self, 'disconnect_btn') and self.disconnect_btn.winfo_exists():
            self.disconnect_btn.state(["disabled"])
    
    def update_detail_buttons_state(self, enabled):
        """Updates state of detail action buttons"""
        state = ["!disabled"] if enabled else ["disabled"]
        
        # Get reference to action frame directly
        try:
            # Find the action frame which is in the details frame
            content_frame = self.winfo_children()[1]  # This should be the content_frame
            if content_frame and hasattr(content_frame, 'winfo_children'):
                details_frame = None
                # Look for details_frame (LabelFrame with text "Client Details")
                for child in content_frame.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Client Details":
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
            # Ensure we have a client selected to delete
            client_to_delete_id = self.selected_client.client_id
            success = self.api_client.delete_client(client_to_delete_id)
            
            if self.winfo_exists(): # Check if view still exists
                if success:
                    self.after(0, lambda: self.status_var.set(f"Client '{client_to_delete_id}' deleted successfully"))
                    # Clear selection and details panel, then reload
                    self.selected_client = None
                    self.after(0, self.clear_client_details) 
                    self.after(0, self.load_clients)
                else:
                    self.after(0, lambda: self.status_var.set(f"Failed to delete client"))
                    self.after(0, lambda: messagebox.showerror("Error", "Failed to delete client."))
                
        except AttributeError: # Handle case where self.selected_client is None
             if self.winfo_exists():
                self.after(0, lambda: self.status_var.set("No client selected to delete"))
        except Exception as e:
            print(f"Error deleting client: {str(e)}")
            if self.winfo_exists(): # Check if view still exists
                self.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to delete client: {str(e)}"))
    
    def view_client_topics(self):
        """Navigate to topics view filtered by client"""
        if not self.selected_client:
            return
        self.show_view_callback("client_topics", client_id=self.selected_client.client_id)

    def view_client_subscriptions(self):
        """Navigate to subscriptions view filtered by client"""
        if not self.selected_client:
            return
        self.show_view_callback("client_subscriptions", client_id=self.selected_client.client_id)

    def view_client_messages(self):
        """Navigate to messages view filtered by client"""
        if not self.selected_client:
            return
        self.show_view_callback("client_messages", client_id=self.selected_client.client_id)

    def view_client_events(self):
        """Navigate to events view filtered by client"""
        if not self.selected_client:
            return
        
        # This would require passing filter info to events view
        messagebox.showinfo("Not Implemented", "View events by client feature coming soon!")

    def start_auto_refresh(self):
        """Starts auto-refresh job"""
        if not self.is_refreshing:
            self.is_refreshing = True
            self.auto_refresh_job = threading.Timer(1.0, self.load_clients)
            self.auto_refresh_job.start()

    def stop_auto_refresh(self):
        """Stops auto-refresh job"""
        self.is_refreshing = False
        if self.auto_refresh_job:
            self.auto_refresh_job.cancel()
            self.auto_refresh_job = None

    def on_destroy(self):
        """Called when the view is being destroyed"""
        self.stop_auto_refresh()

    def disconnect_client(self):
        """Disconnects the selected client"""
        if not self.selected_client:
            return
        
        if messagebox.askyesno(
            "Disconnect Client", 
            f"Are you sure you want to disconnect client '{self.selected_client.client_id}'?"
        ):
            threading.Thread(target=self._disconnect_client_thread, daemon=True).start()
    
    def _disconnect_client_thread(self):
        """Background thread for client disconnection"""
        try:
            # Ensure we have a client selected to disconnect
            client_to_disconnect_id = self.selected_client.client_id
            success = self.api_client.update_client_status(client_to_disconnect_id, False)
            
            if self.winfo_exists(): # Check if view still exists
                if success:
                    self.after(0, lambda: self.status_var.set(f"Client '{client_to_disconnect_id}' disconnected successfully"))
                    # Clear selection and details panel, then reload
                    self.selected_client = None
                    self.after(0, self.clear_client_details) 
                    self.after(0, self.load_clients)
                else:
                    self.after(0, lambda: self.status_var.set(f"Failed to disconnect client"))
                    self.after(0, lambda: messagebox.showerror("Error", "Failed to disconnect client."))
                
        except AttributeError: # Handle case where self.selected_client is None
             if self.winfo_exists():
                self.after(0, lambda: self.status_var.set("No client selected to disconnect"))
        except Exception as e:
            print(f"Error disconnecting client: {str(e)}")
            if self.winfo_exists(): # Check if view still exists
                self.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to disconnect client: {str(e)}")) 