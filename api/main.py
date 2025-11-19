"""
Main FastAPI Application for YiChin Chatbot System

Provides OpenAI-compatible chat endpoints for chatbot integration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from api.routers import chatbot_response
# Agent is automatically initialized when imported
from agent.agent import agent

# Initialize logger
logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="YiChin Chatbot API",
    version="1.0.0",
    description="億進寢具 Chatbot API with RAG and conversation memory",
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

