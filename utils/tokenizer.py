# File: secureaudit/utils/tokenizer.py
import tiktoken

def count_tokens(text: str, model: str = 'gpt-4o-mini') -> int:
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))