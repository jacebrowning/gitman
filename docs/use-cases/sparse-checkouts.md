# Using sparse checkouts

For some use-cases, especially when dealing with monorepos, it can be useful to limit the paths that are checked out
from the reference repository. It is important to note, that this influences only the shape of the project local
checkout. The reference repository, maintained by gitman as a cache, will still be a full clone of the original repo.

Using `sparse_paths` will use git's sparse checkout feature to just materialize the selected paths in the working tree.
As this is a [git feature](https://git-scm.com/docs/git-read-tree#_sparse_checkout), all syntax options are
available and passed unmodified to `$GIT_DIR/info/sparse-checkout`.

The following example configuration will clone the full font-awesome repo into the cache, but the project local
clone will only contain the `fonts` directory and it's children.

```yaml
- name: fontawesome
  repo: https://github.com/FortAwesome/Font-Awesome
  sparse_paths:
  - fonts/*
  rev: master
```
