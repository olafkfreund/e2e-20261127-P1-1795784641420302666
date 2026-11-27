# Criterion (AC#3): `main` and `python -m wordfreq` read from `sys.stdin` by default
# when no `path` argument is given (or when `path` is "-"), honor `--case-sensitive`,
# `--top`, `--min-len`, and `--json`, terminate non-empty TSV output and `--json`
# output with a final "\n" (writing nothing for empty TSV output), and return 0 on
# success or 2 with non-empty stderr on invalid arguments or missing files.

import io
import json
import sys

import pytest

from wordfreq.cli import main


@pytest.fixture
def stdin_text(monkeypatch):
    def _set(text):
        monkeypatch.setattr(sys, "stdin", io.StringIO(text))

    return _set


def test_main_default_stdin_returns_zero(stdin_text):
    stdin_text("hello world\n")

    assert main([]) == 0


def test_main_default_stdin_reads_input_as_tsv(stdin_text, capsys):
    stdin_text("b a b\n")

    main([])

    assert capsys.readouterr().out == "b\t2\na\t1\n"


def test_main_dash_path_reads_stdin(stdin_text, capsys):
    stdin_text("b a b\n")

    main(["-"])

    assert capsys.readouterr().out == "b\t2\na\t1\n"


def test_main_default_lowercases_words(stdin_text, capsys):
    stdin_text("A a\n")

    main([])

    assert capsys.readouterr().out == "a\t2\n"


def test_main_case_sensitive_preserves_case(stdin_text, capsys):
    stdin_text("A a\n")

    main(["--case-sensitive"])

    assert capsys.readouterr().out == "A\t1\na\t1\n"


def test_main_top_limits_rows(stdin_text, capsys):
    stdin_text("a a b b c\n")

    main(["--top", "1"])

    assert capsys.readouterr().out == "a\t2\n"


def test_main_min_len_filters_short_words(stdin_text, capsys):
    stdin_text("a bb bb ccc\n")

    main(["--min-len", "2"])

    assert capsys.readouterr().out == "bb\t2\nccc\t1\n"


def test_main_tsv_output_ends_with_newline(stdin_text, capsys):
    stdin_text("x y\n")

    main([])

    assert capsys.readouterr().out.endswith("\n")


def test_main_json_output_ends_with_newline(stdin_text, capsys):
    stdin_text("x y\n")

    main(["--json"])

    assert capsys.readouterr().out.endswith("\n")


def test_main_json_output_is_parseable(stdin_text, capsys):
    stdin_text("x y x\n")

    main(["--json"])

    assert json.loads(capsys.readouterr().out) is not None


def test_main_empty_stdin_returns_zero(stdin_text):
    stdin_text("")

    assert main([]) == 0


def test_main_empty_stdin_writes_nothing_to_stdout(stdin_text, capsys):
    stdin_text("")

    main([])

    assert capsys.readouterr().out == ""
