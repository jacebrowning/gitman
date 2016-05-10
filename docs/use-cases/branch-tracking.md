# Tracking Branches in Dependencies

One common use case of `gitman` is to track versions of related product sub-components such as a web app that depends on an API.

## Sample Configuration

A web app's `gitman.yml` might look something like:

```yaml
location: vendor
sources:
- name: api
  repo: https://github.com/example/api
  rev: develop
sources_locked:
- name: api
  repo: https://github.com/example/api
  rev: b2730855c9efaaa7448b25b82e5a4363785c83ed
```

with a working tree that results in something like:

```sh
package.json
node_modules

gitman.yml
vendor/api  # dependency @ b27308

app
tests
```

## Understanding Locked Sources

In the configuration file, the `sources_locked` section identifies that commit `b27308` of the API was last used to test this web app -- the last time `$ gitman update` was run.

The `sources` section identifies that the `develop` branch should be used when checking out a new version of the API.

## Development Workflow

1. Run `$ gitman install` during continuous integration to test the web app against a known working API
2. Run `$ gitman update` locally to determine if newer versions of the API will break the web app
3. When both components are working together, commit `gitman.yml`
