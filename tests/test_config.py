import os

from takeoff_bench.config import load_env


def test_load_env_sets_missing_values(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    path.write_text("A=one\nB='two words'\n# comment\nC=\n", encoding="utf-8")
    monkeypatch.delenv("A", raising=False)
    monkeypatch.delenv("B", raising=False)
    monkeypatch.delenv("C", raising=False)
    load_env(path)
    assert os.environ["A"] == "one"
    assert os.environ["B"] == "two words"
    assert os.environ["C"] == ""


def test_load_env_does_not_override(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    path.write_text("A=from-file\n", encoding="utf-8")
    monkeypatch.setenv("A", "from-shell")
    load_env(path)
    assert os.environ["A"] == "from-shell"
