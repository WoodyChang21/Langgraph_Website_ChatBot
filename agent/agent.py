# Note: Using langgraph.prebuilt.create_react_agent despite deprecation warning
# because it's the only version that supports checkpointer parameter.
# The deprecation suggests using langchain.agents.create_agent, but that version
# doesn't support checkpointer. This version still works and is the recommended
# approach for agents with memory/checkpointing.
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk
from langsmith import uuid7

from agent.memory.checkpointer import get_shared_checkpointer
from agent.tools.tool import rag_search, product_search, product_filter


# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Global agent instance (initialized at startup)
agent = None


async def initialize_agent(use_checkpointer: bool = True):
    """
    Initialize the global agent instance.
    Call this once at application startup (e.g., in FastAPI lifespan).
    
    Args:
        use_checkpointer: If True, uses Redis checkpointer for conversation memory.
                         If False, no checkpointer (for LangGraph Server mode).
    """
    global agent
    
    # Get checkpointer if needed
    checkpointer = None
    if use_checkpointer:
        checkpointer = await get_shared_checkpointer()
    
    # Create ReAct agent
    agent = create_agent(
        model=llm,
        tools=[rag_search, product_search, product_filter],
        checkpointer=checkpointer,
    )
    
    return agent