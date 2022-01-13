# pylint: disable=redefined-outer-name,expression-not-assigned

import pytest

from gitman.models import Group


@pytest.fixture
def group():
    return Group("foo", ["bar", "qux"])


def test_str_contains_name(group, expect):
    expect(str(group)) == "['foo']"
