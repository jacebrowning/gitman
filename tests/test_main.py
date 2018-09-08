# pylint: disable=unused-variable,expression-not-assigned

import subprocess
import sys

from expecter import expect


def describe_main():

    def it_displays_version():
        code = subprocess.call([sys.executable, "-m", "gitman", "--version"])
        expect(code) == 0
