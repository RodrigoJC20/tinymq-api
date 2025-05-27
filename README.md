# TinyMQ API and Monitoring GUI

This project consists of two main components:

1. **TinyMQ API** - A REST API that runs on the Raspberry Pi and provides endpoints to access the TinyMQ broker's PostgreSQL database.
2. **TinyMQ GUI** - A Tkinter GUI application that runs on a remote machine and communicates with the API.

## Directory Structure

```
tinymq-api/
├── api/                # REST API for the Raspberry Pi
│   ├── app.py         # Main API application
│   ├── config.py      # Configuration settings
│   ├── models.py      # Database models
│   ├── auth.py        # Authentication functions
│   ├── routes/        # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── clients.py
│   │   ├── topics.py
│   │   ├── messages.py
│   │   ├── subscriptions.py
│   │   └── events.py
│   └── requirements.txt # API dependencies
├── gui/               # Tkinter GUI for remote machine
│   ├── api_client.py  # API client for communication with the API
│   ├── app.py         # Main GUI application
│   ├── views/         # Different GUI screens
│   │   ├── client/    # Client-related views
│   │   │   ├── client_events.py
│   │   │   ├── client_messages.py
│   │   │   ├── client_subscriptions.py
│   │   │   ├── client_topics.py
│   │   │   └── clients.py
│   │   ├── event/     # Event-related views
│   │   │   ├── event_all_client_events.py
│   │   │   ├── event_client.py
│   │   │   └── events.py
│   │   ├── message/     # Messages-related views
│   │   │   ├── message_publish.py
│   │   │   ├── message_topic.py
│   │   │   └── messages.py
│   │   ├── subscription/ # Subscription-related views
│   │   │   ├── subscription_client.py
│   │   │   ├── subscription_topic.py
│   │   │   └── subscriptions.py
│   │   ├── topic/     # Topic-related views
│   │   │   ├── topic_client.py
│   │   │   ├── topic_messages.py
│   │   │   ├── topic_subscriptions.py
│   │   │   └── topics.py
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── login.py
│   │   └── settings.py
│   └── requirements.txt # GUI dependencies
├── common/            # Shared code
│   └── models.py      # Shared data models
├── start_api.py        # Script to start the API
├── start_gui.py        # Script to start the GUI
└── README.md          # This file
```

## Setup and Installation

### API (Raspberry Pi)

1. Install dependencies:
   ```
   cd api
   pip install -r requirements.txt
   ```

2. Set up configuration:
   - Update `config.py` with your PostgreSQL connection details
   - Set your admin username and password

3. Run the API:
   ```
   cd tinymq-api
   python start_api.py
   ```

### GUI (Remote machine)

1. Install dependencies:
   ```
   cd gui
   pip install -r requirements.txt
   ```

2. Install the `Noto Color Emoji` font (required for emoji support in the GUI):
   - On Debian/Ubuntu-based systems:
     ```
     sudo apt install fonts-noto-color-emoji
     ```

3. Run the GUI:
   ```
   cd tinymq-api
   python start_gui.py
   ```
   
3. Connect to the API by entering the Raspberry Pi's hostname/IP and the API port

## Usage

1. Start the API on the Raspberry Pi
2. Start the GUI on your desktop/laptop
3. Log in using your admin credentials
4. Use the GUI to monitor and manage your TinyMQ broker 