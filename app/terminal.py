import shlex
import sys
from typing import List
from rich.console import Console
from .commands import DISPATCH, cmd_cat, CommandContext, write_output
from .monitoring import MONITOR
from .nl_mapper import map_nl_to_command
from .errors import CommandError
from .utils import split_redirection

# Optional import: prompt_toolkit only if console available
def _has_console() -> bool:
    try:
        # On Windows, real console has a valid fileno and isatty
        return sys.stdout.isatty() and sys.stdin.isatty()
    except Exception:
        return False

class Terminal:
    def __init__(self):
        self.ctx = CommandContext()
        self.console = Console()
        self.commands = {**DISPATCH, **MONITOR}
        self.use_ptk = False
        self.session = None
        if _has_console():
            try:
                from prompt_toolkit import PromptSession
                from prompt_toolkit.history import FileHistory
                from .completer import TerminalCompleter
                self.session = PromptSession(
                    message=self._prompt,
                    history=FileHistory(".terminal_history"),
                    completer=TerminalCompleter(),
                )
                self.use_ptk = True
            except Exception:
                self.use_ptk = False

    def _prompt(self):
        from pathlib import Path
        return f"[cmd] {Path.cwd()} $ "

    def _print(self, text: str):
        if text:
            self.console.print(text, end="")

    def _help(self):
        lines = [
            "Built-in commands:",
            "  pwd, ls [path], cd <dir>, mkdir <dir>..., rm <path>...,",
            "  cat <file>..., echo <text> [> file | >> file], touch <file>...",
            "Monitoring:",
            "  cpu, mem, ps",
            "Utilities:",
            "  nl \"natural language instruction\"",
            "  help, exit",
        ]
        self._print("\n".join(lines) + "\n")

    def _execute_line(self, line: str):
        try:
            tokens = shlex.split(line)
        except Exception:
            raise CommandError("parse error", "PARSE")
        if not tokens:
            return
        cmd = tokens[0]
        args = tokens[1:]

        if cmd == "help":
            self._help()
            return
        if cmd == "exit":
            raise SystemExit(0)

        core_tokens, redir = split_redirection(tokens)
        cmd = core_tokens[0]
        args = core_tokens[1:]

        if cmd == "nl":
            if not args:
                raise CommandError("usage: nl \"instruction\"", "BAD_ARGS")
            mapped = map_nl_to_command(" ".join(args))
            if not mapped:
                raise CommandError("could not map instruction", "NL_MAP")
            self._print(f"# nl -> {mapped}\n")
            self._execute_line(mapped)
            return

        handler = self.commands.get(cmd)
        if not handler:
            raise CommandError(f"unknown command: {cmd}", "UNKNOWN")

        if handler is cmd_cat:
            out = handler(self.ctx, args, None)
            if redir:
                _ = write_output(out, redir)
                return
            self._print(out)
            return

        out = handler(self.ctx, args, redir)
        self._print(out)

    def run(self):
        from pathlib import Path
        self.console.print("[bold cyan]Python Command Terminal[/bold cyan]")
        if self.use_ptk:
            while True:
                try:
                    line = self.session.prompt()
                    self._execute_line(line)
                except CommandError as e:
                    self._print(f"{e}\n")
                except (KeyboardInterrupt, EOFError):
                    self._print("\n")
                except SystemExit:
                    self._print("bye\n"); break
                except Exception as e:
                    self._print(f"unexpected error: {e}\n")
        else:
            # Basic input fallback for IDEs/CI without a Windows console
            while True:
                try:
                    line = input(f"[cmd] {Path.cwd()} $ ")
                    self._execute_line(line)
                except CommandError as e:
                    self._print(f"{e}\n")
                except (KeyboardInterrupt, EOFError):
                    self._print("\n")
                except SystemExit:
                    self._print("bye\n"); break
                except Exception as e:
                    self._print(f"unexpected error: {e}\n")
