import os
import subprocess

import yorm



class ShellMixIn:

    INDENT = 2
    indent = 0

    def _mkdir(self, path):
        self._display_in('mkdir', '-p', path)
        os.makedirs(path)

    def _cd(self, path, visible=True):
        if visible:
            self._display_in('cd', path)
        os.chdir(path)

    def _git(self, *args):
        self._call('git', *args, quiet=True)

    def _call(self, *args, quiet=False):
        self._display_in(*args)
        if quiet:
            args = list(args) + ['--quiet']
        subprocess.check_call(args)

    def _display_in(self, *args):
        print("{}$ {}".format(' ' * self.indent, ' '.join(args)))


@yorm.map_attr(repo=yorm.standard.String)
@yorm.map_attr(dir=yorm.standard.String)
@yorm.map_attr(rev=yorm.standard.String)
@yorm.map_attr(link=yorm.standard.String)
class Source(yorm.extended.AttributeDictionary, ShellMixIn):

    """A dictionary of `git` and `ln` arguments."""

    def __init__(self, repo, dir, rev='master', link=None):
        super().__init__()
        self.repo = repo
        self.dir = dir
        self.rev = rev
        self.link = link

    def get(self):

        if os.path.exists(self.dir):
            self._cd(self.dir)
            self._fetch()
            self._clean()
            self._reset()
        else:
            self._clone()
            self._cd(self.dir)

        self._checkout()

    def _fetch(self):
        self._git('fetch', '--tags', '--force', '--prune')

    def _clean(self):
        self._git('clean', '--force', '-d', '-x')

    def _reset(self):
        self._git('reset', '--hard')

    def _clone(self):
        self._git('clone', self.repo, self.dir)

    def _checkout(self):
        self._git('checkout', self.rev)

    def _link(self, root):
        path = os.path.join(root, self.dir)
        self._call('ln', '-sf', path, self.link)


@yorm.map_attr(all=Source)
class Sources(yorm.container.List):

    """A list of dependencies."""


@yorm.map_attr(location=yorm.standard.String)
@yorm.map_attr(sources=Sources)
@yorm.store_instances("{self.root}/{self.filename}")
class Dependencies(ShellMixIn):

    """A dictionary of dependency configuration options."""

    FILENAMES = ('gdm.yml', 'gdm.yaml', '.gdm.yml', 'gdm.yaml')

    def __init__(self, root, filename='gdm.yml', location='gdm_modules'):
        super().__init__()
        self.root = root
        self.filename = filename
        self.location = location
        self.sources = []

    @classmethod
    def update_all(cls, root=None, indent=0):

        if root is None:
            root = os.getcwd()

        for filename in os.listdir(root):
            if filename.lower() in cls.FILENAMES:

                dependencies = cls(root, filename)

                dependencies.indent = indent
                dependencies.update()

                break

    def update(self):

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

            self.__class__.update_all(indent=source.indent + self.INDENT)

            self._cd(path, visible=False)
