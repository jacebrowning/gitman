"""Unit tests for the `gitman` package."""


def assert_calls(mock_call, expected):
    """Confirm the expected list of calls matches the mock call."""
    __tracebackhide__ = True  # pylint: disable=unused-variable
    actual = [' '.join((str(arg).replace('\\', '/') for arg in args[0]))
              for args in mock_call.call_args_list]
    assert expected == actual
