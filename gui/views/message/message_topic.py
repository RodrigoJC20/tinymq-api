import tkinter as tk
from tkinter import ttk
import threading
from dateutil.parser import parse

class MessageTopicView(ttk.Frame):
    def __init__(self, parent, api_client, message_id, show_view_callback):
        super().__init__(parent)
        self.api_client = api_client
        self.message_id = message_id
        self.show_view_callback = show_view_callback
        self.status_var = tk.StringVar(value="Ready")
        self.setup_ui()
        self.load_topic_details()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(15, 5))
        header_frame.columnconfigure(2, weight=1)
        header_frame.columnconfigure(3, weight=0)

        back_button = ttk.Button(header_frame, text="< Back", command=lambda: self.show_view_callback("messages"))
        back_button.grid(row=0, column=0, padx=5)

        title_label = ttk.Label(header_frame, text="Message Topic Details", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5)

        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.load_topic_details)
        refresh_button.grid(row=0, column=3, padx=5, sticky="e")

        details_frame = ttk.LabelFrame(self, text="Topic Details")
        details_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        details_frame.columnconfigure(1, weight=1)

        ttk.Label(details_frame, text="Topic ID:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.topic_id_label = ttk.Label(details_frame, text="")
        self.topic_id_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(details_frame, text="Topic Name:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.topic_name_label = ttk.Label(details_frame, text="")
        self.topic_name_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(details_frame, text="Owner Client ID:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.owner_client_id_label = ttk.Label(details_frame, text="")
        self.owner_client_id_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(details_frame, text="Created At:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.created_at_label = ttk.Label(details_frame, text="")
        self.created_at_label.grid(row=3, column=1, sticky="w", padx=5, pady=2)

        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky="w")

    def load_topic_details(self):
        self.status_var.set("Loading topic details...")
        threading.Thread(target=self._fetch_topic_details, daemon=True).start()

    def _fetch_topic_details(self):
        topic = self.api_client.get_topic_by_message(self.message_id)
        if topic:
            self.topic_id_label.config(text=topic.id)
            self.topic_name_label.config(text=topic.name)
            self.owner_client_id_label.config(text=topic.owner_client_id)
            self.created_at_label.config(text=parse(topic.created_at).strftime("%Y-%m-%d %H:%M:%S") if topic.created_at else "N/A")
            self.status_var.set("Topic details loaded")
        else:
            self.status_var.set("Failed to load topic details")
