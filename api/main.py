"""
Main FastAPI Application for YiChin Chatbot System

Provides OpenAI-compatible chat endpoints for chatbot integration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from api.routers import chatbot_response
from agent.agent import initialize_agent

# Initialize logger
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Initializes agent at startup and cleans up at shutdown.
    """
    # Startup: Initialize agent
    logger.info("Initializing agent...")
    await initialize_agent()
    logger.info("Agent initialized successfully")
    
    yield
    
    # Shutdown: Cleanup (if needed)
    logger.info("Shutting down...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="YiChin Chatbot API",
    version="1.0.0",
    description="億進寢具 Chatbot API with RAG and conversation memory",
    lifespan=lifespan
)

# CORS middleware (for web frontends)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chatbot_response.router, prefix="/chatbot", tags=["ChatBot"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "YiChin Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/chatbot/get_agent_answer/",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy", "service": "yichin-chatbot"}

