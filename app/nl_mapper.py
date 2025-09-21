# Very lightweight NL -> command heuristic mapper
# Example: nl "create folder test" -> mkdir test
import shlex

patterns = [
    # (keywords, template)
    (["create", "folder"], "mkdir {name}"),
    (["make", "folder"], "mkdir {name}"),
    (["new", "folder"], "mkdir {name}"),
    (["remove", "file"], "rm {name}"),
    (["remove", "folder"], "rm {name}"),
    (["delete"], "rm {name}"),
    (["show", "files"], "ls"),
    (["list", "files"], "ls"),
    (["where", "am", "i"], "pwd"),
    (["print", "working", "directory"], "pwd"),
    (["create", "file"], "touch {name}"),
    (["write", "to", "file"], "echo {content} > {name}"),
]

def map_nl_to_command(text: str) -> str | None:
    t = text.lower()
    tokens = t.split()
    def contains(words): return all(w in tokens for w in words)
    for words, tmpl in patterns:
        if contains(words):
            # naive name/content extraction
            parts = [p for p in tokens if p not in words]
            if "{name}" in tmpl:
                name = parts[-1] if parts else "newitem"
                return tmpl.format(name=name, content="content")
            return tmpl.format(name="newitem", content="content")
    # fallback: try to pass-through as is
    try:
        shlex.split(text)
        return text
    except Exception:
        return None
