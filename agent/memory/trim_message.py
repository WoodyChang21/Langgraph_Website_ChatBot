from langchain.agents.middleware.types import before_model, AgentState
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.graph.message import RemoveMessage, REMOVE_ALL_MESSAGES
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from typing import Any

MAX_CONVERSATION_LENGTH = 25

# Create middleware for message trimming
@before_model
def trim_messages_middleware(state: AgentState, runtime: Any = None) -> dict[str, any] | None:
    """Trim messages before model call to stay within token limits."""
    trimmed_messages = trim_messages(
        state["messages"],
        max_tokens=MAX_CONVERSATION_LENGTH,  # Rough estimate (adjust as needed)
        strategy="last",  # Keep most recent
        token_counter=len,  # Simple counter
        include_system=True,  # Always keep system prompts
        allow_partial=False,  # Don't split messages
        start_on="human",  # ← KEY: Prevents incomplete tool calls!
    )
    # Return trimmed messages to be used by the model
    # return {"messages": trimmed_messages}

    return {
        "messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *trimmed_messages]
    }