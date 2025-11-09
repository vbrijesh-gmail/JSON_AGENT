from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from typing import Optional, Dict, Any
import json
import uvicorn
import os
from pathlib import Path

# Import the json agent runner
from json_agent import run_json_task

app = FastAPI(title="JSON Agent API")

# CORS for local development and the React UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_DIR = Path(__file__).resolve().parent
STATIC_DIR = ROOT_DIR / "static"
INDEX_FILE = STATIC_DIR / "index.html"

@app.get("/")
async def index() -> HTMLResponse:
    if INDEX_FILE.exists():
        return HTMLResponse(INDEX_FILE.read_text(encoding="utf-8"))
    return HTMLResponse("<h3>JSON Agent API</h3>")

@app.post("/api/modify")
async def modify_json(
    prompt: str = Form(...),
    file: Optional[UploadFile] = File(None),
    json_text: Optional[str] = Form(None),
) -> JSONResponse:
    # Validate input
    if not file and not json_text:
        raise HTTPException(status_code=400, detail="Provide either a JSON file upload or json_text.")
    if file and json_text:
        raise HTTPException(status_code=400, detail="Provide only one of file or json_text, not both.")

    try:
        if file:
            # Read uploaded file contents
            raw = await file.read()
            obj = json.loads(raw.decode("utf-8"))
        else:
            obj = json.loads(json_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    # Run the agent task
    try:
        updated: Dict[str, Any] = await run_json_task(prompt, obj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    return JSONResponse(content={
        "updated": updated,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("json_agent.web.app:app", host="0.0.0.0", port=port, reload=True)
