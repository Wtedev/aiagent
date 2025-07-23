from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.app.services import run_roadmap   

router = APIRouter(prefix="/api", tags=["roadmap"])

class RoadmapRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/roadmap", response_model=ChatResponse)
async def roadmap_endpoint(req: RoadmapRequest, request: Request):
    answer = await run_roadmap(req.question)
    return {"answer": answer}