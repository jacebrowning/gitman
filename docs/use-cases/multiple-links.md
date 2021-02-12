# Using multiple links

This feature can be used to create as many symbolic links as you need from one repository.

## The syntax

Let's say we have a simple project structure.

|- include
|- src
|- docs

```yaml
location: .gitman 

sources:
  - repo: <URL of my_dependency repository>
    name: my_dependency
    rev: v1.0.3
    links:
      - source: include
        target: vendor/partial_repo
      - target: vendor/full_repo
```

This will result in the following symbolic links:
- `<root>/vendor/partial_repo` -> `<root>/.gitman/my_dependency/include`
- `<root>/vendor/full_repo` -> `<root>/.gitman/my_dependency`

## Alternative syntax

```yaml
location: vendor 

sources:
  - repo: <URL of my_dependency repository>
      name: my_dependency
      rev: v1.0.3
      links:
        - { source: src, target: partial_repo }
        - { target: full_repo }
```

