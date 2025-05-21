# File: secureaudit/scanner/chunker.py
from typing import List, Dict
from ..utils.tokenizer import count_tokens


def chunk_by_token_limit(chunks: List[Dict], max_tokens: int = 2000) -> List[Dict]:
    """
    Further split or filter chunks based on token limit.
    If a chunk exceeds the limit, it will be broken into smaller text blocks.
    """
    new_chunks = []
    for chunk in chunks:
        code = chunk['code']
        tokens = count_tokens(code)

        if tokens <= max_tokens:
            new_chunks.append(chunk)
            continue

        # Fallback: break into paragraphs or smaller blocks
        lines = code.split('\n')
        block = []
        block_token_count = 0
        block_start_line = chunk['start_line']

        for i, line in enumerate(lines):
            block.append(line)
            block_token_count += count_tokens(line)

            if block_token_count >= max_tokens or i == len(lines) - 1:
                chunk_copy = chunk.copy()
                chunk_copy['code'] = '\n'.join(block)
                chunk_copy['start_line'] = block_start_line
                chunk_copy['end_line'] = block_start_line + len(block) - 1
                new_chunks.append(chunk_copy)
                block = []
                block_token_count = 0
                block_start_line = chunk['start_line'] + i + 1

    return new_chunks