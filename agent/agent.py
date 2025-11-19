from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langsmith import uuid7

from agent.memory.checkpointer import get_shared_checkpointer
from agent.tools.tool import rag_search, product_search, product_filter
from agent.prompt.read_prompt import SYSTEM_PROMPT_TEMPLATE

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
        system_prompt=SYSTEM_PROMPT_TEMPLATE,
    )
    
    return agent