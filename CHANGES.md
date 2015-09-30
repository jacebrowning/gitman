Revision History
================

0.5 (unreleased)
----------------

- Added Git plugin support via: `git deps`
- Removed '--no-clean' option (now the default) on 'install' and 'update'.
- Added '--clean' option to delete ignored files on 'install' and 'update'.

0.4.1 (2015/09/24)
------------------

- Switched to cloning for initial working tree creation.

0.4 (2015/09/18)
----------------

- Replaced 'install' command with 'update'.
- Updated 'install' command to use locked dependency versions.
- Now sorting sources after a successful 'update'.
- Now requiring '--force' to 'uninstall' with uncommitted changes.
- Updated 'list' command to show full shell commands.

0.3.1 (2015/09/09)
------------------

- Ensures files are not needlessly reloaded with newer versions of YORM.

0.3 (2015/06/26)
----------------

- Added '--no-clean' option to disable removing untracked files.
- Added support for `rev-parse` dates as the dependency `rev`.

0.2.5 (2015/06/15)
------------------

- Added '--quiet' option to hide warnings.

0.2.4 (2015/05/19)
------------------

- Now hiding YORM logging bellow warnings.

0.2.3 (2015/05/17)
------------------

- Upgraded to YORM v0.4.

0.2.2 (2015/05/04)
------------------

- Specified YORM < v0.4.

0.2.1 (2015/03/12)
------------------

- Added automatic remote branch tracking in dependencies.
- Now requiring '--force' when there are untracked files.

0.2 (2015/03/10)
----------------

- Added 'list' command to display current URLs/SHAs.

0.1.4 (2014/02/27)
------------------

- Fixed an outdated index when checking for changes.

0.1.3 (2014/02/27)
------------------

- Fixed extra whitespace when logging shell output.

0.1.2 (2014/02/27)
------------------

- Added '--force' argument to:
    - overwrite uncommitted changes
    - create symbolic links in place of directories
- Added live shell command output with '-vv' argument.

0.1 (2014/02/24)
----------------

- Initial release.
