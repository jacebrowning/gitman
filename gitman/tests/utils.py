# pylint: disable=expression-not-assigned

from expecter import expect


def check_calls(mock_call, expected):
    """Confirm the expected list of calls matches the mock call."""
    __tracebackhide__ = True  # pylint: disable=unused-variable
    actual = [" ".join(args[0]) for args in mock_call.call_args_list]
    expect(expected) == actual
