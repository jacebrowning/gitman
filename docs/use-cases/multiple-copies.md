# Using Multiple Copies

This feature can be used to create as many copies as you need from one repository. This can be helpful e.g. on Windows where you need administrator priviledges in order to create a symbolic link.

## The Syntax

Let's say we have a simple project structure:

```text
|- include
|- src
|- docs
```

with the following `gitman.yml`:

```yaml
location: .gitman

sources:
  - repo: <URL of my_dependency repository>
    name: my_dependency
    rev: v1.0.3
    copies:
      - source: include
        target: vendor/partial_repo
      - target: vendor/full_repo
```

This will result in the following copies:

- `<root>/.gitman/my_dependency/include` -> `<root>/vendor/partial_repo`
- `<root>/.gitman/my_dependency` -> `<root>/vendor/full_repo`

## Alternative Syntax

```yaml
location: vendor

sources:
  - repo: <URL of my_dependency repository>
      name: my_dependency
      rev: v1.0.3
      copies:
        - { source: src, target: partial_repo }
        - { target: full_repo }
```

