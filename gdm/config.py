"""Wrappers for the dependency configuration files."""

import os

import yorm

from .shell import ShellMixin, GitMixin


@yorm.map_attr(repo=yorm.standard.String)
@yorm.map_attr(dir=yorm.standard.String)
@yorm.map_attr(rev=yorm.standard.String)
@yorm.map_attr(link=yorm.standard.String)
class Source(yorm.extended.AttributeDictionary, ShellMixin, GitMixin):

    """A dictionary of `git` and `ln` arguments."""

    def __init__(self, repo, dir, rev='master', link=None):  # pylint: disable=W0622
        super().__init__()
        self.repo = repo
        self.dir = dir
        self.rev = rev
        self.link = link

    def get(self):
        if os.path.exists(self.dir):
            self._cd(self.dir)
            self._fetch(self.repo)
            self._clean()
            self._reset()
        else:
            self._clone(self.repo, self.dir)
            self._cd(self.dir)
        self._checkout(self.rev)


@yorm.map_attr(all=Source)
class Sources(yorm.container.List):

    """A list of source dependencies."""


@yorm.map_attr(location=yorm.standard.String)
@yorm.map_attr(sources=Sources)
@yorm.store_instances("{self.root}/{self.filename}")
class Config(ShellMixin):

    """A dictionary of dependency configuration options."""

    FILENAMES = ('gdm.yml', 'gdm.yaml', '.gdm.yml', 'gdm.yaml')

    def __init__(self, root, filename='gdm.yml', location='gdm_sources'):
        super().__init__()
        self.root = root
        self.filename = filename
        self.location = location
        self.sources = []

    def install_deps(self):

        path = os.path.join(self.root, self.location)

        if not self.indent:
            print()

        if not os.path.isdir(path):
            self._mkdir(path)
        self._cd(path)
        print()

        for source in self.sources:

            source.indent = self.indent + self.INDENT
            source.get()
            print()

            install_deps(root=os.getcwd(), indent=source.indent + self.INDENT)

            self._cd(path, visible=False)


def install_deps(root, indent=0):
    """Install the dependences listed in the project's configuration file."""

    for filename in os.listdir(root):
        if filename.lower() in Config.FILENAMES:

            config = Config(root, filename)

            config.indent = indent
            config.install_deps()

            break
