# Git Setup

In order for `gitman` to interact with Git, it must be configured to store your credentials for private repository access.

To test, trying cloning one of your private repositories:

```shell
$ git clone https://github.com/<owner>/<repo>.git
```

If you see:

```shell
Username for 'https://github.com':
```

then credential storage is not set up correctly.

## Stored Credentials

To use the Keychain manager on OS X, run:

```
$ git config --global credential.helper osxkeychain
```

To use the Credential Manager on Windows run:

```
$ git config --global credential.helper wincred
```

If you're using two-factory authentication on GitHub, you'll need to [provide a personal access token](http://olivierlacan.com/posts/why-is-git-https-not-working-on-github/) instead of your password.

## SSH Keys

You can also set up SSH keys (for [GitHub](https://help.github.com/articles/generating-ssh-keys/)) and use a different URL:

```shell
$ git clone git://github.com/<owner>/<repo>.git
```

## OAuth Tokens

Finally, the repository URL itself can contain an OAuth token (for [GitHub](https://github.com/blog/1270-easier-builds-and-deployments-using-git-over-https-and-oauth)):

```shell
$ git clone https://<token>@github.com/<owner>/<repo>.git
```

The token can also be written to `.netrc` during builds, see the guide for [Travis CI](https://docs.travis-ci.com/user/private-dependencies/#API-Token).
