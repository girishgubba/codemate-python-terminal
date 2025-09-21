# app/web.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.executor import Executor

app = FastAPI(title="Python Command Terminal Web")
ex = Executor()

# Simple HTML UI
INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Python Command Terminal</title>
  <style>
    body { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; margin: 2rem; }
    #out { white-space: pre-wrap; background: #0b1020; color: #e6e6e6; padding: 1rem; min-height: 300px; border-radius: 8px; }
    #cmd { width: 80%; padding: 0.5rem; font-family: inherit; }
    button { padding: 0.5rem 1rem; }
  </style>
</head>
<body>
  <h2>Python Command Terminal (Hosted)</h2>
  <div id="out"></div>
  <div style="margin-top:1rem;">
    <input id="cmd" placeholder="Type a command, e.g., ls or pwd" />
    <button id="runBtn">Run</button>
    <button id="helpBtn">Help</button>
    <button id="clearBtn">Clear</button>
  </div>
  <script>
    const out = document.getElementById('out');
    const cmd = document.getElementById('cmd');
    const runBtn = document.getElementById('runBtn');
    const helpBtn = document.getElementById('helpBtn');
    const clearBtn = document.getElementById('clearBtn');

    async function runCommand(c) {
      if (!c) return;
      out.textContent += "\\n$ " + c + "\\n";
      const resp = await fetch('/run', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ cmd: c })
      });
      const data = await resp.json();
      out.textContent += (data.output || '');
      out.scrollTop = out.scrollHeight;
    }

    runBtn.onclick = () => runCommand(cmd.value);
    helpBtn.onclick = () => runCommand('help');
    clearBtn.onclick = () => { out.textContent = ''; };
    cmd.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') runCommand(cmd.value);
    });

    // Show initial help
    runCommand('help');
  </script>
</body>
</html>
"""

class RunRequest(BaseModel):
    cmd: str

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(INDEX_HTML)

@app.post("/run")
def run(req: RunRequest):
    out = ex.run_once(req.cmd)
    return {"output": out}

@app.get("/health")
def health():
    return {"status": "ok"}
