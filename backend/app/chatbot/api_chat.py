from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict

from backend.app.services import run_chat, run_chat_stream

router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    model_config = ConfigDict(extra='allow')  # Pydantic v2
    question: str

class ChatResponse(BaseModel):
    model_config = ConfigDict(extra='allow')  # Pydantic v2
    answer: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    """Return one complete answer for the given question."""
    try:
        answer = await run_chat(payload.question)
        return {"answer": answer}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/chat/stream")
async def chat_stream(question: str):
    """Stream the answer token-by-token using SSE."""
    async def event_generator():
        try:
            async for chunk in run_chat_stream(question):
                yield f"data: {chunk}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {str(exc)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
