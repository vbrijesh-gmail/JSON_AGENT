import os
import sys
import uvicorn
from dotenv import load_dotenv
from pathlib import Path

def main():
    """Entry point for the JSON Agent server."""
    # Add current directory to path for local imports
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Load .env file from the same directory as this script
    env_path = current_dir / '.env'
    load_dotenv(dotenv_path=env_path)

    port = int(os.environ.get("PORT", 8002))
    print(f"Starting JSON Agent server on http://0.0.0.0:{port}")
    print(f"Web UI: http://localhost:{port}/")
    print(f"API Docs: http://localhost:{port}/docs")
    
    # Import app directly from local files
    from web.app import app
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    main()
