# Linking Related Feature Branches


Another use case of `gdm` is to test experimental versions of related product sub-components. In the [web app + API example](branch-tracking.md), a new feature might require changes in both the API and web app.

## Custom Locked Sources

By manually modifying the `sources_locked` section, a particular version of the API can be checked out to help finish the complete feature in the web app:

```yaml
location: gdm_sources
sources:
- dir: api
  link: ''
  repo: https://github.com/example/api
  rev: develop
sources_locked:
- dir: api
  link: ''
  repo: https://github.com/example/api
  rev: feature/authenticate-with-github  # related feature branch in the API
```

If this modified `gdm.yml` is committed to a corresponding feature branch in the web app, others will be able to create a similar working tree to collaborate on the feature.

## Development Workflow

1. Run `$ gdm install` during continuous integration and locally to test the web app against the proposed API changes
2. Commit `gdm.yml` to share this feature branch with others
3. When the feature is complete, merge the API feature branch first
4. Run `$ gdm update` to reset `gdm.yml` back to a tracking a specific commit
