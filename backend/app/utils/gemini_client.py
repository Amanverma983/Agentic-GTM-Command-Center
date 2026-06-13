import json
import logging
import google.generativeai as genai
from app.config import settings
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel

logger = logging.getLogger("gtm_center.gemini_client")

# Configure genai SDK if key is set
api_available = False
if settings.gemini_api_key:
    try:
        genai.configure(api_key=settings.gemini_api_key)
        api_available = True
    except Exception as e:
        logger.error(f"Failed to configure Gemini SDK: {e}")

def call_gemini(
    prompt: str,
    system_instruction: Optional[str] = None,
    response_schema: Optional[Type[BaseModel]] = None,
    mock_fallback_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calls Gemini 2.5 Flash API with system instructions and optional JSON schemas.
    Falls back to mock_fallback_data if API key is not present or an error occurs.
    """
    if not api_available or not settings.gemini_api_key:
        logger.warning("Gemini API key not configured or invalid. Using mock fallback data.")
        return mock_fallback_data or {}

    try:
        # We use gemini-2.5-flash
        model_name = "gemini-2.5-flash"
        
        generation_config = {}
        if response_schema:
            generation_config = {
                "response_mime_type": "application/json",
                "response_schema": response_schema
            }

        # Create model instance
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            generation_config=generation_config
        )

        logger.info(f"Invoking {model_name}...")
        response = model.generate_content(prompt)
        
        # Parse JSON output
        text_content = response.text.strip()
        
        # Check if text is wrapped in ```json ... ```
        if text_content.startswith("```json"):
            text_content = text_content[7:]
            if text_content.endswith("```"):
                text_content = text_content[:-3]
        elif text_content.startswith("```"):
            text_content = text_content[3:]
            if text_content.endswith("```"):
                text_content = text_content[:-3]
                
        text_content = text_content.strip()
        parsed_response = json.loads(text_content)
        
        # Validate schema if provided
        if response_schema:
            validated = response_schema.model_validate(parsed_response)
            return validated.model_dump()
            
        return parsed_response

    except Exception as e:
        logger.error(f"Gemini API invocation error: {str(e)}. Falling back to mock data.")
        if mock_fallback_data:
            return mock_fallback_data
        raise e
