# Criterion (AC#1): _check_limits raises ValueError when min_len < 1 or top < 0.
# Expected messages: 'min_len must be >= 1' and 'top must be >= 0'.
import re

import pytest

from wordfreq.cli import _check_limits


@pytest.mark.parametrize(
    "min_len",
    [0, -1, -100],
    ids=["zero", "minus_one", "large_negative"],
)
def test_check_limits_min_len_below_one_raises_value_error(min_len):
    with pytest.raises(ValueError, match=re.escape("min_len must be >= 1")):
        _check_limits(min_len, 10)


@pytest.mark.parametrize(
    "top",
    [-1, -50],
    ids=["minus_one", "large_negative"],
)
def test_check_limits_top_below_zero_raises_value_error(top):
    with pytest.raises(ValueError, match=re.escape("top must be >= 0")):
        _check_limits(1, top)


def test_check_limits_min_len_one_and_top_zero_does_not_raise():
    _check_limits(1, 0)
