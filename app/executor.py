# app/executor.py
import shlex
from .commands import DISPATCH, cmd_cat, CommandContext, write_output
from .monitoring import MONITOR
from .errors import CommandError
from .utils import split_redirection
from .nl_mapper import map_nl_to_command

class Executor:
    def __init__(self):
        self.ctx = CommandContext()
        self.commands = {**DISPATCH, **MONITOR}

    def run_once(self, line: str) -> str:
        try:
            tokens = shlex.split(line)
        except Exception:
            return "error: parse error\n"
        if not tokens:
            return ""

        cmd = tokens[0]
        args = tokens[1:]

        core_tokens, redir = split_redirection(tokens)
        cmd = core_tokens[0]
        args = core_tokens[1:]

        if cmd == "help":
            return (
                "Built-in commands:\n"
                "  pwd, ls [path], cd <dir>, mkdir <dir>..., rm <path>..., \n"
                "  cat <file>..., echo <text> [> file | >> file], touch <file>...\n"
                "Monitoring:\n"
                "  cpu, mem, ps\n"
                "Utilities:\n"
                "  nl \"natural language instruction\"\n"
                "  help\n"
            )

        if cmd == "nl":
            if not args:
                return "error: usage: nl \"instruction\"\n"
            mapped = map_nl_to_command(" ".join(args))
            if not mapped:
                return "error: could not map instruction\n"
            # show mapping then execute
            mapped_out = f"# nl -> {mapped}\n"
            return mapped_out + self.run_once(mapped)

        handler = self.commands.get(cmd)
        if not handler:
            return f"error: unknown command: {cmd}\n"

        try:
            if handler is cmd_cat:
                out = handler(self.ctx, args, None)
                if redir:
                    _ = write_output(out, redir)
                    return ""
                return out
            out = handler(self.ctx, args, redir)
            return out
        except CommandError as e:
            return f"{e}\n"
        except Exception as e:
            return f"unexpected error: {e}\n"
