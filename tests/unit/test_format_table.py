# AC#2: format_table formats rows as word\tcount lines separated by \n and returns '' for empty input
import pytest

from wordfreq.cli import format_table


def test_format_table_rows_joined_by_newline_without_trailing_newline():
    rows = [("the", 3), ("cat", 1)]

    result = format_table(rows)

    assert result == "the\t3\ncat\t1"


def test_format_table_single_row_has_no_newline():
    rows = [("hello", 7)]

    result = format_table(rows)

    assert result == "hello\t7"


@pytest.mark.parametrize(
    "rows",
    [[], ()],
    ids=["empty_list", "empty_tuple"],
)
def test_format_table_empty_input_returns_empty_string(rows):
    result = format_table(rows)

    assert result == ""
