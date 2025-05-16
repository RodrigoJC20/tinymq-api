#!/usr/bin/env python3
"""
TinyMQ API Launcher
-------------------
This script launches the TinyMQ API on the Raspberry Pi.
"""

import os
import sys
import argparse
from api.config import settings

# Make sure we're in the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def parse_args():
    parser = argparse.ArgumentParser(description='TinyMQ API Server')
    parser.add_argument('--host', type=str, default=settings.api_host,
                        help=f'Host to bind to (default: {settings.api_host})')
    parser.add_argument('--port', type=int, default=settings.api_port,
                        help=f'Port to bind to (default: {settings.api_port})')
    parser.add_argument('--db-host', type=str, default=os.getenv('DB_HOST', 'localhost'),
                        help='PostgreSQL host (default: localhost)')
    parser.add_argument('--db-name', type=str, default=os.getenv('DB_NAME', 'tinymq'),
                        help='PostgreSQL database name (default: tinymq)')
    parser.add_argument('--db-user', type=str, default=os.getenv('DB_USER', 'tinymq_broker'),
                        help='PostgreSQL user (default: tinymq_broker)')
    parser.add_argument('--db-password', type=str, default=os.getenv('DB_PASSWORD', 'tinymq_password'),
                        help='PostgreSQL password (default: tinymq_password)')
    parser.add_argument('--db-port', type=int, default=os.getenv('DB_PORT', '5432'),
                        help='PostgreSQL port (default: 5432)')
    parser.add_argument('--reload', action='store_true',
                        help='Enable auto-reload for development')
    
    return parser.parse_args()

def main():
    # Parse command-line arguments
    args = parse_args()
    
    # Set environment variables for database connection
    os.environ['DB_HOST'] = args.db_host
    os.environ['DB_NAME'] = args.db_name
    os.environ['DB_USER'] = args.db_user
    os.environ['DB_PASSWORD'] = args.db_password
    os.environ['DB_PORT'] = str(args.db_port)
    
    # Print startup message
    print("=" * 60)
    print(f"Starting TinyMQ API Server")
    print(f"Host: {args.host}, Port: {args.port}")
    print(f"Database: {args.db_name} on {args.db_host}")
    print("=" * 60)
    
    # Import here so environment variables are set before import
    import uvicorn
    from api.app import setup_database
    
    try:
        # Initialize the database
        setup_database()
        
        # Start the API server
        uvicorn.run(
            "api.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    except Exception as e:
        print(f"Error starting API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 