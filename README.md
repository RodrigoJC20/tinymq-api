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
│   │   ├── clients.py
│   │   ├── topics.py
│   │   ├── messages.py
│   │   └── events.py
│   └── requirements.txt # API dependencies
├── gui/               # Tkinter GUI for remote machine
│   ├── app.py         # Main GUI application
│   ├── views/         # Different GUI screens
│   │   ├── __init__.py
│   │   ├── login.py
│   │   ├── dashboard.py
│   │   ├── clients.py
│   │   ├── topics.py
│   │   └── logs.py
│   └── requirements.txt # GUI dependencies
├── common/            # Shared code
│   └── models.py      # Shared data models
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
   cd api
   python app.py
   ```

### GUI (Remote machine)

1. Install dependencies:
   ```
   cd gui
   pip install -r requirements.txt
   ```

2. Run the GUI:
   ```
   cd gui
   python app.py
   ```
   
3. Connect to the API by entering the Raspberry Pi's hostname/IP and the API port

## Usage

1. Start the API on the Raspberry Pi
2. Start the GUI on your desktop/laptop
3. Log in using your admin credentials
4. Use the GUI to monitor and manage your TinyMQ broker 