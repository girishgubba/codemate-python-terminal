# app/api.py
from fastapi import FastAPI
from pydantic import BaseModel
from app.executor import Executor

app = FastAPI(title="Python Command Terminal API")
ex = Executor()

class RunRequest(BaseModel):
    cmd: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run")
def run(req: RunRequest):
    out = ex.run_once(req.cmd)
    return {"output": out}
