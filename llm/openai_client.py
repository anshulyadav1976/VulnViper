# File: vulnviper/llm/openai_client.py
from openai import OpenAI
from typing import Dict
import json

# Example prompt template
PROMPT_TEMPLATE = '''
You are a secure code auditor. Analyze the following Python code chunk for security vulnerabilities.
Provide your answer as a JSON object with keys:
- "summary": short description of what the code does
- "vulnerabilities": list of found vulnerabilities or concerns
- "recommendations": list of suggested fixes or mitigations
### Code Chunk:
```python
{code}
```
'''

def analyze_chunk_openai(api_key: str, code_chunk: str, model_name: str = "gpt-4o-mini") -> Dict:
    """
    Sends a code chunk to the OpenAI API for security analysis.
    Returns the parsed JSON result.
    """
    client = OpenAI(api_key=api_key)
    prompt = PROMPT_TEMPLATE.format(code=code_chunk)
    resp = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are an expert security auditor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    text = resp.choices[0].message.content.strip()
    
    # Attempt to strip markdown code fences if present
    if text.startswith("```json\n") and text.endswith("\n```"):
        text = text[len("```json\n"):-len("\n```")]
    elif text.startswith("```") and text.endswith("```"):
        # Generic fallback if ```json is not present but ``` is
        text = text[3:-3]
        # Further strip potential newlines if the content was on its own line
        text = text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError as e:
        # Fallback: return raw text and error on parse error
        result = {
            "error": f"LLM response could not be parsed as JSON: {e}",
            "raw_output": text
        }
    return result
