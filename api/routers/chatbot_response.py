"""
Chat completion router - OpenAI-compatible endpoints
"""

from fastapi import HTTPException, APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
import structlog

from agent.agent_response import get_agent_answer, get_agent_answer_stream
from langsmith import uuid7

logger = structlog.get_logger()

router = APIRouter()

# 取得 response
@router.get("/get_agent_answer/")
async def get_agent_answer_api(
    question: str = Query(..., description="使用者提出的問題"),
    uuid: str = Query(default="", description="使用者的唯一 ID"),
):
    """
    Get agent answer for a user question.
    Uses global agent instance (initialized at app startup).
    """
    try:
        # Use provided UUID or generate a new one
        user_id = uuid if uuid else str(uuid7())
        if not question:
            logger.warning("invalid_input_empty_question", input=question)
            raise HTTPException(status_code=400, detail="問題內容不可為空。")
        
        # Get answer from global agent
        answer = await get_agent_answer(user_request=question, uuid=user_id)
        
        return {
            "answer": answer,
            "uuid": user_id,
            "record_id": "default_record_id",  # Placeholder for future use
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception("exception_in_answer", error=str(e))
        raise HTTPException(status_code=500, detail=f"伺服器內部錯誤：{str(e)}")

@router.get("/get_agent_answer_stream/")
async def get_agent_answer_stream_api(
    question: str = Query(..., description="使用者提出的問題"),
    uuid: str = Query(default="", description="使用者的唯一 ID"),
):
    """
    Stream agent answer token by token using Server-Sent Events (SSE).
    """
    
    try:
        user_id = uuid if uuid else str(uuid7())
        if not question:
            logger.warning("invalid_input_empty_question", input=question)
            raise HTTPException(status_code=400, detail="問題內容不可為空。")
        
        async def generate():
            """Generator function for streaming tokens"""
            try:
                async for token in get_agent_answer_stream(
                    user_request=question, 
                    uuid=user_id
                ):
                    # Format as Server-Sent Events (SSE)
                    # Format: data: <json>\n\n
                    yield f"data: {json.dumps({'token': token, 'uuid': user_id}, ensure_ascii=False)}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'done': True, 'uuid': user_id}, ensure_ascii=False)}\n\n"
            except Exception as e:
                logger.exception("exception_in_stream", error=str(e))
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            }
        )
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception("exception_in_stream_endpoint", error=str(e))
        raise HTTPException(status_code=500, detail=f"伺服器內部錯誤：{str(e)}")