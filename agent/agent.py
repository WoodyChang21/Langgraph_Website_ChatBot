from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from agent.memory.trim_message import trim_messages_middleware
from agent.memory.checkpointer import get_shared_checkpointer
from agent.tools.tool import rag_search, product_search, product_filter
from agent.prompt.read_prompt import SYSTEM_PROMPT_TEMPLATE

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Global agent instance (initialized on import)
agent = None


async def initialize_agent(use_checkpointer: bool = True):
    """
    Initialize the global agent instance.
    Automatically called when this module is imported.
    
    Args:
        use_checkpointer: If True, uses Redis checkpointer for conversation memory.
                         If False, no checkpointer (for LangGraph Server mode).
    """
    global agent

    if agent is not None:
        return agent
    
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
        middleware=[trim_messages_middleware],  # ← Add middleware here
    )
    
    return agent


# def _initialize_agent_sync():
#     """Synchronous wrapper to initialize agent on import."""
#     try:
#         # Try to get the current event loop
#         loop = asyncio.get_running_loop()
#         # If we get here, loop is already running - can't use asyncio.run()
#         # This shouldn't happen on import, but if it does, we'll initialize lazily
#         return
#     except RuntimeError:
#         # No event loop is running, safe to create one
#         try:
#             # Try to use existing loop if available
#             loop = asyncio.get_event_loop()
#             if loop.is_closed():
#                 # Loop is closed, create a new one
#                 asyncio.run(initialize_agent())
#             else:
#                 # Loop exists and is not closed, use it
#                 loop.run_until_complete(initialize_agent())
#         except RuntimeError:
#             # No event loop exists at all, create a new one
#             asyncio.run(initialize_agent())


# # Initialize agent when module is imported
# _initialize_agent_sync()