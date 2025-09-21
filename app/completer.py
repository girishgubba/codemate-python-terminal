import os
from pathlib import Path
from prompt_toolkit.completion import Completer, Completion

BASIC_COMMANDS = [
    "pwd","ls","cd","mkdir","rm","cat","echo","touch",
    "cpu","mem","ps","help","exit","nl"
]

class TerminalCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        parts = text.split()
        if not parts:
            for c in BASIC_COMMANDS:
                yield Completion(c, start_position=0)
            return
        if len(parts) == 1:
            for c in BASIC_COMMANDS:
                if c.startswith(parts[0]):
                    yield Completion(c, start_position=-len(parts[0]))
            return
        # file path completion
        prefix = parts[-1]
        base = Path(prefix).expanduser()
        dirpath = base.parent if base.parent != Path('.') else Path.cwd()
        if not dirpath.exists():
            return
        for name in os.listdir(dirpath):
            cand = (dirpath / name)
            disp = name + ("/" if cand.is_dir() else "")
            if str(cand).startswith(str(base)):
                yield Completion(str(cand), display=disp, start_position=-len(prefix))
