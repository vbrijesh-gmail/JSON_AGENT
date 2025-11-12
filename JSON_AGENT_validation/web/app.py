from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
from typing import Optional, Dict, Any, List, Union
import json
import uvicorn
import os
import traceback
from pathlib import Path

# Import the json agent runner
# Works with or without package installation
import sys
from pathlib import Path
try:
    from json_agent import run_json_task
except ImportError:
    # Fallback: import from parent directory
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from agent import run_json_task

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

class ValidationErrorResponse(JSONResponse):
    def __init__(
        self,
        content: Any,
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
        **kwargs,
    ) -> None:
        super().__init__(content=content, status_code=status_code, **kwargs)

@app.exception_handler(ValueError)
async def validation_exception_handler(request, exc):
    return ValidationErrorResponse(
        content={
            "detail": str(exc),
            "type": "validation_error",
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
        }
    )

@app.post("/api/modify")
async def modify_json(
    prompt: str = Form(...),
    file: Optional[UploadFile] = File(None),
    json_text: Optional[str] = Form(None),
    schema_path: str = Form("deal_schema.json"),  # Default to deal_schema.json if not provided
) -> JSONResponse:
    if not file and not json_text:
        raise HTTPException(status_code=400, detail="Provide either a JSON file upload or json_text.")
    if file and json_text:
        raise HTTPException(status_code=400, detail="Provide only one of file or json_text, not both.")

    try:
        if file:
            # Read the uploaded file
            contents = await file.read()
            data = json.loads(contents)
        elif json_text:
            data = json.loads(json_text)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either file or json_text must be provided"
            )

        # Get the absolute path to the schema file
        schema_file = Path(schema_path)
        if not schema_file.is_absolute():
            # If relative path, assume it's relative to the project root
            schema_file = Path(__file__).parent.parent / schema_path

        # Process the JSON with the agent and schema validation
        updated_data = await run_json_task(
            prompt=prompt,
            json_obj=data,
            schema_path=str(schema_file)
        )
        
        return JSONResponse({
            "status": "success",
            "data": updated_data
        })

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format: {str(e)}"
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema file not found: {str(e)}"
        )
    except HTTPException:
        # Re-raise HTTP exceptions as is
        raise
    except Exception as e:
        # Log the full error for debugging
        print(f"Error processing request: {str(e)}")
        print(traceback.format_exc())
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8002))
    print(f"Starting JSON Agent FastAPI server on http://0.0.0.0:{port}")
    print(f"Web UI: http://localhost:{port}/")
    print(f"API Docs: http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
