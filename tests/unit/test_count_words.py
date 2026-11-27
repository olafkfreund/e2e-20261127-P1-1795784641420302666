# AC#1: count_words extracts tokens, lowercases by default, preserves case with
# ignore_case=False, filters by min_len, and sorts by (-count, word).
import pytest

from wordfreq.cli import count_words


def test_count_words_extracts_alnum_tokens_splits_on_punctuation_returns_expected_words():
    text = "Hello, world! It's 42 cats-dogs_x"

    result = count_words(text)

    assert result == [
        ("42", 1),
        ("cats", 1),
        ("dogs", 1),
        ("hello", 1),
        ("it", 1),
        ("s", 1),
        ("world", 1),
        ("x", 1),
    ]


def test_count_words_default_lowercases_tokens_returns_single_lowercase_entry():
    text = "Apple apple APPLE"

    result = count_words(text)

    assert result == [("apple", 3)]


def test_count_words_ignore_case_false_preserves_case_returns_distinct_entries():
    text = "Apple apple APPLE"

    result = count_words(text, ignore_case=False)

    assert result == [("APPLE", 1), ("Apple", 1), ("apple", 1)]


def test_count_words_ignore_case_false_counts_per_exact_spelling():
    text = "go Go go"

    result = count_words(text, ignore_case=False)

    assert result == [("go", 2), ("Go", 1)]


@pytest.mark.parametrize(
    "min_len,expected",
    [
        (1, [("a", 1), ("an", 1), ("cat", 1), ("the", 1)]),
        (2, [("an", 1), ("cat", 1), ("the", 1)]),
        (3, [("cat", 1), ("the", 1)]),
    ],
    ids=["min_len_1_keeps_all", "min_len_2_drops_single_char", "min_len_3_drops_short"],
)
def test_count_words_min_len_filters_short_tokens_returns_expected_words(min_len, expected):
    text = "a an the cat"

    result = count_words(text, min_len=min_len)

    assert result == expected


def test_count_words_sorts_by_descending_count_returns_most_frequent_first():
    text = "b a c a b a"

    result = count_words(text)

    assert result == [("a", 3), ("b", 2), ("c", 1)]


def test_count_words_breaks_count_ties_alphabetically_returns_word_ascending():
    text = "zeta alpha alpha zeta"

    result = count_words(text)

    assert result == [("alpha", 2), ("zeta", 2)]


def test_count_words_empty_text_returns_empty_list():
    result = count_words("")

    assert result == []
