# Using Sparse Checkouts

For some use-cases, especially when dealing with monorepos, it can be useful to limit the paths that are checked out
from the reference repository. It is important to note, that this influences only the shape of the project local
checkout. The reference repository, maintained by gitman as a cache, will still be a full clone of the original repo.

Using `sparse_paths` will use git's sparse checkout feature to just materialize the selected paths in the working tree.
The `sparse_paths_type` option selects between git's two sparse-checkout modes:

- `"cone"` (default): only directory paths are supported and git uses a faster hash-based algorithm.
  Note that **all files at the repository root are always included** in cone mode; only subdirectories can be filtered.
- `"no-cone"`: patterns are treated as gitignore-style regular expressions and passed unmodified to git.
  This enables file-level and glob patterns (e.g. `"*.c"`) that cone mode cannot match.

## Cone mode (default)

The following example configuration will clone the full font-awesome repo into the cache, but the project local
clone will only contain the `fonts` directory and it's children.

```yaml
- repo: "https://github.com/FortAwesome/Font-Awesome"
  name: fontawesome
  rev: master
  sparse_paths:
    - "fonts/*"
```

Since cone mode only accepts directories, the trailing `/*` is stripped automatically so that `fonts` is passed to
`git sparse-checkout set`.

## Non-cone mode

When you need to match individual files or use regular-expression patterns, set `sparse_paths_type: no-cone`.
Patterns are passed unmodified to git's sparse checkout. For example, to check out only a single root-level file
and a specific subdirectory:

```yaml
- repo: "https://github.com/example/repo"
  name: example
  rev: main
  sparse_paths_type: no-cone
  sparse_paths:
    - "/c"
    - "/a/"
```

See the [git sparse-checkout documentation][git-sparse] for the full pattern syntax available in non-cone mode.

[git-sparse]: https://git-scm.com/docs/git-sparse-checkout
