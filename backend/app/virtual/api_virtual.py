from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.virtual.openSdkv2 import run_virtual_agents

app = FastAPI()

# Allow frontend (virtual.html) to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.post("/virtual")
async def analyze_case(request: Request):
    try:
        data = await request.json()
        user_query = data.get("user_query")

        if not user_query:
            return JSONResponse(status_code=400, content={"error": "Missing 'user_query'"})

        result = run_virtual_agents(user_query)  # 🚀 Logic from openSdk used here
        return {"result": result}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})