import os
from functools import wraps


def preserve_cwd(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        cwd = os.getcwd()
        result = function(*args, **kwargs)
        os.chdir(cwd)
        return result

    return wrapped
