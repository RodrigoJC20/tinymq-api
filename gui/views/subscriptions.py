import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from gui.api_client import ApiClient
from common import Subscription, Topic, Client

class SubscriptionsView(ttk.Frame):
    def __init__(self, parent, api_client, show_view_callback):
        super().__init__(parent)
        self.parent = parent
        self.api_client = api_client
        self.show_view_callback = show_view_callback
        
        # Pagination variables
        self.page = 0
        self.page_size = 20
        self.total_subscriptions = 0
        
        # Filter variables
        self.show_active_only = tk.BooleanVar(value=True)
        
        # Selected subscription for details
        self.selected_subscription = None
        
        # Setup UI components
        self.setup_ui()
        
        # Load initial data
        self.load_subscriptions()
    
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
        
        title_label = ttk.Label(header_frame, text="TinyMQ Subscriptions", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        
        # Filter active subscriptions
        active_filter = ttk.Checkbutton(
            header_frame, 
            text="Active Only", 
            variable=self.show_active_only,
            command=self.load_subscriptions
        )
        active_filter.grid(row=0, column=2, padx=5, pady=10)
        
        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.load_subscriptions)
        refresh_button.grid(row=0, column=3, padx=5, pady=10)
        
        # Main content - split into top subscription list and bottom subscription details
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=3)  # Subscription list gets more space
        content_frame.rowconfigure(1, weight=2)  # Subscription details gets less space
        
        # Subscription list frame with Treeview
        list_frame = ttk.LabelFrame(content_frame, text="Subscription List")
        list_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Subscriptions table with scrollbar
        self.subscriptions_tree = ttk.Treeview(
            list_frame,
            columns=("id", "client_id", "topic_name", "subscribed_at", "active"),
            show="headings",
            selectmode="browse"
        )
        
        self.subscriptions_tree.heading("id", text="ID")
        self.subscriptions_tree.heading("client_id", text="Client ID")
        self.subscriptions_tree.heading("topic_name", text="Topic")
        self.subscriptions_tree.heading("subscribed_at", text="Subscribed At")
        self.subscriptions_tree.heading("active", text="Active")
        
        self.subscriptions_tree.column("id", width=50)
        self.subscriptions_tree.column("client_id", width=200)
        self.subscriptions_tree.column("topic_name", width=200)
        self.subscriptions_tree.column("subscribed_at", width=150)
        self.subscriptions_tree.column("active", width=80)
        
        self.subscriptions_tree.grid(row=0, column=0, sticky="nsew")
        self.subscriptions_tree.bind("<<TreeviewSelect>>", self.on_subscription_selected)
        
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
        
        # Subscription details frame
        details_frame = ttk.LabelFrame(content_frame, text="Subscription Details")
        details_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        details_frame.columnconfigure(1, weight=1)
        
        # Subscription details content
        ttk.Label(details_frame, text="Subscription ID:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.detail_sub_id = ttk.Label(details_frame, text="")
        self.detail_sub_id.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Client ID:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.detail_client_id = ttk.Label(details_frame, text="")
        self.detail_client_id.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Topic:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.detail_topic_name = ttk.Label(details_frame, text="")
        self.detail_topic_name.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Topic ID:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.detail_topic_id = ttk.Label(details_frame, text="")
        self.detail_topic_id.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Subscribed At:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.detail_subscribed_at = ttk.Label(details_frame, text="")
        self.detail_subscribed_at.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Status:").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        self.detail_active = ttk.Label(details_frame, text="")
        self.detail_active.grid(row=5, column=1, sticky="w", padx=5, pady=2)
        
        # Action buttons
        action_frame = ttk.Frame(details_frame)
        action_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        self.toggle_status_btn = ttk.Button(
            action_frame, 
            text="Desactivate", 
            command=self.toggle_subscription_status
        )
        self.toggle_status_btn.grid(row=0, column=0, padx=5)
        
        view_client_btn = ttk.Button(
            action_frame, 
            text="View Client", 
            command=lambda: self.show_view_callback("subscription_client", subscription_id=self.selected_subscription.id)
        )
        view_client_btn.grid(row=0, column=1, padx=5)
        
        view_topic_btn = ttk.Button(
            action_frame, 
            text="View Topic", 
            command=lambda: self.show_view_callback("subscription_topic", subscription_id=self.selected_subscription.id)
        )
        view_topic_btn.grid(row=0, column=2, padx=5)
        
        delete_btn = ttk.Button(
            action_frame, 
            text="Delete Subscription", 
            command=self.delete_subscription,
            style="Danger.TButton"
        )
        delete_btn.grid(row=0, column=3, padx=5)
        
        # Status bar
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky="w")
        
        # Initially disable subscription actions
        self.update_detail_buttons_state(False)
    
    def load_subscriptions(self):
        """Loads subscription data from API"""
        self.status_var.set("Loading subscriptions...")
        self.update_idletasks()
        
        # Clear selected subscription
        self.selected_subscription = None
        self.clear_subscription_details()
        
        # Calculate skip based on page and page size
        skip = self.page * self.page_size
        
        # Get active filter value
        active_only = self.show_active_only.get()
        
        # Start loading in background thread
        threading.Thread(
            target=self._fetch_subscriptions, 
            args=(skip, active_only), 
            daemon=True
        ).start()
    
    def _fetch_subscriptions(self, skip, active_only):
        """Background thread to fetch subscriptions from API"""
        subscriptions = self.api_client.get_subscriptions(
            skip=skip, 
            limit=self.page_size, 
            active_only=active_only
        )
        
        # Update UI in main thread
        self.after(0, lambda: self._update_subscription_list(subscriptions))
    
    def _update_subscription_list(self, subscriptions):
        """Updates the subscriptions treeview with data"""
        # Clear existing entries
        for row in self.subscriptions_tree.get_children():
            self.subscriptions_tree.delete(row)
            
        # Add subscriptions to treeview
        for sub in subscriptions:
            # Format the subscribed_at timestamp if it exists
            subscribed_at = sub.subscribed_at
            if subscribed_at:
                # Format date for display
                if isinstance(subscribed_at, str):
                    # If it's a string, it's likely ISO format
                    try:
                        subscribed_at = datetime.fromisoformat(subscribed_at.replace('Z', '+00:00'))
                    except ValueError:
                        pass
                
                if isinstance(subscribed_at, datetime):
                    subscribed_at = subscribed_at.strftime("%Y-%m-%d %H:%M:%S")
            
            # Display "Yes" or "No" for active status
            active_text = "Yes" if sub.active else "No"
            
            self.subscriptions_tree.insert(
                "", "end", 
                values=(sub.id, sub.client_id, sub.topic_name, subscribed_at, active_text)
            )
            
        # Update status
        if subscriptions:
            self.status_var.set(f"Loaded {len(subscriptions)} subscriptions")
        else:
            self.status_var.set("No subscriptions found")
            
        # Update pagination buttons
        self.update_pagination()
    
    def update_pagination(self):
        """Update pagination controls based on current page"""
        self.page_label.config(text=f"Page {self.page + 1}")
        
        # Enable/disable prev button based on current page
        if self.page > 0:
            self.prev_page_btn.state(["!disabled"])
        else:
            self.prev_page_btn.state(["disabled"])
            
        # Logic for next button could depend on if we know there are more pages
        # For now, we'll disable it if we received fewer items than the page size
        children_count = len(self.subscriptions_tree.get_children())
        if children_count < self.page_size:
            self.next_page_btn.state(["disabled"])
        else:
            self.next_page_btn.state(["!disabled"])
    
    def prev_page(self):
        """Go to previous page of subscriptions"""
        if self.page > 0:
            self.page -= 1
            self.load_subscriptions()
    
    def next_page(self):
        """Go to next page of subscriptions"""
        self.page += 1
        self.load_subscriptions()
    
    def on_subscription_selected(self, event):
        """Handle subscription selection in treeview"""
        selected_items = self.subscriptions_tree.selection()
        if selected_items:
            # Get subscription ID from the first column of the selected row
            item_values = self.subscriptions_tree.item(selected_items[0], "values")
            subscription_id = int(item_values[0])
            
            # Fetch subscription details in background
            self.status_var.set("Loading subscription details...")
            threading.Thread(target=self._fetch_subscription_details, args=(subscription_id,), daemon=True).start()
        else:
            self.clear_subscription_details()
            self.update_detail_buttons_state(False)
    
    def _fetch_subscription_details(self, subscription_id):
        """Background thread to fetch subscription details"""
        subscription = self.api_client.get_subscription(subscription_id)
        
        if subscription:
            # Update UI in main thread
            self.after(0, lambda: self.update_subscription_details(subscription))
        else:
            self.after(0, lambda: self.status_var.set("Failed to load subscription details"))
    
    def update_subscription_details(self, subscription):
        """Update the subscription details panel with subscription data"""
        self.selected_subscription = subscription
        
        # Format the subscribed_at timestamp if it exists
        subscribed_at = subscription.subscribed_at
        if subscribed_at:
            # Format date for display
            if isinstance(subscribed_at, str):
                try:
                    subscribed_at = datetime.fromisoformat(subscribed_at.replace('Z', '+00:00'))
                except ValueError:
                    pass
            
            if isinstance(subscribed_at, datetime):
                subscribed_at = subscribed_at.strftime("%Y-%m-%d %H:%M:%S")
        
        # Update detail labels
        self.detail_sub_id.config(text=str(subscription.id))
        self.detail_client_id.config(text=subscription.client_id)
        self.detail_topic_name.config(text=subscription.topic_name or "Unknown")
        self.detail_topic_id.config(text=str(subscription.topic_id))
        self.detail_subscribed_at.config(text=subscribed_at or "Unknown")
        
        active_status = "Active" if subscription.active else "Inactive"
        self.detail_active.config(text=active_status)
        
        # Update toggle button text based on current status
        if subscription.active:
            self.toggle_status_btn.config(text="Desactivate")
        else:
            self.toggle_status_btn.config(text="Activate")
        
        # Enable action buttons
        self.update_detail_buttons_state(True)
        
        self.status_var.set("Subscription details loaded")
    
    def clear_subscription_details(self):
        """Clear the subscription details panel"""
        self.detail_sub_id.config(text="")
        self.detail_client_id.config(text="")
        self.detail_topic_name.config(text="")
        self.detail_topic_id.config(text="")
        self.detail_subscribed_at.config(text="")
        self.detail_active.config(text="")
        
        # Reset toggle button text
        self.toggle_status_btn.config(text="Toggle Status")
        
        # Disable action buttons
        self.update_detail_buttons_state(False)
    
    def update_detail_buttons_state(self, enabled):
        """Enable or disable the detail action buttons"""
        state = ["!disabled"] if enabled else ["disabled"]
        
        # Get all buttons in the action frame
        action_frame = self.winfo_children()[1].winfo_children()[1].winfo_children()[6]
        for child in action_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.state(state)
    
    def toggle_subscription_status(self):
        """Toggle the active status of the selected subscription"""
        if not self.selected_subscription:
            return
            
        # Determine the new status (opposite of current)
        new_status = not self.selected_subscription.active
        action = "activate" if new_status else "desactivate"
        
        # Confirm the action
        confirm = messagebox.askyesno(
            "Confirm Status Change",
            f"Are you sure you want to {action} the subscription for client '{self.selected_subscription.client_id}' to topic '{self.selected_subscription.topic_name}'?",
            icon="question"
        )
        
        if confirm:
            self.status_var.set(f"{action.capitalize()}ing subscription...")
            threading.Thread(
                target=self._toggle_status_thread,
                args=(new_status,),
                daemon=True
            ).start()
    
    def _toggle_status_thread(self, new_status):
        """Background thread to toggle subscription status"""
        if not self.selected_subscription:
            return
            
        try:
            # Call the API to update the subscription status
            success = self.api_client.update_subscription_status(self.selected_subscription.id, new_status)
            
            if success:
                # Update the UI to reflect the new status
                self.after(0, lambda: self.status_var.set("Subscription status updated successfully"))
                self.after(0, self.load_subscriptions)
            else:
                self.after(0, lambda: messagebox.showerror(
                    "Update Failed", 
                    "Failed to update subscription status"
                ))
                self.after(0, lambda: self.status_var.set("Update failed"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(
                "Error", 
                f"An error occurred while updating subscription status: {str(e)}"
            ))
            self.after(0, lambda: self.status_var.set("Error updating status"))
    
    def view_client(self):
        """Navigate to the client details view for this subscription's client"""
        if self.selected_subscription:
            # This would normally transition to the client view
            # For now, just show a message
            messagebox.showinfo("View Client", 
                              f"View client '{self.selected_subscription.client_id}'\n"
                              f"This navigation feature is not yet implemented.")
    
    def view_topic(self):
        """Navigate to the topic details view for this subscription's topic"""
        if self.selected_subscription:
            # This would normally transition to the topic view
            # For now, just show a message
            messagebox.showinfo("View Topic", 
                              f"View topic '{self.selected_subscription.topic_name}'\n"
                              f"This navigation feature is not yet implemented.")
    
    def delete_subscription(self):
        """Delete the selected subscription"""
        if not self.selected_subscription:
            return
            
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the subscription for client '{self.selected_subscription.client_id}' to topic '{self.selected_subscription.topic_name}'?",
            icon="warning"
        )
        
        if confirm:
            self.status_var.set("Deleting subscription...")
            threading.Thread(target=self._delete_subscription_thread, daemon=True).start()
    
    def _delete_subscription_thread(self):
        """Background thread to delete a subscription"""
        if not self.selected_subscription:
            return
            
        success = self.api_client.delete_subscription(self.selected_subscription.id)
        
        if success:
            # Reload subscriptions after deletion
            self.after(0, lambda: self.status_var.set("Subscription deleted successfully"))
            self.after(0, self.load_subscriptions)
        else:
            self.after(0, lambda: messagebox.showerror(
                "Delete Failed", 
                "Failed to delete subscription"
            ))
            self.after(0, lambda: self.status_var.set("Delete failed"))