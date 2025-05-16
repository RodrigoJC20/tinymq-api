@echo off
rem Activate virtual environment and run the GUI

rem Change to script directory
cd /d "%~dp0"

rem Check if virtual environment exists
if not exist gui_venv (
    echo Creating virtual environment...
    python3.12 -m venv gui_venv
    
    echo Installing dependencies...
    call gui_venv\Scripts\activate
    pip install -r gui/requirements.txt
) else (
    rem Activate virtual environment
    call gui_venv\Scripts\activate
)

rem Run the application
echo Starting TinyMQ GUI...
python start_gui.py

rem Deactivate virtual environment
call deactivate 