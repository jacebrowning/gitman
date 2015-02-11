import os
import subprocess

import yorm


@yorm.map_attr(repo=yorm.standard.String)
@yorm.map_attr(dir=yorm.standard.String)
@yorm.map_attr(rev=yorm.standard.String)
@yorm.map_attr(link=yorm.standard.String)
class Source(yorm.extended.AttributeDictionary):

    """A dictionary of `git` and `ln` arguments."""

    def __init__(self, repo, dir, rev='master', link=None):
        super().__init__()
        self.repo = repo
        self.dir = dir
        self.rev = rev
        self.link = link

    def get(self, root, location):
        path = os.path.join(root, location)

        if not os.path.isdir(path):
            self._mkdir(path)

        self._cd(path)

        if os.path.exists(self.dir):
            self._cd(self.dir)
            self._reset()
        else:
            self._clone()
            self._cd(self.dir)

        self._checkout()

    def _reset(self):
        # self._git('reset', '--hard')
        pass

    def _clone(self):
        self._git('clone', self.repo, self.dir)

    def _checkout(self):
        # self._git('checkout', self.rev)
        pass

    def _link(self, root):
        path = os.path.join(root, self.dir)
        self._call('ln', '-sf', path, self.link)

    @staticmethod
    def _mkdir(path):
        print("$ mkdir -p {}".format(path))
        os.makedirs(path)

    @staticmethod
    def _cd(path):
        print("$ cd {}".format(path))
        os.chdir(path)

    @classmethod
    def _git(cls, *args):
        args = ['git'] + list(args)
        cls._call(*args)

    @staticmethod
    def _call(*args):
        print("$ {}".format(' '.join(args)))
        subprocess.check_call(args)


@yorm.map_attr(all=Source)
class Sources(yorm.container.List):

    """A list of dependencies."""


@yorm.map_attr(location=yorm.standard.String)
@yorm.map_attr(sources=Sources)
@yorm.store_instances("{self.root}/{self.filename}")
class Dependencies:

    """A dictionary of dependency configuration options."""

    def __init__(self, root, filename='gdm.yml', location='gdm_modules'):
        super().__init__()
        self.root = root
        self.filename = filename
        self.location = location
        self.sources = []

    def update(self):
        for source in self.sources:
            source.get(self.root, self.location)
