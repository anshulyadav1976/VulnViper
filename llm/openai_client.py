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
    try:
        result = json.loads(text)
    except Exception:
        # Fallback: return raw text on parse error
        result = {"raw_output": text}
    return result
