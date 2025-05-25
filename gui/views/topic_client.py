import tkinter as tk
from tkinter import ttk, messagebox
import threading
from common import Client

class TopicClientView(ttk.Frame):
    def __init__(self, parent, api_client, topic_id, show_view_callback):
        super().__init__(parent)
        self.parent = parent
        self.api_client = api_client
        self.topic_id = topic_id
        self.show_view_callback = show_view_callback
        
        # Setup UI components
        self.setup_ui()
        
        # Load initial data
        self.load_client()
    
    def setup_ui(self):
        # Configure the grid
        self.columnconfigure(0, weight=1)
        
        # Header frame
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        header_frame.columnconfigure(1, weight=1)
        
        back_button = ttk.Button(header_frame, text="< Back", command=lambda: self.show_view_callback("topics"))
        back_button.grid(row=0, column=0, sticky="w", padx=5, pady=10)
        
        title_label = ttk.Label(header_frame, text=f"Owner Client for Topic: {self.topic_id}", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        
        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.load_client)
        refresh_button.grid(row=0, column=2, padx=5, pady=10)
        
        # Client details frame
        details_frame = ttk.LabelFrame(self, text="Client Details")
        details_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        details_frame.columnconfigure(1, weight=1)
        
        ttk.Label(details_frame, text="Client ID:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.detail_client_id = ttk.Label(details_frame, text="")
        self.detail_client_id.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Last Connected:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.detail_last_connected = ttk.Label(details_frame, text="")
        self.detail_last_connected.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Last IP:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.detail_last_ip = ttk.Label(details_frame, text="")
        self.detail_last_ip.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Last Port:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.detail_last_port = ttk.Label(details_frame, text="")
        self.detail_last_port.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Connection Count:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.detail_connection_count = ttk.Label(details_frame, text="")
        self.detail_connection_count.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        
        # Status bar
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor="w")
        status_label.grid(row=0, column=0, sticky="w", padx=5)
    
    def load_client(self):
        """Loads client data from API"""
        threading.Thread(target=self._fetch_client, daemon=True).start()
    
    def _fetch_client(self):
        """Background thread to fetch client details"""
        try:
            client = self.api_client.get_client_by_topic(self.topic_id)
            if client is None:
                raise ValueError("Client not found for the specified topic.")
            self.after(0, lambda: self.update_client_details(client))
        except Exception as e:
            error_message = str(e)  # Captura el mensaje de error
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to load client details: {error_message}"))
    
    def update_client_details(self, client):
        """Update the client details panel"""
        if not client:
            self.status_var.set("No client found for this topic.")
            messagebox.showerror("Error", "No client found for this topic.")
            return
        
        self.detail_client_id.config(text=client.client_id)
        self.detail_last_connected.config(text=client.last_connected or "Unknown")
        self.detail_last_ip.config(text=client.last_ip or "Unknown")
        self.detail_last_port.config(text=client.last_port or "Unknown")
        self.detail_connection_count.config(text=str(client.connection_count))
        
        # Update status
        self.status_var.set(f"Loaded client details for {client.client_id}")
        
