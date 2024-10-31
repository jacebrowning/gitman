# Git Setup

In order for `gitman` to interact with Git, it must be configured to store your credentials for private repository access.

To test, trying cloning one of your private repositories:

```sh
$ git clone https://github.com/<owner>/<repo>.git
```

If you see:

```sh
Username for 'https://github.com':
```

then credential storage is not set up correctly.

## Stored Credentials

To use the Keychain on macOS, run:

```sh
$ git config --global credential.helper osxkeychain
```

To use the Credential Manager on Windows run:

```sh
$ git config --global credential.helper wincred
```

If you're using two-factory authentication on GitHub, you'll need to [provide a personal access token](http://olivierlacan.com/posts/why-is-git-https-not-working-on-github/) instead of your password.

## SSH Keys

You can also set up SSH keys (for [GitHub](https://help.github.com/articles/generating-ssh-keys/)) and use a different URL:

```sh
$ git clone git@github.com:<owner>/<repo>.git
```

## OAuth Tokens

Finally, the repository URL itself can contain an OAuth token (for [GitHub](https://github.com/blog/1270-easier-builds-and-deployments-using-git-over-https-and-oauth)):

```sh
$ git clone https://<token>@github.com/<owner>/<repo>.git
```

The token can also be written to `.netrc` during builds, see the guide for [Travis CI](https://docs.travis-ci.com/user/private-dependencies/#API-Token).

## Symlinks on Windows

If you're using Windows, there are some additional prerequisites to ensure Gitman works seamlessly with symbolic links.

### Grant Permissions

For Gitman to link your dependencies to your project, your Windows user account needs permission to create symlinks. By default, this permission may not be granted. To enable it, you can:

* Assign your user account the **Create symbolic links** permission in the Local Group Policy Editor.
* Enable **Developer Mode** in the Windows Settings.
* Run the command-line interface as an **Administrator**.

### Configure Git

In Git for Windows, symlink support must be enabled. You can do this during the installation process (checkbox in the install wizard) or by configuring it manually with the following command:

```sh
$ git config --global core.symlinks true
```

Additionally, Git does not inherently distinguish between symlinks to files and directories. To handle symlinks properly in your repositories, specify the type of symlink in your `.gitattributes` file. By default, Git assumes a symlink points to a file, so only symlinks to directories need to be declared:

```
relative/path/to/your/symlink symlink=dir
```

This ensures your symlinks work correctly after re-cloning your repository.

In some setups, it might be impractical to check in your symlinks. If that's the case, you can exclude your symlinks by adding them to `.gitignore` or `.git/info/exclude`. The latter is preferable as it does not modify the repository's actual content. Automate this step by adding the following to the script section of your gitman.yml:

```sh
mkdir -p .git/info
touch .git/info/exclude
git ls-files -o --exclude-standard > /tmp/unstaged_files
cat /tmp/unstaged_files >> .git/info/exclude
rm /tmp/unstaged_files
```
