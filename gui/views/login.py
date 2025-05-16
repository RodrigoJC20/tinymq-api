import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from common import ApiConfig
from gui.api_client import ApiClient

class LoginView(ttk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.parent = parent
        self.on_login_success = on_login_success
        
        # Default API port
        self.default_port = 8000
        
        self.api_client = None
        self.setup_ui()
    
    def setup_ui(self):
        # Configure the grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        
        # Create header
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, columnspan=2, pady=20, sticky="ew")
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, text="TinyMQ Monitor", font=("Helvetica", 24, "bold"))
        title_label.grid(row=0, column=0)
        
        subtitle_label = ttk.Label(header_frame, text="Connect to your TinyMQ Broker API")
        subtitle_label.grid(row=1, column=0, pady=5)
        
        # Connection details frame with border
        connection_frame = ttk.LabelFrame(self, text="Connection Details")
        connection_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        
        # Host
        ttk.Label(connection_frame, text="Host:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.host_entry = ttk.Entry(connection_frame, width=30)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Port
        ttk.Label(connection_frame, text="Port:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.port_entry = ttk.Entry(connection_frame, width=10)
        self.port_entry.insert(0, str(self.default_port))
        self.port_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Authentication frame
        auth_frame = ttk.LabelFrame(self, text="Authentication")
        auth_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        
        # Username
        ttk.Label(auth_frame, text="Username:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.username_entry = ttk.Entry(auth_frame, width=30)
        self.username_entry.insert(0, "admin")
        self.username_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Password
        ttk.Label(auth_frame, text="Password:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.password_entry = ttk.Entry(auth_frame, show="*", width=30)
        self.password_entry.insert(0, "admin")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Buttons frame
        buttons_frame = ttk.Frame(self)
        buttons_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=20)
        
        # Login button
        self.login_button = ttk.Button(
            buttons_frame, 
            text="Login", 
            command=self.attempt_login,
            style="Accent.TButton"
        )
        self.login_button.grid(row=0, column=0, padx=10)
        
        # Exit button
        self.exit_button = ttk.Button(
            buttons_frame, 
            text="Exit", 
            command=self.parent.quit
        )
        self.exit_button.grid(row=0, column=1, padx=10)
        
        # Status message
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self, textvariable=self.status_var, foreground="red")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Add some padding to all children of frames
        for frame in [connection_frame, auth_frame]:
            for child in frame.winfo_children():
                child.grid_configure(padx=5, pady=5)
    
    def attempt_login(self):
        # Get input values
        host = self.host_entry.get().strip()
        port_str = self.port_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Validate inputs
        if not host:
            self.status_var.set("Please enter a host name or IP address")
            return
        
        try:
            port = int(port_str)
            if port <= 0 or port > 65535:
                raise ValueError("Port number out of range")
        except ValueError:
            self.status_var.set("Please enter a valid port number (1-65535)")
            return
        
        if not username or not password:
            self.status_var.set("Please enter both username and password")
            return
        
        # Create API config and client
        api_config = ApiConfig(
            host=host,
            port=port,
            username=username,
            password=password
        )
        self.api_client = ApiClient(api_config)
        
        # Show login in progress
        self.status_var.set("Connecting to API...")
        self.login_button.state(["disabled"])
        self.update_idletasks()
        
        # Attempt login
        success = self.api_client.login()
        
        if success:
            self.status_var.set("Login successful!")
            self.on_login_success(self.api_client)
        else:
            self.login_button.state(["!disabled"])
            self.status_var.set("Login failed. Please check your connection details and credentials.") 