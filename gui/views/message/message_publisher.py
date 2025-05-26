import tkinter as tk
from tkinter import ttk
import threading
from dateutil.parser import parse

class MessagePublisherView(ttk.Frame):
    def __init__(self, parent, api_client, message_id, show_view_callback):
        super().__init__(parent)
        self.api_client = api_client
        self.message_id = message_id
        self.show_view_callback = show_view_callback
        self.status_var = tk.StringVar(value="Ready")
        self.setup_ui()
        self.load_publisher_details()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(15, 5))
        header_frame.columnconfigure(2, weight=1)
        header_frame.columnconfigure(3, weight=0)

        back_button = ttk.Button(header_frame, text="< Back", command=lambda: self.show_view_callback("messages"))
        back_button.grid(row=0, column=0, padx=5)

        title_label = ttk.Label(header_frame, text="Message Publisher Details", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5)

        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.load_publisher_details)
        refresh_button.grid(row=0, column=3, padx=5, sticky="e")

        details_frame = ttk.LabelFrame(self, text="Publisher Details")
        details_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        details_frame.columnconfigure(1, weight=1)

        ttk.Label(details_frame, text="Client ID:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.client_id_label = ttk.Label(details_frame, text="")
        self.client_id_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(details_frame, text="Last Connected:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.last_connected_label = ttk.Label(details_frame, text="")
        self.last_connected_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(details_frame, text="Last IP:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.last_ip_label = ttk.Label(details_frame, text="")
        self.last_ip_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(details_frame, text="Last Port:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.last_port_label = ttk.Label(details_frame, text="")
        self.last_port_label.grid(row=3, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(details_frame, text="Connection Count:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.connection_count_label = ttk.Label(details_frame, text="")
        self.connection_count_label.grid(row=4, column=1, sticky="w", padx=5, pady=2)

        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky="w")

    def load_publisher_details(self):
        self.status_var.set("Loading publisher details...")
        threading.Thread(target=self._fetch_publisher_details, daemon=True).start()

    def _fetch_publisher_details(self):
        publisher = self.api_client.get_publisher_by_message(self.message_id)
        if publisher:
            self.client_id_label.config(text=publisher.client_id)
            self.last_connected_label.config(text=parse(publisher.last_connected).strftime("%Y-%m-%d %H:%M:%S") if publisher.last_connected else "N/A")
            self.last_ip_label.config(text=publisher.last_ip or "N/A")
            self.last_port_label.config(text=publisher.last_port or "N/A")
            self.connection_count_label.config(text=publisher.connection_count)
            self.status_var.set("Publisher details loaded")
        else:
            self.status_var.set("Failed to load publisher details")
