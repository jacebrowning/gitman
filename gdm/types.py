import yorm


@yorm.map_attr(clone=yorm.standard.String)
@yorm.map_attr(to=yorm.standard.String)
@yorm.map_attr(at=yorm.standard.String)
@yorm.map_attr(link=yorm.standard.String)
class Dependency(yorm.extended.AttributeDictionary):

    """A dictionary of `git` and `ln` arguments."""
            
    @property
    def path(self):
        return os.path.join(self.root, self.to)
        
    
    def update(self, root):
        
    def _clone(self):
        self._call('git', 'clone', self.clone, self.to)
        
    def _checkout(self):
        self._call('git', 'checkout', self.at)
        
    def _link(self):
        self._call('ln', '-sf', self.path, self.link)
        
        
        
    @staticmethod
    def _call(*args):
        pass
    

        


@yorm.map_attr(all=Dependency)
class DependencyList(yorm.container.List):

    """A list of dependencies."""


@yorm.map_attr(directory=yorm.standard.String)
@yorm.map_attr(repositories=DependencyList)
@yorm.store_instances("{self.root}/{self.filename}")
class Configuration:

    """A dictionary of dependency configuration options."""

    def __init__(self, root, filename='gdm.yml', location='gdm_modules'):
        super().__init__()
        self.root = root
        self.filename = filename
        self.location = location
        self.repositories = []
        
    def __iter__(self):
        
