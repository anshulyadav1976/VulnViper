# File: vulnviper/llm/clients.py
from typing import Dict
from .openai_client import analyze_chunk_openai
from .gemini_client import analyze_chunk_gemini

# Default models if not specified in config
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-latest"

def audit_chunk_with_llm(code_chunk: str, api_key: str, provider: str, model: str = None) -> Dict:
    """
    Audits a code chunk using the specified LLM provider and model.

    Args:
        code_chunk: The string of code to audit.
        api_key: The API key for the LLM provider.
        provider: The LLM provider ("openai" or "gemini").
        model: The specific model to use. If None, uses default for the provider.

    Returns:
        A dictionary containing the analysis result.
    """
    if provider == "openai":
        actual_model = model if model else DEFAULT_OPENAI_MODEL
        return analyze_chunk_openai(api_key=api_key, code_chunk=code_chunk, model_name=actual_model)
    elif provider == "gemini":
        actual_model = model if model else DEFAULT_GEMINI_MODEL
        return analyze_chunk_gemini(api_key=api_key, code_chunk=code_chunk, model_name=actual_model)
    else:
        # Fallback or error for unsupported provider
        return {"error": f"Unsupported LLM provider: {provider}", "summary": "", "vulnerabilities": [], "dependencies": []} 