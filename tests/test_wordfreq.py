"""Unit and CLI tests for the wordfreq package."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from wordfreq.cli import count_words, format_table, main

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_count_words_basic_ranking() -> None:
    text = "Apple banana apple, cherry! Banana apple."
    assert count_words(text) == [("apple", 3), ("banana", 2), ("cherry", 1)]


def test_format_table_tsv() -> None:
    assert format_table([("apple", 3), ("banana", 2)]) == "apple\t3\nbanana\t2"


def test_format_table_empty_input_returns_empty_string() -> None:
    assert format_table([]) == ""


def test_count_words_breaks_ties_alphabetically() -> None:
    assert count_words("pear apple pear mango apple kiwi") == [
        ("apple", 2),
        ("pear", 2),
        ("kiwi", 1),
        ("mango", 1),
    ]


def test_count_words_tie_order_ignores_input_order() -> None:
    forward = count_words("zeta alpha mid")
    reverse = count_words("mid alpha zeta")
    assert forward == reverse == [("alpha", 1), ("mid", 1), ("zeta", 1)]


def test_count_words_top_is_applied_after_tie_breaking() -> None:
    assert count_words("pear apple pear mango apple kiwi", top=2) == [
        ("apple", 2),
        ("pear", 2),
    ]


def test_count_words_ignore_case_merges_variants() -> None:
    assert count_words("Apple APPLE apple") == [("apple", 3)]


def test_count_words_case_sensitive_keeps_variants_distinct() -> None:
    assert count_words("Apple apple APPLE apple", ignore_case=False) == [
        ("apple", 2),
        ("APPLE", 1),
        ("Apple", 1),
    ]


def test_count_words_min_len_filters_short_words() -> None:
    assert count_words("a an the an", min_len=2) == [("an", 2), ("the", 1)]


def test_count_words_rejects_min_len_below_one() -> None:
    with pytest.raises(ValueError, match=r"^min_len must be >= 1$"):
        count_words("text", min_len=0)


def test_count_words_rejects_negative_top() -> None:
    with pytest.raises(ValueError, match=r"^top must be >= 0$"):
        count_words("text", top=-1)


def test_cli_top_and_min_len(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("to be or not to be that is the question", encoding="utf-8")
    rc = main([str(sample), "--min-len", "3", "--top", "2"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.strip().splitlines() == ["not\t1", "question\t1"]


def test_cli_case_sensitive_flag(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "case.txt"
    sample.write_text("Apple apple APPLE apple", encoding="utf-8")

    assert main([str(sample)]) == 0
    assert capsys.readouterr().out == "apple\t4\n"

    assert main([str(sample), "--case-sensitive"]) == 0
    assert capsys.readouterr().out == "apple\t2\nAPPLE\t1\nApple\t1\n"


def test_cli_reads_stdin_by_default(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("beta alpha beta\n"))
    assert main([]) == 0
    assert capsys.readouterr().out == "beta\t2\nalpha\t1\n"


def test_cli_dash_reads_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("one two"))
    assert main(["-"]) == 0
    assert capsys.readouterr().out == "one\t1\ntwo\t1\n"


def test_cli_empty_tsv_output_prints_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("!!! ???"))
    assert main([]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_cli_tsv_output_ends_with_single_newline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "newline.txt"
    sample.write_text("beta alpha beta", encoding="utf-8")
    assert main([str(sample)]) == 0
    out = capsys.readouterr().out
    assert out.endswith("\n")
    assert not out.endswith("\n\n")


def test_cli_json_output_shape_and_trailing_newline(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("beta alpha beta"))
    assert main(["--json"]) == 0
    out = capsys.readouterr().out
    assert out.endswith("\n")
    assert not out.endswith("\n\n")
    assert json.loads(out) == [
        {"word": "beta", "count": 2},
        {"word": "alpha", "count": 1},
    ]


def test_cli_json_empty_input_emits_empty_list(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    assert main(["--json"]) == 0
    assert capsys.readouterr().out == "[]\n"


@pytest.mark.parametrize("argv", [["--min-len=0"], ["--top=-1"], ["--top=abc"]])
def test_cli_invalid_arguments_return_2(
    argv: list[str],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("alpha"))
    assert main(argv) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""


def test_cli_missing_file_returns_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "does-not-exist.txt"
    assert main([str(missing)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "wordfreq: error" in captured.err
    assert str(missing) in captured.err


def test_python_m_wordfreq_reads_stdin() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "wordfreq", "--top", "2"],
        input="beta alpha beta gamma gamma gamma",
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout == "gamma\t3\nbeta\t2\n"
    assert result.stderr == ""


def test_python_m_wordfreq_json_output() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "wordfreq", "--json"],
        input="beta alpha beta",
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.endswith("\n")
    assert not result.stdout.endswith("\n\n")
    assert json.loads(result.stdout) == [
        {"word": "beta", "count": 2},
        {"word": "alpha", "count": 1},
    ]


def test_python_m_wordfreq_missing_file_exits_2(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.txt"
    result = subprocess.run(
        [sys.executable, "-m", "wordfreq", str(missing)],
        input="",
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 2
    assert result.stdout == ""
    assert "wordfreq: error" in result.stderr
