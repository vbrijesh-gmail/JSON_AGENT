from typing import Dict, Any, Optional
import json
from jsonschema import validate, ValidationError, SchemaError

class SchemaValidator:
    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Initialize SchemaValidator with an optional JSON schema.
        If no schema is provided, it must be set later using set_schema().
        """
        self.schema = schema

    def set_schema(self, schema: Dict[str, Any]) -> None:
        """Set or update the JSON schema for validation."""
        self.schema = schema

    def validate_json(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate JSON data against the schema.
        
        Args:
            json_data: The JSON data to validate
            
        Returns:
            Dict containing 'is_valid' (bool) and 'error' (str if validation failed)
            
        Raises:
            SchemaError: If the schema itself is invalid
        """
        if not self.schema:
            raise ValueError("No schema provided. Please set a schema using set_schema() first.")
        
        try:
            validate(instance=json_data, schema=self.schema)
            return {"is_valid": True, "error": None}
        except ValidationError as e:
            return {
                "is_valid": False,
                "error": f"Validation error: {e.message} at path: {'/'.join(map(str, e.absolute_path))}"
            }
        except SchemaError as e:
            raise SchemaError(f"Invalid schema: {e}")

    @classmethod
    def from_file(cls, schema_path: str) -> 'SchemaValidator':
        """Create a SchemaValidator instance from a JSON schema file."""
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        return cls(schema)

    def validate_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate a JSON file against the schema.
        
        Args:
            file_path: Path to the JSON file to validate
            
        Returns:
            Dict containing 'is_valid' (bool) and 'error' (str if validation failed)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            return self.validate_json(json_data)
        except json.JSONDecodeError as e:
            return {
                "is_valid": False,
                "error": f"Invalid JSON: {str(e)}"
            }
        except Exception as e:
            return {
                "is_valid": False,
                "error": f"Error reading file: {str(e)}"
            }
