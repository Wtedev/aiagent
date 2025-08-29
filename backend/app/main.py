"""backend/app/main.py
FastAPI application entry‑point.
Run with:
    uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Any, Dict

from backend.app.virtual.api_virtual import run_virtual_agents

load_dotenv()


def _parse_origins(env_value: str | None) -> list[str]:
    if not env_value or env_value.strip() == "*":
        return ["*"]
    return [o.strip() for o in env_value.split(",") if o.strip()]

# ────────────────────────────────────────────────
# FastAPI instance
# ────────────────────────────────────────────────

app = FastAPI(title="Qanoneed API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_origins(os.getenv("CORS_ORIGINS", "*")),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/Style", StaticFiles(directory="Style"), name="style")

# Routers -----------------------------------------------------------
from backend.app.chatbot.api_chat import router as chat_router

app.include_router(chat_router, prefix="/api")

# Frontend Routes ---------------------------------------------------
@app.get("/")
async def serve_homepage():
    """Serve the main homepage"""
    return FileResponse("Style/index.html")

@app.get("/chat")
async def serve_chat():
    """Serve the chat interface"""
    return FileResponse("Style/chat.html")

@app.get("/virtual")
async def serve_virtual():
    """Serve the virtual ruling interface"""
    return FileResponse("Style/virtual.html")

@app.get("/roadmap")
async def serve_roadmap():
    """Serve the roadmap interface"""
    return FileResponse("Style/roadmap.html")

# API Routes --------------------------------------------------------
class VirtualRequest(BaseModel):
    user_query: Any  

@app.post("/virtual")
async def virtual_consultation(req: VirtualRequest):
   
    result = run_virtual_agents(req.user_query)
    return {"result": result}

from backend.app.roadmap.api_roadmap import router as roadmap_router
app.include_router(roadmap_router)

# Health‑check ------------------------------------------------------

@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Simple uptime probe for load balancers."""
    return {"status": "ok"}

# ------------------------------------------------------------------
# Optional: run via `python -m app.main`
# ------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn 

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
