# Criterion (AC#3): main returns 2 with non-empty stderr for invalid arguments
# (min-len 0, negative top, non-int) or missing files.

import pytest

from wordfreq.cli import main


@pytest.mark.parametrize(
    "argv",
    [
        pytest.param(["--min-len", "0"], id="min-len-zero"),
        pytest.param(["--top", "-1"], id="negative-top"),
        pytest.param(["--top", "abc"], id="non-int-top"),
    ],
)
def test_main_invalid_argument_returns_2(argv, capsys):
    exit_code = main(argv)

    assert exit_code == 2


@pytest.mark.parametrize(
    "argv",
    [
        pytest.param(["--min-len", "0"], id="min-len-zero"),
        pytest.param(["--top", "-1"], id="negative-top"),
        pytest.param(["--top", "abc"], id="non-int-top"),
    ],
)
def test_main_invalid_argument_writes_stderr(argv, capsys):
    main(argv)

    captured = capsys.readouterr()

    assert captured.err != ""


def test_main_missing_file_returns_2(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"

    exit_code = main([str(missing)])

    assert exit_code == 2


def test_main_missing_file_writes_stderr(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"

    main([str(missing)])

    captured = capsys.readouterr()

    assert captured.err != ""
