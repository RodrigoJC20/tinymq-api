import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class SettingsView(ttk.Frame):
    def __init__(self, parent, api_client, show_view_callback):
        super().__init__(parent)
        self.parent = parent
        self.api_client = api_client
        self.show_view_callback = show_view_callback
        
        # Password variables
        self.new_password = tk.StringVar()
        self.confirm_password = tk.StringVar()
        
        # Setup UI components
        self.setup_ui()
    
    def setup_ui(self):
        # Configure the grid
        self.columnconfigure(0, weight=1)
        
        # Header frame - Title and control buttons
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        header_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(header_frame, text="Admin Settings", font=("Helvetica", 18, "bold"))
        title_label.grid(row=0, column=0, sticky="w", padx=5, pady=10)
        
        # Back button
        back_button = ttk.Button(
            header_frame, 
            text="Back to Dashboard", 
            command=lambda: self.show_view_callback("dashboard")
        )
        back_button.grid(row=0, column=3, padx=5)
        
        # Main content area
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.columnconfigure(0, weight=1)
        
        # Password change section
        change_password_frame = ttk.LabelFrame(content_frame, text="Change Admin Password")
        change_password_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        change_password_frame.columnconfigure(1, weight=1)
        
        # New password field
        new_pwd_label = ttk.Label(change_password_frame, text="New Password:")
        new_pwd_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        new_pwd_entry = ttk.Entry(change_password_frame, textvariable=self.new_password, show="*", width=20)
        new_pwd_entry.grid(row=0, column=1, sticky="w", padx=10, pady=10)
        
        # Confirm password field
        confirm_pwd_label = ttk.Label(change_password_frame, text="Confirm Password:")
        confirm_pwd_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        
        confirm_pwd_entry = ttk.Entry(change_password_frame, textvariable=self.confirm_password, show="*", width=20)
        confirm_pwd_entry.grid(row=1, column=1, sticky="w", padx=10, pady=10)
        
        # Password requirements hint
        hint_label = ttk.Label(
            change_password_frame, 
            text="Password should be at least 8 characters long", 
            foreground="gray"
        )
        hint_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, sticky="e", padx=10, pady=10)
        
        cancel_btn = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=lambda: self.show_view_callback("dashboard")
        )
        cancel_btn.grid(row=0, column=0, padx=5)
        
        save_btn = ttk.Button(
            button_frame, 
            text="Change Password", 
            command=self.change_password
        )
        save_btn.grid(row=0, column=1, padx=5)
    
    def change_password(self):
        """Changes the admin password"""
        new_pwd = self.new_password.get()
        confirm_pwd = self.confirm_password.get()
        
        # Validate passwords
        if not new_pwd:
            messagebox.showerror("Error", "Password cannot be empty")
            return
            
        if new_pwd != confirm_pwd:
            messagebox.showerror("Error", "Passwords do not match")
            return
            
        if len(new_pwd) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long")
            return
        
        # Call API to change password
        success = self.api_client.change_password(new_pwd)
        
        if success:
            messagebox.showinfo(
                "Success", 
                "Password has been changed successfully!\nPlease use the new password next time you log in."
            )
            self.show_view_callback("dashboard")
        else:
            messagebox.showerror(
                "Error", 
                "Failed to change password. Please try again later."
            )
    
    def on_destroy(self):
        """Clean up when view is destroyed"""
        pass  # No timers or resources to clean up yet 