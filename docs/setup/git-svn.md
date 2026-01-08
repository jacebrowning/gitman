# Git SVN Setup

If you're planning to use Gitman to manage Subversion repositories, ensure `git svn` is configured correctly.

## Install missing SVN packages

```sh
sudo apt-get install git-svn
sudo apt-get install subversion libapache2-svn
```

## Credentials

In order for Gitman to interact with `git svn`, it must be configured to store your SVN credentials (cached) for private repository access. As a test, trying cloning one of your private repositories:

```sh
$ git svn clone -r <rev> <repo>
```

### Option 1: Enter manually credentials

If authentication realm is not already properly configured then Username and Password needs to be entered.

For example:

```sh
$ git svn clone -r HEAD http://my-svn-repo/trunk/MyDirectory
Initialized empty Git repository in /home/Dev/MyDirectory/.git/
Authentication realm: <http://my-svn-repo:80> my-svn-repo repository access
Username: JohnDoe
Password for 'John Doe'
```

This credentials should be cached afterwards.
For further information about caching credentials see [here](http://svnbook.red-bean.com/vi/1.8/svn.serverconfig.netmodel.html).

### Option 2: Manually store Credentials

1. Generate the MD5 hash of the realmstring of the repository provider.
2. Create a file under /home/<username>/.subversion/auth/svn.simple, where the filename is the md5 hash. This is how `git svn` will find the credentials when challenged.
3. The content of the file will have key value pairs as shown below:

```
K 8
passtype
V 6
simple
K 8
password
V <password character count>
<password>
K 15
svn:realmstring
V 50
<repo> <repo name>
K 8
username
V <username character count>
<username>
END
```

Now both `git svn` and `svn` should be able to check out from the repo without asking for credentials.
