import yorm
from yorm.types import AttributeDictionary, List, String

from .. import exceptions


@yorm.attr(name=String)
@yorm.attr(members=List.of_type(String))
class Group(AttributeDictionary):
    """A group with sources."""

    def __init__(self, name, members):

        super().__init__()
        self.name = name
        self.members = members or []

        for key in ['name', 'members']:
            if not self[key]:
                msg = "'{}' required for {}".format(key, repr(self))
                raise exceptions.InvalidConfig(msg)

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
