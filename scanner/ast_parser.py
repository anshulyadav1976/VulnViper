# File: secureaudit/scanner/ast_parser.py
import ast
from pathlib import Path
from typing import List, Dict


def parse_file_to_chunks(filepath: Path) -> List[Dict]:
    """
    Parse a Python file into chunks based on top-level functions and classes.
    Returns a list of dicts with metadata and code.
    """
    source = filepath.read_text(encoding='utf-8')
    tree = ast.parse(source)
    chunks: List[Dict] = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno - 1
            end = getattr(node, 'end_lineno', None)
            if end is None:
                # Fallback: read until next node or EOF
                end = node.lineno
            # Extract the source lines for this chunk
            lines = source.splitlines()[start:end]
            chunk_code = "\n".join(lines)
            chunks.append({
                'name': node.name,
                'type': type(node).__name__,  # FunctionDef, AsyncFunctionDef, or ClassDef
                'start_line': start + 1,
                'end_line': end,
                'code': chunk_code
            })

    # If no functions or classes found, treat entire file as one chunk
    if not chunks:
        chunks.append({
            'name': filepath.stem,
            'type': 'Module',
            'start_line': 1,
            'end_line': len(source.splitlines()),
            'code': source
        })

    return chunks
