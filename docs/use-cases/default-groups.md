# Specifying a Default Group

Using the `default_group` attribute in gitman.yml specifies which group of
dependencies to install if no inputs are provided to `gitman install`. If
if is set to a blank string, `default_group: ''`, then all sources are
installed.

When nested gitman projects are used default groups are installed if they
exist. In the case of the following project layout:

Project A's configuration file:

```yaml
location: dependencies

sources:
  - name: b
    type: git
    repo: https://project_b
    rev: master
```

Project B's configuration file:

```yaml
location: dependencies

sources:
  - name: c
    type: git
    repo: https://project_c
    rev: master
  - name: d
    type: git
    repo: https://project_d
    rev: master

groups:
  - name: group_c_d
    members:
      - c
      - d
  - name: group_d
    members:
      - d

default_group: group_d
```

When `gitman install` is invoked from project A then project B is installed.
As project B is installed the default group `group_d` will be installed, unless
`gitman install -n` or `gitman install --no-defaults` is specified which will result in all of project B's dependencies (both c and d) being installed.
