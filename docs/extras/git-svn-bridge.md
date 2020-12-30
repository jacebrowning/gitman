# Using Git SVN

Many development projects use Subversion (SVN) to manage their source code. It’s the most popular open source VCS and has been around for nearly a decade. It’s also very similar in many ways to CVS, which was the big boy of the source-control world before that.

One of Git’s great features is a bidirectional bridge to Subversion called `git svn`. This tool allows you to use Git as a valid client to a Subversion server, so you can use all the local features of Git and then push to a Subversion server as if you were using Subversion locally.

> **Important**
>
> The GitMan `git svn` support does currently not track any changes in the imported SVN repository.
> The focus of this feature is to just import SVN dependencies
> in a readonly fashion.
> In this matter any changes in the imported svn repository
> will be overridden by an update/install process (like an implicit `--force` for each GitMan command).

To import SVN repositories it is required to specify the repo source parameter `type` to `git-svn` for the corresponding entries.

Example Configuration:

```yaml
location: imports

sources:
  - repo: http:http://my-svn-repo/trunk/MyDirectory
    name: MyDirectory
    type: git-svn
    rev: HEAD

  - repo: http:http://my-svn-repo/trunk/MySecondDirectory
    name: MySecondDirectory
    type: git-svn
    rev: 72846

  - repo: https://github.com/lz4/lz4
    name: lz4
    type: git
    rev: v1.8.1.2
```

By default, the `repo` source parameter `type` is `git`.

> **Note**
>
> The GitMan `git svn` support internally uses:
>
> ```
> $ git svn clone -r <rev> <repo>
> ```
>
> to resolve the individual SVN source dependency. In this matter, only the specified SVN revision will be fetched (shallow history).
