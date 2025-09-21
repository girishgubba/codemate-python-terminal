import os
from pathlib import Path

ROOT = Path.cwd().resolve()

def resolve_path(p: str | None) -> Path:
    if not p:
        return Path.cwd().resolve()
    return (Path.cwd() / p).expanduser().resolve()

def safe_path(p: str | None) -> Path:
    target = resolve_path(p)
    # Soft sandbox: allow anywhere but normalize; tweak if strict sandbox is needed
    return target

def format_error(msg: str) -> str:
    return f"error: {msg}"

def split_redirection(tokens: list[str]):
    # Support simple `echo "x" > file` style
    if ">" in tokens:
        idx = tokens.index(">")
        return tokens[:idx], (">", tokens[idx+1] if idx+1 < len(tokens) else None)
    if ">>" in tokens:
        idx = tokens.index(">>")
        return tokens[:idx], (">>", tokens[idx+1] if idx+1 < len(tokens) else None)
    return tokens, None
