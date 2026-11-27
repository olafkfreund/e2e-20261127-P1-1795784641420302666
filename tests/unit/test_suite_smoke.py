# AC#4: pytest -q passes across tests/test_wordfreq.py
#
# Criterion (from rationale): the shipped tests/test_wordfreq.py suite must
# exercise main end-to-end and pass under `pytest -q`. The suite is run in a
# subprocess, and main is also driven end-to-end through its public interface
# with the expected values from AC#3.

import io
import subprocess
import sys
from pathlib import Path

import pytest

import wordfreq
from wordfreq.cli import main

# The imported package lives in the project checkout: <project>/wordfreq/__init__.py
PROJECT_ROOT = Path(wordfreq.__file__).resolve().parents[1]
SHIPPED_SUITE = PROJECT_ROOT / "tests" / "test_wordfreq.py"


@pytest.mark.slow
def test_shipped_suite_pytest_q_exit_code_zero():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(SHIPPED_SUITE)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0


def test_main_stdin_default_returns_zero(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("a b a\n"))
    assert main([]) == 0


def test_main_stdin_default_tsv_ranked_output(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("a b a\n"))
    main([])
    assert capsys.readouterr().out == "a\t2\nb\t1\n"


def test_main_tsv_output_ends_with_final_newline(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("a b a\n"))
    main([])
    assert capsys.readouterr().out.endswith("\n")


def test_main_empty_input_writes_nothing_to_stdout(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    main([])
    assert capsys.readouterr().out == ""


def test_main_dash_path_reads_stdin_returns_zero(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("x y x\n"))
    assert main(["-"]) == 0


def test_main_missing_file_returns_two(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"
    assert main([str(missing)]) == 2


def test_main_missing_file_writes_stderr(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"
    main([str(missing)])
    assert capsys.readouterr().err != ""


def test_main_min_len_zero_returns_two(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("a b\n"))
    assert main(["--min-len", "0"]) == 2


def test_main_negative_top_returns_two(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("a b\n"))
    assert main(["--top", "-1"]) == 2


def test_main_invalid_argument_writes_stderr(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("a b\n"))
    main(["--min-len", "0"])
    assert capsys.readouterr().err != ""


def test_main_json_output_ends_with_final_newline(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("a b a\n"))
    main(["--json"])
    assert capsys.readouterr().out.endswith("\n")


def test_main_case_sensitive_preserves_case_in_output(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("A a\n"))
    main(["--case-sensitive"])
    assert capsys.readouterr().out == "A\t1\na\t1\n"
