#!/usr/bin/env python3
"""
TinyMQ GUI Launcher
------------------
This script launches the TinyMQ Monitor GUI application on a remote machine.
"""

import os
import sys

# Make sure we're in the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def main():
    # Print startup message
    print("=" * 60)
    print("Starting TinyMQ Monitor GUI")
    print("=" * 60)
    
    # Check if tkinter is available
    try:
        import tkinter
    except ImportError:
        print("Error: Tkinter is not installed. Please install it first.")
        print("On Linux: sudo apt-get install python3-tk")
        print("On macOS: Tkinter should be included with Python")
        print("On Windows: Reinstall Python with the tcl/tk option checked")
        sys.exit(1)
    
    # Check for required dependencies
    try:
        import requests
        import ttkthemes
        import PIL
    except ImportError as e:
        print(f"Error: Missing required dependency: {e}")
        print("Please install the required dependencies:")
        print("pip install -r gui/requirements.txt")
        sys.exit(1)
    
    # Start the GUI application
    try:
        from gui.app import TinyMQMonitorApp
        app = TinyMQMonitorApp()
        app.run()
    except Exception as e:
        print(f"Error starting GUI application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 