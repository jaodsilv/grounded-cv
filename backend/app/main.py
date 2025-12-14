"""GroundedCV FastAPI Application Entry Point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rich.logging import RichHandler

from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger("grounded-cv")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")

    # Ensure data directories exist
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.master_resume_dir.mkdir(parents=True, exist_ok=True)
    settings.market_research_dir.mkdir(parents=True, exist_ok=True)
    settings.company_research_dir.mkdir(parents=True, exist_ok=True)
    settings.base_resumes_dir.mkdir(parents=True, exist_ok=True)
    settings.tailored_dir.mkdir(parents=True, exist_ok=True)
    settings.templates_dir.mkdir(parents=True, exist_ok=True)

    yield

    # Shutdown
    logger.info("Shutting down GroundedCV")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-agentic AI Resume, CV, and Cover Letter tailoring system",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


# API info endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "tagline": "Your story. Truthfully tailored.",
        "docs": "/docs",
        "health": "/health",
    }


# Import and include routers
# from app.api import documents, master_resume, research, generation, debug, websocket
# app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
# app.include_router(master_resume.router, prefix="/api/master-resume", tags=["Master Resume"])
# app.include_router(research.router, prefix="/api/research", tags=["Research"])
# app.include_router(generation.router, prefix="/api/generation", tags=["Generation"])
# app.include_router(debug.router, prefix="/api/debug", tags=["Debug"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
