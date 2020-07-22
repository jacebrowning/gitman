from dataclasses import dataclass
from typing import List


@dataclass
class Group:
    """A group with sources."""

    name: str
    members: List[str]

    def __repr__(self):
        return "<group {}>".format(self)

    def __str__(self):
        pattern = "['{n}']"
        return pattern.format(n=self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __lt__(self, other):
        return self.name < other.name
