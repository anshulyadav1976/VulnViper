# File: vulnviper/llm/gemini_client.py
import google.generativeai as genai
from typing import Dict
import json

# Using a similar prompt structure for consistency
GEMINI_PROMPT_TEMPLATE = """You are a secure code auditor. Analyze the following Python code chunk for security vulnerabilities.
Provide your answer as a JSON object with keys: "summary", "vulnerabilities", "recommendations", "dependencies".
Code Chunk:
{code}"""

def analyze_chunk_gemini(api_key: str, code_chunk: str, model_name: str = "gemini-2.5-flash-latest") -> Dict:
    """
    Sends a code chunk to the Gemini API for security analysis.
    Returns the parsed JSON result.
    """
    genai.configure(api_key=api_key)
    prompt = GEMINI_PROMPT_TEMPLATE.format(code=code_chunk)
    model = genai.GenerativeModel(model_name)
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                temperature=0.0
            )
        )
        
        text_content = response.text.strip()
        # Basic cleaning for potential markdown ```json ... ```
        if text_content.startswith("```json"):
            text_content = text_content[7:]
        if text_content.endswith("```"):
            text_content = text_content[:-3]
        
        result = json.loads(text_content)

    except json.JSONDecodeError as e:
        result = {"raw_output": response.text if 'response' in locals() else "No response", "error": f"Failed to parse JSON: {str(e)}"}
    except Exception as e:
        result = {"raw_output": "", "error": f"Gemini API call failed: {str(e)}"}
        
    return result 