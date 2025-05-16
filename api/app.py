import uvicorn
import logging
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from .models import Base, engine, get_db, User
from .config import settings
from .auth import (
    Token, authenticate_user, create_access_token, 
    initialize_admin_user, update_last_login
)

from .routes import auth, clients, topics, subscriptions, messages, events

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create tables in database
def setup_database():
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Initialize the first admin user if needed
        db = next(get_db())
        if initialize_admin_user(db):
            logger.info("Admin user initialized with default credentials")
            logger.warning("Please change the default admin password immediately")
        
    except Exception as e:
        logger.error(f"Database setup error: {e}")
        raise

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Login endpoint (outside of auth router for simplicity)
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login time
    update_last_login(db, user)
    
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Include routers
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(topics.router)
app.include_router(subscriptions.router)
app.include_router(messages.router)
app.include_router(events.router)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "endpoints": [
            "/token - Get authentication token",
            "/docs - API documentation",
            "/auth - Authentication endpoints",
            "/clients - Client management",
            "/topics - Topic management",
            "/subscriptions - Subscription management",
            "/messages - Message logs",
            "/events - Connection events"
        ]
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    setup_database()
    
    logger.info(f"Starting API server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    ) 