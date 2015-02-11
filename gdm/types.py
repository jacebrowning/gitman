import os

import yorm


@yorm.map_attr(repo=yorm.standard.String)
@yorm.map_attr(dir=yorm.standard.String)
@yorm.map_attr(rev=yorm.standard.String)
@yorm.map_attr(link=yorm.standard.String)
class Dependency(yorm.extended.AttributeDictionary):

    """A dictionary of `git` and `ln` arguments."""

    def __init__(self, repo, dir, rev='master', link=None):
        super().__init__()
        self.repo = repo
        self.dir = dir
        self.rev = rev
        self.link = link

    def update(self, root):
        pass

    def _clone(self):
        self._call('git', 'clone', self.repo, self.dir)

    def _checkout(self):
        self._call('git', 'checkout', self.rev)

    def _link(self, root):
        path = os.path.join(root, self.dir)
        self._call('ln', '-sf', path, self.link)

    @staticmethod
    def _call(*args):
        pass


@yorm.map_attr(all=Dependency)
class DependencyList(yorm.container.List):

    """A list of dependencies."""


@yorm.map_attr(location=yorm.standard.String)
@yorm.map_attr(sources=DependencyList)
@yorm.store_instances("{self.root}/{self.filename}")
class Configuration:

    """A dictionary of dependency configuration options."""

    def __init__(self, root, filename='gdm.yml', location='gdm_modules'):
        super().__init__()
        self.root = root
        self.filename = filename
        self.location = location
        self.sources = []

    def __iter__(self):
        pass
