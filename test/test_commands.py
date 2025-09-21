import os
from pathlib import Path
from app.commands import CommandContext, cmd_pwd, cmd_ls, cmd_cd, cmd_mkdir, cmd_rm, cmd_cat, cmd_echo, cmd_touch
from app.errors import CommandError

def test_basic_flow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ctx = CommandContext()

    assert cmd_pwd(ctx, [], None).strip() == str(tmp_path)
    cmd_mkdir(ctx, ["a"], None)
    cmd_touch(ctx, ["a/f.txt"], None)
    out = cmd_ls(ctx, ["a"], None)
    assert "f.txt" in out
    with open(tmp_path / "a" / "f.txt", "w") as f:
        f.write("hello")
    assert "hello" in cmd_cat(ctx, ["a/f.txt"], None)
    cmd_cd(ctx, ["a"], None)
    assert Path.cwd().name == "a"
    cmd_cd(ctx, [".."], None)
    cmd_rm(ctx, ["a"], None)
    assert not (tmp_path / "a").exists()
