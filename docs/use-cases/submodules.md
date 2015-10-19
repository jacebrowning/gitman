# Replacing Git Submodules

While Git [submodules](http://git-scm.com/docs/git-submodule) are an obvious choice to include a particular version of another repository in yours, they end up being far less flexible when one needs to track branches or frequently switch between multiple versions of dependencies.

## An Existing Submodule

When managing a single dependency using submodules, there will be two items in your working tree with special meaning. The `.gitmodules` file, which contains submodule configuration, and semi-ignored directory containing the checked out dependency:

```sh
<root>/vendor/my_dependency  # submodule at: a5fe3d
```

Using Git in the outer working tree will essentially ignore the contents of the nested working tree, but will still complain if there are changes locally or the submodule's origin has changes.

## Mimicking Submodules

To get the same behavior using GDM, first delete the `.gitmodules` file and create a new `.gdm.yml`:

```yaml
location: .gdm
sources:
- repo: <URL of my_dependenc's repository>
  dir: my_dependency
  rev: a5fe3d
  link: vendor/my_depenendy
```

Add `.gdm` to your `.gitignore` file and overwrite the old submodule location by running:

```sh
gdm install --force
```

Now `<root>/vendor/my_dependency` will be a symbolic link that points to an ignored working tree of `my_dependency` at revision `a5fe3d`.

### Getting Dependencies

In other working trees, simply run `$ gdm install` to check out the source dependencies of your project.

### Modifying Dependencies

To include a different version of a dependency, modify the `rev` value in the GDM configuration file.
