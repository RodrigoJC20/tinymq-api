import os
import secrets
from typing import Dict, Optional

# API Settings
API_HOST = "0.0.0.0"  # Listen on all interfaces
API_PORT = 8000       # Default port for API
API_TITLE = "TinyMQ API"
API_DESCRIPTION = "REST API for accessing TinyMQ broker's database"
API_VERSION = "0.1.0"

# Default admin credentials - should be changed after first login
# These will be used to initialize the admin user if it doesn't exist
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin"

# JWT Settings
# Generate a new secret key on startup if one doesn't exist
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour

# Database Settings
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "tinymq")
DB_USER = os.getenv("DB_USER", "tinymq_broker")
DB_PASSWORD = os.getenv("DB_PASSWORD", "tinymq_password")
DB_PORT = int(os.getenv("DB_PORT", "5432"))

# Connection string for SQLAlchemy
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Page size for pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100

class Settings:
    """Application settings"""
    api_host: str = API_HOST
    api_port: int = API_PORT
    api_title: str = API_TITLE
    api_description: str = API_DESCRIPTION
    api_version: str = API_VERSION
    jwt_secret_key: str = JWT_SECRET_KEY
    jwt_algorithm: str = JWT_ALGORITHM
    jwt_access_token_expire_minutes: int = JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    database_url: str = DATABASE_URL
    default_page_size: int = DEFAULT_PAGE_SIZE
    max_page_size: int = MAX_PAGE_SIZE

settings = Settings() 