# Models

The internal models can be used as a high-level wrapper for creating and managing working trees of cloned source code repositories.

## `Source`

### Define Repository

Create a new `Source` instance from a repository URL:

```python
from gitman.models import Source

source = Source("https://github.com/jacebrowning/gitman-demo")
```

or customize the source name and revision to get:

```python
source = Source(
    repo="https://github.com/jacebrowning/gitman-demo",
    name="my-demo", # defaults to repository name
    rev="my-branch", # defaults to 'main'
)
```

### Update Files

Then, update files on disk:

```python
source.update_files()
```

or overwrite changes, if necessary:

```python
source.update_files(force=True)
```

## `Group`

*TBD*

## `Config`

*TBD*
