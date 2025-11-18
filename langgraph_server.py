"""
LangGraph Server Entry Point for Agent-Chat-UI

This file exposes your Airport AI Agent Swarm as a LangGraph server
that can be used with agent-chat-ui or deployed with LangGraph CLI.

Note: LangGraph CLI provides its own checkpointer (PostgreSQL-based).
We don't use Redis here to avoid connection issues.

Usage:
    langgraph dev  # For local development
    langgraph up   # For production
"""

import asyncio
import structlog
from dotenv import load_dotenv
from agent import agent

load_dotenv()


logger = structlog.get_logger()


def initialize_app():
    """Initialize and return the compiled LangGraph app"""
    try:
        logger.info("Initializing Airport Agent Swarm for LangGraph server...")
        
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Create agents without checkpointer (LangGraph Server handles persistence automatically)
        async def build_graph():
            return await agent.initialize_agent(use_checkpointer=False)
        
        # Run the async initialization
        app = loop.run_until_complete(build_graph())
        
        logger.info("Agent initialized successfully!")
        return app
        
    except Exception as e:
        logger.error(f"Failed to initialize swarm: {e}", exc_info=True)
        raise


# This is what LangGraph CLI will look for
# It expects a compiled StateGraph
graph = initialize_app()

logger.info("LangGraph server ready! Graph exposed as 'graph', 'app', and 'agent'")

