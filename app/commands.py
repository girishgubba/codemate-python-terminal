import os
import shutil
from pathlib import Path
from typing import List
from .errors import CommandError
from .utils import safe_path, split_redirection

class CommandContext:
    def __init__(self):
        self.cwd = Path.cwd()

def write_output(out: str, redir):
    if not redir:
        return out
    op, path = redir
    if not path:
        raise CommandError("missing redirection target", "BAD_REDIR")
    target = safe_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if op == ">" else "a"
    with open(target, mode, encoding="utf-8") as f:
        f.write(out)
    return ""

def cmd_pwd(ctx: CommandContext, args: List[str], redir=None) -> str:
    if args:
        raise CommandError("pwd takes no arguments", "BAD_ARGS")
    out = str(Path.cwd()) + "\n"
    return write_output(out, redir)

def cmd_ls(ctx: CommandContext, args: List[str], redir=None) -> str:
    path = safe_path(args[0]) if args else Path.cwd()
    if not path.exists():
        raise CommandError(f"no such file or directory: {path}", "NOENT")
    if path.is_file():
        out = path.name + "\n"
    else:
        items = sorted(p.name + ("/" if (path / p).is_dir() else "") for p in os.listdir(path))
        out = "\n".join(items) + ("\n" if items else "")
    return write_output(out, redir)

def cmd_cd(ctx: CommandContext, args: List[str], redir=None) -> str:
    if len(args) != 1:
        raise CommandError("usage: cd <dir>", "BAD_ARGS")
    path = safe_path(args[0])
    if not path.exists() or not path.is_dir():
        raise CommandError(f"not a directory: {path}", "NOTDIR")
    os.chdir(path)
    ctx.cwd = Path.cwd()
    return ""

def cmd_mkdir(ctx: CommandContext, args: List[str], redir=None) -> str:
    if not args:
        raise CommandError("usage: mkdir <dir>...", "BAD_ARGS")
    for d in args:
        p = safe_path(d)
        p.mkdir(parents=True, exist_ok=True)
    return ""

def cmd_rm(ctx: CommandContext, args: List[str], redir=None) -> str:
    if not args:
        raise CommandError("usage: rm <path>...", "BAD_ARGS")
    for a in args:
        p = safe_path(a)
        if not p.exists():
            raise CommandError(f"no such file or directory: {p}", "NOENT")
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
    return ""

def cmd_cat(ctx: CommandContext, args: List[str], redir=None) -> str:
    if not args:
        raise CommandError("usage: cat <file>...", "BAD_ARGS")
    chunks = []
    for a in args:
        p = safe_path(a)
        if not p.exists() or not p.is_file():
            raise CommandError(f"not a file: {p}", "NOTFILE")
        with open(p, "r", encoding="utf-8") as f:
            chunks.append(f.read())
    out = ("\n".join(chunks)) + ("\n" if chunks and not chunks[-1].endswith("\n") else "")
    return out  # allow piping to redir by caller

def cmd_echo(ctx: CommandContext, args: List[str], redir=None) -> str:
    out = " ".join(args) + "\n"
    return write_output(out, redir)

def cmd_touch(ctx: CommandContext, args: List[str], redir=None) -> str:
    if not args:
        raise CommandError("usage: touch <file>...", "BAD_ARGS")
    for a in args:
        p = safe_path(a)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8"):
            os.utime(p, None)
    return ""

DISPATCH = {
    "pwd": cmd_pwd,
    "ls": cmd_ls,
    "cd": cmd_cd,
    "mkdir": cmd_mkdir,
    "rm": cmd_rm,
    "cat": cmd_cat,
    "echo": cmd_echo,
    "touch": cmd_touch,
}
