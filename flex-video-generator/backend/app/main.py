"""
FastAPI application entry point for Flex Video Generator.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting Flex Video Generator API...")

    # Ensure storage directories exist
    settings.ensure_directories()

    # Initialize database tables
    init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down Flex Video Generator API...")


# Create FastAPI application
app = FastAPI(
    title="Flex Video Generator API",
    description="API for mass-generating Instagram flex/lifestyle videos",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Mount static file directories for serving media
storage_root = Path(settings.storage_root)
if storage_root.exists():
    app.mount("/storage", StaticFiles(directory=str(storage_root)), name="storage")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "Flex Video Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/settings/health"
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=True
    )
