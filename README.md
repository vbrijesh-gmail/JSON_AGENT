# JSON Agent

This package provides a Python-based agent that can read and modify JSON files based on a natural language prompt.

## Installation

To install the package, navigate to this directory and run:

```bash
pip install .
```

This will install the `json_agent` package and its dependencies.

## Usage

### As a Server

To start the web server, run the following command:

```bash
json-agent-server
```

This will start a FastAPI server with a web UI at `http://localhost:8000`.

### As a Library

You can also use the agent directly in your Python code:

```python
import asyncio
from json_agent import run_json_task

async def main():
    my_json = {"status": "pending"}
    prompt = "Change the status to 'completed'."
    updated_json = await run_json_task(prompt, my_json)
    print(updated_json)

if __name__ == "__main__":
    asyncio.run(main())
```
