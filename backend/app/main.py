"""backend/app/main.py
FastAPI application entry‑point.
Run with:
    uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env, if present
load_dotenv()

# ────────────────────────────────────────────────
# Helper to turn CORS_ORIGINS env → list[str]
# ────────────────────────────────────────────────

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

# Routers -----------------------------------------------------------
from backend.app.api_chat import router as chat_router  # noqa: E402  (import after app for clarity)

app.include_router(chat_router, prefix="/api")

# Health‑check ------------------------------------------------------

@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Simple uptime probe for load balancers."""
    return {"status": "ok"}

# ------------------------------------------------------------------
# Optional: run via `python -m app.main`
# ------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn  # only imported when run directly

    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
