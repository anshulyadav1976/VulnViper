# File: secureaudit/scanner/file_walker.py
import subprocess
from pathlib import Path
from typing import List


def get_target_files(base_dir: str) -> List[Path]:
    """
    Return a list of Python files to audit.
    Prioritize staged files in a git repo, else walk the directory.
    """
    base = Path(base_dir)
    files: List[Path] = []
    # Attempt to find staged files in a git repository
    git_dir = base / ".git"
    if git_dir.exists() and git_dir.is_dir():
        try:
            result = subprocess.check_output(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                cwd=base
            )
            staged = [
                base / Path(p.strip())
                for p in result.decode().splitlines()
                if p.strip().endswith(".py")
            ]
            if staged:
                return staged
        except subprocess.CalledProcessError:
            pass

    # Fallback: walk entire directory for .py files
    for path in base.rglob("*.py"):
        # Skip virtualenvs and cache folders
        str_path = str(path)
        if "site-packages" in str_path or "__pycache__" in str_path:
            continue
        files.append(path)
    return files
