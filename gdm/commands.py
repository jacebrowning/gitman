
from .types import Dependencies


def install(root):


    dependencies = Dependencies(root)
    dependencies.update()


    return True




