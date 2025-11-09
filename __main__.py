import os
import uvicorn
from dotenv import load_dotenv
from pathlib import Path

def main():
    """Entry point for the JSON Agent server."""
    # Load .env file from the same directory as this script
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)

    port = int(os.environ.get("PORT", 8000))
    print(f"Starting JSON Agent server on http://0.0.0.0:{port}")
    uvicorn.run("json_agent.web.app:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    main()
