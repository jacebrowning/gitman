import yorm


@yorm.map_attr(clone=yorm.standard.String)
@yorm.map_attr(to=yorm.standard.String)
@yorm.map_attr(at=yorm.standard.String)
@yorm.map_attr(link=yorm.standard.String)
class Dependency(yorm.extended.AttributeDictionary):

    """A dictionary of `git` and `ln` arguments."""


@yorm.map_attr(all=Dependency)
class DependencyList(yorm.container.List):

    """A list of dependencies."""


@yorm.map_attr(root=yorm.standard.String)
@yorm.map_attr(dependencies=DependencyList)
class Configuration(yorm.extended.AttributeDictionary):

    """A dictionary of dependency configuration options."""

    def __init__(self, root='gdm_modules'):
        super().__init__()
        self.root = root
