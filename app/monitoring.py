import psutil
from typing import List
from .errors import CommandError

def cmd_cpu(_, args: List[str], redir=None) -> str:
    if args:
        raise CommandError("cpu takes no arguments", "BAD_ARGS")
    perc = psutil.cpu_percent(interval=0.2)
    return f"CPU: {perc:.1f}%\n"

def cmd_mem(_, args: List[str], redir=None) -> str:
    if args:
        raise CommandError("usage: mem", "BAD_ARGS")
    v = psutil.virtual_memory()
    return f"MEM: used {v.used//(1024**2)}MB / {v.total//(1024**2)}MB ({v.percent:.1f}%)\n"

def cmd_ps(_, args: List[str], redir=None) -> str:
    if args:
        raise CommandError("usage: ps", "BAD_ARGS")
    lines = ["PID  NAME  CPU%  MEM%"]
    for p in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_percent"]):
        info = p.info
        lines.append(f"{info['pid']:>5}  {info.get('name','')[:20]:<20}  "
                     f"{(info.get('cpu_percent') or 0):>4.1f}  {(info.get('memory_percent') or 0):>4.1f}")
    return "\n".join(lines) + "\n"

MONITOR = {
    "cpu": cmd_cpu,
    "mem": cmd_mem,
    "ps": cmd_ps,
}
