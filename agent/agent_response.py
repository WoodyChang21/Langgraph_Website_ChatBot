from agent.agent import initialize_agent
from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk
from langsmith import uuid7



async def get_agent_answer(user_request: str, uuid: str):
    """
    Get agent answer for a user request.
    
    Args:
        user_request: User's question/message
        uuid: User's unique ID for conversation thread
    
    Returns:
        Agent's response content
    """
    agent = await initialize_agent()
    
    config = {"configurable": {"thread_id": uuid}}
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=user_request)]},
        config=config
    )
    return result["messages"][-1].content

async def get_agent_answer_stream(user_request: str, uuid: str):
    agent = await initialize_agent()
    
    config = {"configurable": {"thread_id": uuid}}
    async for chunk in agent.astream(
        {"messages": [HumanMessage(content=user_request)]},
        config=config,
        stream_mode="messages",
    ):
        chunk_message = chunk[0]
        if isinstance(chunk_message, AIMessageChunk):
            if chunk_message.content:
                yield chunk_message.content


if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Initialize agent once
        agent = await initialize_agent()
        config = {"configurable": {"thread_id": uuid7()}}
        
        while True:
            # LangGraph agents expect input as a dict with "messages" key
            user_input = input("User: ")
            result = await agent.ainvoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            print("Assistant: ", result["messages"][-1].content)
    

    async def stream_main():
        agent = await initialize_agent()
        config = {"configurable": {"thread_id": uuid7()}}
        async for chunk in get_agent_answer_stream("我要怎麼知道我的床墊尺寸，我是大學生", config["configurable"]["thread_id"]):
            print("Assistant: ", chunk)
    asyncio.run(stream_main())