# Replacing Git Submodules

While Git [submodules](http://git-scm.com/docs/git-submodule) are an obvious choice to include a particular version of another repository in yours, they end up being far less flexible when one needs to track branches or frequently switch between multiple versions of dependencies.

## An Existing Submodule

When managing a single dependency using submodules, there will be two items in your working tree with special meaning. The `.gitmodules` file, which contains submodule configuration, and semi-ignored directory containing the checked out dependency:

```sh
<root>/vendor/my_dependency  # submodule at: a943a702d06f34599aee1f8da8ef9f7296031d69
```

Using Git in the outer working tree will essentially ignore the contents of the nested working tree, but will still complain if there are changes locally or the submodule's origin has changes.

## Mimicking Submodules

To get the same behavior using `gitman`, first delete the `.gitmodules` file and create a new `.gitman.yml`:

```yaml
location: .gitman
sources:
- name: my_dependency
  repo: <URL of my_dependency's repository>
  rev: a943a702d06f34599aee1f8da8ef9f7296031d69
  link: vendor/my_depenendy
```

Add `.gitman` to your `.gitignore` file and overwrite the old submodule location by running:

```sh
gitman install --force
```

Now `<root>/vendor/my_dependency` will be a symbolic link that points to an ignored working tree of `my_dependency` at revision `a943a7`.

### Getting Dependencies

In other working trees, simply run `$ gitman install` to check out the source dependencies of your project.

### Modifying Dependencies

To include a different version of a dependency, modify the `rev` value in the configuration file.
