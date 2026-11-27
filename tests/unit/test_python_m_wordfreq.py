# Criterion (AC#3): main and python -m wordfreq read from sys.stdin by default
# when no path argument is given, print ranked TSV, and return 2 with non-empty
# stderr on missing files.
import io
import subprocess
import sys

import pytest

from wordfreq.__main__ import main


def _run_module(args, stdin_text=""):
    return subprocess.run(
        [sys.executable, "-m", "wordfreq", *args],
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_python_m_wordfreq_stdin_default_prints_ranked_tsv_exit_0():
    result = _run_module([], stdin_text="b a b\n")
    assert result.returncode == 0
    assert result.stdout == "b\t2\na\t1\n"


def test_python_m_wordfreq_stdin_dash_path_prints_ranked_tsv_exit_0():
    result = _run_module(["-"], stdin_text="b a b\n")
    assert result.returncode == 0
    assert result.stdout == "b\t2\na\t1\n"


def test_python_m_wordfreq_missing_file_exit_2_nonempty_stderr(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    result = _run_module([str(missing)])
    assert result.returncode == 2
    assert result.stderr != ""


def test_main_stdin_default_reads_sys_stdin_returns_0(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("b a b\n"))
    assert main([]) == 0
    assert capsys.readouterr().out == "b\t2\na\t1\n"
