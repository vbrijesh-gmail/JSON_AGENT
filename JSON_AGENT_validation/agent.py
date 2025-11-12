from google.adk.agents.llm_agent import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
import json
from typing import Any, Dict, Optional
import tempfile
import os
import asyncio
from pathlib import Path
from schema_validator import SchemaValidator


def read_json_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(path: str, data: Dict[str, Any], indent: int) -> str:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    return "written"


json_agent = Agent(
    model='gemini-2.5-flash',
    name='json_agent',
    description='Reads and modifies JSON files when given a file path and instructions.',
    instruction='When a file path to a JSON file is provided, read it first using read_json_file, then apply the requested changes and write the updated JSON back using write_json_file.',
    tools=[read_json_file, write_json_file],
)

# Runner and session helpers
_runner = InMemoryRunner(agent=json_agent, app_name='json_agent_app')


async def run_json_task(
    prompt: str, 
    json_obj: Dict[str, Any], 
    schema_path: Optional[str] = None
) -> Dict[str, Any]:
    """Accepts a natural language prompt and a JSON object, and returns the modified JSON.

    Args:
        prompt: Natural language instructions for modifying the JSON
        json_obj: The JSON object to modify
        schema_path: Optional path to a JSON schema file for validation
        
    Returns:
        The modified JSON object
        
    Raises:
        ValueError: If JSON validation against schema fails
    """
    # Initialize schema validator if schema path is provided
    validator = None
    if schema_path:
        if not Path(schema_path).exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        validator = SchemaValidator.from_file(schema_path)
        
        # Validate input JSON against schema
        validation_result = validator.validate_json(json_obj)
        if not validation_result["is_valid"]:
            raise ValueError(f"Input JSON validation failed: {validation_result['error']}")
    
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    tmp_path = tmp.name
    tmp.close()
    try:
        write_json_file(tmp_path, json_obj, 2)
        user_prompt = (
            f"You are given a JSON file at: {tmp_path}.\n"
            f"Task: {prompt}.\n"
            f"Steps:\n"
            f"1) Call read_json_file to load it.\n"
            f"2) Apply the requested changes precisely.\n"
            f"3) Call write_json_file to save the updated JSON back to the same path.\n"
        )

        # Create a session and invoke the agent via the runner
        session = await _runner.session_service.create_session(
            app_name='json_agent_app',
            user_id='user'
        )
        content = types.Content(
            role='user',
            parts=[types.Part.from_text(text=user_prompt)]
        )
        print("[DEBUG] Invoking agent via runner.run")
        try:
            for event in _runner.run(
                user_id='user',
                session_id=session.id,
                new_message=content,
            ):
                # Optionally, you could log events here
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print("[DEBUG] Agent output:", part.text)
        except Exception as e:
            print("[DEBUG] Runner.run raised exception:", e)
            raise

        # Read back the (possibly) updated JSON
        updated = read_json_file(tmp_path)
        
        # Validate output JSON against schema if validator is set
        if validator:
            validation_result = validator.validate_json(updated)
            if not validation_result["is_valid"]:
                raise ValueError(f"Output JSON validation failed: {validation_result['error']}")
                
        return updated
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
