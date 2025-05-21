# File: vulnviper/config.py
import os
import json
from pathlib import Path

# Path to store user config
CONFIG_PATH = Path('.vulnviper_config')

def save_config(api_key: str, llm_provider: str, llm_model: str = None):
    """
    Saves the API key, LLM provider, and optionally the model to the config file.
    """
    config = {
        "api_key": api_key,
        "llm_provider": llm_provider,
        "llm_model": llm_model
    }
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"✅ Configuration saved to {CONFIG_PATH}")

def load_config() -> dict:
    """
    Loads the API key, LLM provider, and model from environment variables or config file.
    Returns a dictionary with 'api_key', 'llm_provider', and 'llm_model'.
    Raises an error if essential config is not found.
    """
    config = {
        "api_key": os.getenv("VULNVIPER_API_KEY"),
        "llm_provider": os.getenv("VULNVIPER_LLM_PROVIDER"),
        "llm_model": os.getenv("VULNVIPER_LLM_MODEL")
    }

    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            data = json.load(f)
            if not config["api_key"] and "api_key" in data:
                config["api_key"] = data["api_key"]
            if not config["llm_provider"] and "llm_provider" in data:
                config["llm_provider"] = data["llm_provider"]
            if not config["llm_model"] and "llm_model" in data:
                config["llm_model"] = data.get("llm_model") # Model is optional
    
    if not config["api_key"]:
        raise RuntimeError(
            "API key not found. Please run 'vulnviper init' or set VULNVIPER_API_KEY."
        )
    if not config["llm_provider"]:
        # Default to openai if not set, or raise error
        # For now, let's require it to be set during init
        raise RuntimeError(
            "LLM provider not found. Please run 'vulnviper init' or set VULNVIPER_LLM_PROVIDER."
        )
        
    return config
