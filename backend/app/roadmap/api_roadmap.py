from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict

from backend.app.services import run_roadmap

router = APIRouter(tags=["roadmap"])

class RoadmapRequest(BaseModel):
    model_config = ConfigDict(extra='allow')  # Pydantic v2
    question: str

class ChatResponse(BaseModel):
    model_config = ConfigDict(extra='allow')  # Pydantic v2
    answer: str

@router.post("/roadmap", response_model=ChatResponse)
async def roadmap_endpoint(payload: RoadmapRequest):
    """Return roadmap for the given question."""
    try:
        answer = await run_roadmap(payload.question)
        return {"answer": answer}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))