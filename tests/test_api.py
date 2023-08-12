# pylint: disable=redefined-outer-name,unused-argument,unused-variable,singleton-comparison,expression-not-assigned,no-member

import inspect
import os
import shutil
from contextlib import suppress

import log
import pytest
from expecter import expect
from freezegun import freeze_time

import gitman
from gitman import shell
from gitman.exceptions import InvalidConfig, InvalidRepository, UncommittedChanges
from gitman.models import Config

from .utilities import strip

ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)))
TMP = os.path.join(ROOT, "tmp")

CONFIG = """
location: deps
sources:
  - repo: https://github.com/jacebrowning/gitman-demo
    name: gitman_1
    rev: example-branch
    type: git
    params:
    sparse_paths:
      -
    links:
      -
    scripts:
      -
  - repo: https://github.com/jacebrowning/gitman-demo
    name: gitman_2
    rev: example-tag
    type: git
    params:
    sparse_paths:
      -
    links:
      -
    scripts:
      -
  - repo: https://github.com/jacebrowning/gitman-demo
    name: gitman_3
    rev: 9bf18e16b956041f0267c21baad555a23237b52e
    type: git
    params:
    sparse_paths:
      -
    links:
      -
    scripts:
      -
sources_locked:
  -
groups:
  -
default_group: ''
""".lstrip()


@pytest.fixture
def config():
    log.info("Temporary directory: %s", TMP)

    with suppress(FileNotFoundError, PermissionError):
        shutil.rmtree(TMP)
    with suppress(FileExistsError):
        os.makedirs(TMP)
    os.chdir(TMP)

    os.system("touch .git")
    config = Config(root=TMP)
    config.datafile.text = CONFIG
    config.datafile.load()

    log.debug("File listing: %s", os.listdir(TMP))

    yield config

    os.chdir(ROOT)


def describe_init():
    def it_creates_a_new_config_file(tmpdir):
        tmpdir.chdir()

        expect(gitman.init()) == True

        expect(Config().datafile.text) == strip(
            """
        location: gitman_sources
        sources:
          - repo: https://github.com/githubtraining/hellogitworld
            name: sample_dependency
            rev: master
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
        sources_locked:
          - repo: https://github.com/githubtraining/hellogitworld
            name: sample_dependency
            rev: ebbbf773431ba07510251bb03f9525c7bab2b13a
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
        default_group: ''
        groups:
          -
        """
        )

    def it_does_not_modify_existing_config_file(config):
        expect(gitman.init()) == False

        expect(config.datafile.text) == CONFIG


def describe_install():
    def it_creates_missing_directories(config):
        shell.rm(config.location)

        expect(gitman.install("gitman_1", depth=1)) == True

        expect(os.listdir(config.location)) == ["gitman_1"]

    def it_should_not_modify_config(config):
        expect(gitman.install("gitman_1", depth=1)) == True

        expect(config.datafile.text) == CONFIG

    def it_merges_sources(config):
        config.datafile.text = strip(
            """
        location: deps
        sources:
          - repo: https://github.com/mrpossoms/gitman-demo-submodule
            name: gitman_sm_1
            type: git
            params: --recursive
            rev: main
            links:
              -
            scripts:
              -
        sources_locked:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            type: git
            rev: example-branch
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_3
            type: git
            rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
            links:
              -
            scripts:
              -
        """
        )
        config.datafile.load()

        expect(gitman.install(depth=1)) == True

        expect(len(os.listdir(config.location))) == 3

        # ensure the submodule cloned successfully by checking for a constituent file.
        expect(
            os.path.isfile(
                os.path.join(TMP, config.location, "gitman_sm_1/mrpossoms/README.md")
            )
        ) == True

    def it_can_handle_missing_locked_sources(config):
        config.datafile.text = strip(
            """
        location: deps
        sources:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_1
            type: git
            params:
            rev: example-branch
            links:
              -
            scripts:
              -
        sources_locked:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            type: git
            rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
            links:
              -
            scripts:
              -
        """
        )
        config.datafile.load()

        expect(gitman.install("gitman_1", depth=1)) == True

        expect(os.listdir(config.location)) == ["gitman_1"]

    def it_detects_invalid_repositories(config):
        shell.rm(os.path.join("deps", "gitman_1", ".git"))
        shell.mkdir(os.path.join("deps", "gitman_1", ".git"))

        try:
            with pytest.raises(InvalidRepository):
                expect(gitman.install("gitman_1", depth=1)) == False

        finally:
            shell.rm(os.path.join("deps", "gitman_1"))

    def describe_links():
        @pytest.fixture
        def config_with_link(config):
            config.datafile.text = strip(
                """
            location: deps
            sources:
              - name: gitman_1
                repo: https://github.com/jacebrowning/gitman-demo
                rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
                links:
                  - target: my_link
                scripts:
                  -
            """
            )
            config.datafile.load()

            return config

        def it_should_create_links(config_with_link):
            expect(gitman.install(depth=1)) == True

            expect(os.listdir()).contains("my_link")

        def it_should_not_overwrite_files(config_with_link):
            os.system("touch my_link")

            with pytest.raises(RuntimeError):
                gitman.install(depth=1)

        def it_should_not_overwrite_non_empty_directories(config_with_link):
            os.system("mkdir my_link")
            os.system("touch mylink/my_link")

            with pytest.raises(RuntimeError):
                gitman.install(depth=1)

        def it_overwrites_files_with_force(config_with_link):
            os.system("touch my_link")

            expect(gitman.install(depth=1, force=True)) == True

    def describe_multi_links():
        @pytest.fixture
        def config_with_links(config):
            config.datafile.text = strip(
                """
            location: deps
            sources:
              - name: gitman_1
                repo: https://github.com/jacebrowning/gitman-demo
                rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
                links:
                  - source: gitman_sources/gmd_3
                    target: gmd_3
                  - source: gitman_sources/gmd_4
                    target: gmd_4
                scripts:
                  -
            """
            )
            config.datafile.load()

            return config

        def it_should_create_links(config_with_links):
            expect(gitman.install(depth=1)) == True
            expect(os.listdir()).contains("gmd_3")
            expect(os.listdir()).contains("gmd_4")

        def it_should_not_overwrite_files(config_with_links):
            os.system("touch gmd_3")

            with pytest.raises(RuntimeError):
                gitman.install(depth=1)

        def it_should_not_overwrite_non_empty_directories(config_with_links):
            os.system("mkdir gmd_3")
            os.system("touch gmd_3/my_link")

            with pytest.raises(RuntimeError):
                gitman.install(depth=1)

        def it_overwrites_files_with_force(config_with_links):
            os.system("touch gmd_3")

            expect(gitman.install(depth=1, force=True)) == True

    def describe_scripts():
        @pytest.fixture
        def config_with_scripts(config):
            config.datafile.text = strip(
                """
            location: deps
            sources:
              - name: gitman_1
                type: git
                params:
                repo: https://github.com/jacebrowning/gitman-demo
                rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
                links:
                  -
                scripts:
                  - make foobar
            """
            )
            config.datafile.load()

            return config

        def it_detects_failures_in_scripts(config_with_scripts):
            with pytest.raises(RuntimeError):
                expect(gitman.install())

        def script_failures_can_be_ignored(config_with_scripts):
            expect(gitman.install(force=True)) == True

    def describe_sparse_paths():
        @pytest.fixture
        def config_with_scripts(config):
            config.datafile.text = strip(
                """
                    location: deps
                    sources:
                      - name: gitman_1
                        type: git
                        params:
                        repo: https://github.com/jacebrowning/gitman-demo
                        sparse_paths:
                          - src/*
                        rev: ddbe17ef173538d1fda29bd99a14bab3c5d86e78
                        links:
                          -
                        scripts:
                          -
                    """
            )
            config.datafile.load()

            return config

        def it_successfully_materializes_the_repo(config):
            expect(gitman.install(depth=1, force=True)) == True
            dir_listing = os.listdir(os.path.join(config.location, "gitman_1"))
            expect(dir_listing).contains("src")

        def it_contains_only_the_sparse_paths(config):
            expect(gitman.install(depth=1, force=True)) == True
            dir_listing = os.listdir(os.path.join(config.location, "gitman_1"))
            expect(dir_listing).contains("src")
            expect(len(dir_listing) == 1)

        def it_should_handle_updated_sparse_paths(config):
            config.datafile.text = strip(
                """
                    location: deps
                    sources:
                      - name: gitman_1
                        type: git
                        params:
                        repo: https://github.com/jacebrowning/gitman-demo
                        sparse_paths:
                          - gdm/*
                          - Makefile
                        rev: 63ddfd82d308ddae72d31b61cb8942c898fa05b5
                        links:
                          -
                        scripts:
                          -
                    """
            )
            config.datafile.load()

            expect(gitman.install(depth=1)) == True
            dir_listing = os.listdir(os.path.join(config.location, "gitman_1"))
            expect(dir_listing).contains("gdm")
            expect(dir_listing).contains("Makefile")
            expect(len(dir_listing) == 2)

            config.datafile.text = strip(
                """
                    location: deps
                    sources:
                      - name: gitman_1
                        type: git
                        params:
                        repo: https://github.com/jacebrowning/gitman-demo
                        sparse_paths:
                          - docs/*
                        rev: 63ddfd82d308ddae72d31b61cb8942c898fa05b5
                        links:
                          -
                        scripts:
                          -
                    """
            )
            config.datafile.load()
            expect(gitman.install(depth=1)) == True
            dir_listing = os.listdir(os.path.join(config.location, "gitman_1"))
            expect(dir_listing).contains("docs")
            expect(len(dir_listing) == 1)

        def it_should_handle_new_sparse_paths(config):
            config.datafile.text = strip(
                """
                    location: deps
                    sources:
                      - name: gitman_1
                        type: git
                        params:
                        repo: https://github.com/jacebrowning/gitman-demo
                        sparse_paths:
                          -
                        rev: 63ddfd82d308ddae72d31b61cb8942c898fa05b5
                        links:
                          -
                        scripts:
                          -
                    """
            )
            config.datafile.load()

            expect(gitman.install(depth=1)) == True
            dir_listing = os.listdir(os.path.join(config.location, "gitman_1"))
            expect(len(dir_listing) > 3)

            config.datafile.text = strip(
                """
                    location: deps
                    sources:
                      - name: gitman_1
                        type: git
                        params:
                        repo: https://github.com/jacebrowning/gitman-demo
                        sparse_paths:
                          - gdm/*
                          - docs/*
                          - Makefile
                        rev: 63ddfd82d308ddae72d31b61cb8942c898fa05b5
                        links:
                          -
                        scripts:
                          -
                    """
            )
            config.datafile.load()
            expect(gitman.install(depth=1)) == True
            dir_listing = os.listdir(os.path.join(config.location, "gitman_1"))
            expect(dir_listing).contains("docs")
            expect(dir_listing).contains("gdm")
            expect(dir_listing).contains("Makefile")
            expect(len(dir_listing) == 3)

        def it_should_handle_removed_sparse_paths(config):
            config.datafile.text = strip(
                """
                    location: deps
                    sources:
                      - name: gitman_1
                        type: git
                        params:
                        repo: https://github.com/jacebrowning/gitman-demo
                        sparse_paths:
                          - gdm/*
                          - docs/*
                          - Makefile
                        rev: 63ddfd82d308ddae72d31b61cb8942c898fa05b5
                        links:
                          -
                        scripts:
                          -
                    """
            )
            config.datafile.load()

            expect(gitman.install(depth=1, force=True)) == True
            dir_listing = os.listdir(os.path.join(config.location, "gitman_1"))
            expect(dir_listing).contains("docs")
            expect(dir_listing).contains("gdm")
            expect(dir_listing).contains("Makefile")
            expect(len(dir_listing) == 3)

            config.datafile.text = strip(
                """
                    location: deps
                    sources:
                      - name: gitman_1
                        type: git
                        params:
                        repo: https://github.com/jacebrowning/gitman-demo
                        sparse_paths:
                          -
                        rev: 63ddfd82d308ddae72d31b61cb8942c898fa05b5
                        links:
                          -
                        scripts:
                          -
                    """
            )
            config.datafile.load()
            expect(gitman.install(depth=1)) == True
            dir_listing = os.listdir(os.path.join(config.location, "gitman_1"))
            expect(len(dir_listing) > 3)

    def describe_mixed_names():
        @pytest.fixture
        def config_with_group(config):
            config.datafile.text = strip(
                """
                location: deps
                sources:
                  - name: gitman_1
                    type: git
                    params:
                    repo: https://github.com/jacebrowning/gitman-demo
                    sparse_paths:
                      -
                    rev: example-branch
                    links:
                      -
                    scripts:
                      -
                  - name: gitman_2
                    type: git
                    params:
                    repo: https://github.com/jacebrowning/gitman-demo
                    sparse_paths:
                      -
                    rev: example-tag
                    links:
                      -
                    scripts:
                      -
                groups:
                  - name: main_group
                    members:
                      - gitman_1
                  - name: super_group
                    members:
                    - gitman_1
                    - gitman_2
                """
            )
            config.datafile.load()

            return config

        def install_with_group_and_source_is_successful(config_with_group):
            expect(
                gitman.install("main_group", "gitman_2", depth=1, force=True)
            ) == True
            expect(
                os.path.exists(os.path.join(config_with_group.location, "gitman_1"))
            ) == True
            expect(
                os.path.exists(os.path.join(config_with_group.location, "gitman_2"))
            ) == True

        def groups_with_redundant_deps_install_successfully(config_with_group):
            expect(
                gitman.install("main_group", "super_group", depth=1, force=True)
            ) == True

        def group_and_redundant_source_install_successfully(config_with_group):
            expect(
                gitman.install("main_group", "gitman_1", depth=1, force=True)
            ) == True

    def describe_default_group():
        @pytest.fixture
        def config_with_default_group(config):
            config.datafile.text = strip(
                """
        location: deps
        sources:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_1
            type: git
            params:
            sparse_paths:
              -
            rev: example-branch
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            type: git
            params:
            sparse_paths:
              -
            rev: example-tag
            links:
              -
            scripts:
              -
        groups:
          - name: main
            members:
              - gitman_1
          - name: secondary
            members:
              - gitman_2
        default_group: 'main'
        """
            )
            config.datafile.load()

            return config

        @pytest.fixture
        def config_without_default_group(config):
            config.datafile.text = strip(
                """
        location: deps
        sources:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_1
            type: git
            params:
            sparse_paths:
              -
            rev: example-branch
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            type: git
            params:
            sparse_paths:
              -
            rev: example-tag
            links:
              -
            scripts:
              -
        groups:
          - name: main
            members:
              - gitman_1
          - name: secondary
            members:
              - gitman_2
        default_group: ''
        """
            )
            config.datafile.load()

            return config

        def it_installs_default_group(config_with_default_group):
            expect(gitman.install(depth=1, force=True)) == True
            expect(
                os.path.exists(
                    os.path.join(config_with_default_group.location, "gitman_1")
                )
            ) == True
            expect(
                os.path.exists(
                    os.path.join(config_with_default_group.location, "gitman_2")
                )
            ) == False

        def it_installs_all_sources_when_no_default_group(config_without_default_group):
            expect(gitman.install(depth=1, force=True)) == True
            expect(
                os.path.exists(
                    os.path.join(config_without_default_group.location, "gitman_1")
                )
            ) == True
            expect(
                os.path.exists(
                    os.path.join(config_without_default_group.location, "gitman_2")
                )
            ) == True

        def it_installs_all_sources_when_all_specified(config_with_default_group):
            expect(gitman.install(depth=1, force=True, skip_default_group=True)) == True
            expect(
                os.path.exists(
                    os.path.join(config_with_default_group.location, "gitman_1")
                )
            ) == True
            expect(
                os.path.exists(
                    os.path.join(config_with_default_group.location, "gitman_2")
                )
            ) == True


def describe_uninstall():
    def it_deletes_dependencies_when_they_exist(config):
        gitman.install("gitman_1", depth=1)
        expect(os.path.isdir(config.location)) == True

        expect(gitman.uninstall()) == True

        expect(os.path.exists(config.location)) == False

    def it_should_not_fail_when_no_dependencies_exist(config):
        expect(os.path.isdir(config.location)) == False

        expect(gitman.uninstall()) == True

    def it_deletes_the_log_file(config):
        gitman.install("gitman_1", depth=1)
        gitman.list()
        expect(os.path.exists(config.log_path)) == True

        gitman.uninstall()
        expect(os.path.exists(config.log_path)) == False

    def describe_keep_location():
        def it_deletes_dependencies_when_they_exist(config):
            gitman.install("gitman_1", depth=1)
            expect(os.path.isdir(config.location)) == True

            expect(gitman.uninstall(keep_location=True)) == True

            path = os.path.join(config.location, "gitman_1")
            expect(os.path.exists(path)) == False

            expect(os.path.exists(config.location)) == True

            gitman.uninstall()

        def it_should_not_fail_when_no_dependencies_exist(config):
            expect(os.path.isdir(config.location)) == False

            expect(gitman.uninstall(keep_location=True)) == True

            gitman.uninstall()

        def it_deletes_the_log_file(config):
            gitman.install("gitman_1", depth=1)
            gitman.list()
            expect(os.path.exists(config.log_path)) == True

            gitman.uninstall(keep_location=True)
            expect(os.path.exists(config.log_path)) == False

            gitman.uninstall()


def describe_update():
    def it_should_not_modify_config(config):
        gitman.update("gitman_1", depth=1)

        expect(config.datafile.text) == CONFIG

    def it_locks_previously_unlocked_dependencies(config):
        config.datafile.text = strip(
            """
        location: deps
        sources:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_1
            type: git
            params:
            sparse_paths:
              -
            rev: example-branch
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            type: git
            params:
            sparse_paths:
              -
            rev: example-tag
            links:
              -
            scripts:
              -
        sources_locked:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            type: git
            params:
            sparse_paths:
              -
            rev: (old revision)
            links:
              -
            scripts:
              -
        groups:
          -
        """
        )
        config.datafile.load()

        gitman.update(depth=1)

        config.datafile.load()
        expect(config.datafile.text) == strip(
            """
        location: deps
        sources:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_1
            rev: example-branch
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            rev: example-tag
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
        sources_locked:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
        groups:
          -
        default_group: ''
        """
        )

    def it_should_not_lock_dependencies_when_disabled(config):
        config.datafile.text = strip(
            """
        location: deps
        sources:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_1
            rev: example-branch
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            type: git
            params:
            sparse_paths:
              -
            rev: example-tag
            links:
              -
            scripts:
              -
        sources_locked:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            rev: (old revision)
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
        groups:
          -
        """
        )
        config.datafile.load()

        gitman.update(depth=1, lock=False)

        expect(config.datafile.text) == strip(
            """
        location: deps
        sources:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_1
            rev: example-branch
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            rev: example-tag
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
        sources_locked:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            rev: (old revision)
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
        groups:
          -
        default_group: ''
        """
        )

    def it_should_not_allow_source_and_group_name_conflicts(config):
        config.datafile.text = strip(
            """
        location: deps
        sources:
          - name: gitman_1
            type: git
            params:
            repo: https://github.com/jacebrowning/gitman-demo
            rev: example-branch
          - name: gitman_2
            type: git
            params:
            repo: https://github.com/jacebrowning/gitman-demo
            rev: example-branch
        groups:
          - name: gitman_1
            members:
              - gitman_1
              - gitman_2
            """
        )
        config.datafile.load()

        with pytest.raises(InvalidConfig):
            gitman.update(depth=1, lock=True)

    def it_locks_previously_locked_dependencies_by_group_name(config):
        config.datafile.text = strip(
            """
        location: deps
        sources:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_1
            type: git
            params:
            sparse_paths:
              -
            rev: example-branch
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            type: git
            params:
            sparse_paths:
              -
            rev: example-tag
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_3
            type: git
            params:
            sparse_paths:
              -
            rev: example-tag
            links:
              -
            scripts:
              -
        sources_locked:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_1
            type: git
            params:
            sparse_paths:
              -
            rev: (old revision)
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            type: git
            params:
            sparse_paths:
              -
            rev: (old revision)
            links:
              -
            scripts:
              -
        groups:
          - name: group_a
            members:
              - gitman_1
              - gitman_2
        """
        )
        config.datafile.load()

        gitman.update("group_a", depth=1)

        config.datafile.load()
        expect(config.datafile.text) == strip(
            """
        location: deps
        sources:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_1
            rev: example-branch
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            rev: example-tag
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_3
            rev: example-tag
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
        sources_locked:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_1
            rev: dfd561870c0eb6e814f8f6cd11f8f62f4ae88ea0
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
        groups:
          - name: group_a
            members:
              - gitman_1
              - gitman_2
        default_group: ''
        """
        )

    def it_should_not_lock_dependencies_changes_force_interactive_no(
        config, monkeypatch
    ):
        def git_changes(
            type, include_untracked=False, display_status=True, _show=False
        ):
            # always return True because changes won't be overwriten
            return True

        # patch the git.changes function to stimulate the
        # force-interactive question (without changes no question)
        monkeypatch.setattr("gitman.git.changes", git_changes)
        # patch standard input function to return "n" for each call
        # this is necessary to answer the force-interactive question
        # with no to skip the force process
        monkeypatch.setattr("builtins.input", lambda x: "n")

        config.datafile.text = strip(
            """
        location: deps
        sources:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            type: git
            params:
            sparse_paths:
              -
            rev: example-tag
            links:
              -
            scripts:
              -
        sources_locked:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            type: git
            params:
            sparse_paths:
              -
            rev: (old revision)
            links:
              -
            scripts:
              -
        groups:
          -
        """
        )
        config.datafile.load()

        gitman.update(depth=1, force_interactive=True)

        expect(config.datafile.text) == strip(
            """
        location: deps
        sources:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            rev: example-tag
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
        sources_locked:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            rev: (old revision)
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
        groups:
          -
        default_group: ''
        """
        )

    def it_locks_dependencies_changes_force_interactive_yes(config, monkeypatch):
        def git_changes(
            type, include_untracked=False, display_status=True, _show=False
        ):

            # get caller function name
            caller = inspect.stack()[1].function
            # if caller is update_files then we return True
            # to simulate local changes
            if caller == "update_files":
                return True

            # all other functions get False because after
            # the force process there are logically no changes anymore
            return False

        # patch the git.changes function to stimulate the
        # force-interactive question (without changes no question)
        monkeypatch.setattr("gitman.git.changes", git_changes)
        # patch standard input function to return "y" for each call
        # this is necessary to answer the force-interactive question
        # with yes to invoke the force process
        monkeypatch.setattr("builtins.input", lambda x: "y")

        config.datafile.text = strip(
            """
        location: deps
        sources:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            type: git
            params:
            sparse_paths:
              -
            rev: example-tag
            links:
              -
            scripts:
              -
        sources_locked:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            type: git
            params:
            sparse_paths:
              -
            rev: (old revision)
            links:
              -
            scripts:
              -
        groups:
          -
        """
        )
        config.datafile.load()

        gitman.update(depth=1, force_interactive=True)

        config.datafile.load()
        expect(config.datafile.text) == strip(
            """
        location: deps
        sources:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            rev: example-tag
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
        sources_locked:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
        groups:
          -
        default_group: ''
        """
        )

    def it_merges_sources(config):
        config.datafile.text = strip(
            """
        location: deps
        sources:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_1
            type: git
            params:
            rev: example-branch
            links:
              -
            scripts:
              -
        sources_locked:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            type: git
            rev: example-branch
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_3
            type: git
            rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
            links:
              -
            scripts:
              -
        """
        )
        config.datafile.load()

        expect(gitman.install(depth=1)) == True

        expect(len(os.listdir(config.location))) == 3


def describe_list():
    @freeze_time("2012-01-14 12:00:01")
    def it_updates_the_log(config):
        gitman.install()
        gitman.list()

        with open(config.log_path) as stream:
            contents = stream.read().replace(TMP, "tmp").replace("\\", "/")
        expect(contents) == strip(
            """
        2012-01-14 12:00:01
        tmp/deps/gitman_1: https://github.com/jacebrowning/gitman-demo @ dfd561870c0eb6e814f8f6cd11f8f62f4ae88ea0
        tmp/deps/gitman_1/gitman_sources/gdm_3: https://github.com/jacebrowning/gdm-demo @ 050290bca3f14e13fd616604202b579853e7bfb0
        tmp/deps/gitman_1/gitman_sources/gdm_3/gitman_sources/gdm_3: https://github.com/jacebrowning/gdm-demo @ fb693447579235391a45ca170959b5583c5042d8
        tmp/deps/gitman_1/gitman_sources/gdm_3/gitman_sources/gdm_4: https://github.com/jacebrowning/gdm-demo @ 63ddfd82d308ddae72d31b61cb8942c898fa05b5
        tmp/deps/gitman_1/gitman_sources/gdm_4: https://github.com/jacebrowning/gdm-demo @ 63ddfd82d308ddae72d31b61cb8942c898fa05b5
        tmp/deps/gitman_2: https://github.com/jacebrowning/gitman-demo @ 7bd138fe7359561a8c2ff9d195dff238794ccc04
        tmp/deps/gitman_3: https://github.com/jacebrowning/gitman-demo @ 9bf18e16b956041f0267c21baad555a23237b52e
        """,
            end="\n\n",
        )

    @freeze_time("2012-01-14 12:00:02")
    def it_handles_missing_dependencies(config):
        gitman.list()

        with open(config.log_path) as stream:
            contents = stream.read().replace(TMP, "tmp").replace("\\", "/")
        expect(contents) == strip(
            """
        2012-01-14 12:00:02
        tmp/deps: <missing> @ <unknown>
        tmp/deps: <missing> @ <unknown>
        tmp/deps: <missing> @ <unknown>
        """,
            end="\n\n",
        )


def describe_lock():
    def it_records_all_versions_when_no_arguments(config):
        expect(gitman.update(depth=1, lock=False)) == True
        expect(gitman.lock(depth=1)) == True

        config.datafile.load()
        expect(config.datafile.text).contains(
            strip(
                """
        sources_locked:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_1
            rev: dfd561870c0eb6e814f8f6cd11f8f62f4ae88ea0
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_2
            rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_3
            rev: 9bf18e16b956041f0267c21baad555a23237b52e
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
        """
            )
        )

    def it_records_specified_dependencies(config):
        expect(gitman.update(depth=1, lock=False)) == True
        expect(gitman.lock("gitman_1", "gitman_3", depth=1)) == True

        config.datafile.load()
        expect(config.datafile.text).contains(
            strip(
                """
        sources_locked:
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_1
            rev: dfd561870c0eb6e814f8f6cd11f8f62f4ae88ea0
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
          - repo: https://github.com/jacebrowning/gitman-demo
            name: gitman_3
            rev: 9bf18e16b956041f0267c21baad555a23237b52e
            type: git
            params:
            sparse_paths:
              -
            links:
              -
            scripts:
              -
        """
            )
        )

    def it_should_fail_on_dirty_repositories(config):
        expect(gitman.update(depth=1, lock=False)) == True
        shell.rm(os.path.join("deps", "gitman_1", ".project"))

        try:
            with pytest.raises(UncommittedChanges):
                gitman.lock()

            expect(config.datafile.text).does_not_contain("<dirty>")

        finally:
            shell.rm(os.path.join("deps", "gitman_1"))

    def it_should_fail_on_missing_repositories(config):
        shell.mkdir("deps")
        shell.rm(os.path.join("deps", "gitman_1"))

        with pytest.raises(InvalidRepository):
            gitman.lock()

        expect(config.datafile.text).does_not_contain("<unknown>")

    def it_should_fail_on_invalid_repositories(config):
        shell.mkdir("deps")
        shell.rm(os.path.join("deps", "gitman_1", ".git"))
        shell.mkdir(os.path.join("deps", "gitman_1", ".git"))

        try:
            with pytest.raises(InvalidRepository):
                gitman.lock()

            expect(config.datafile.text).does_not_contain("<unknown>")

        finally:
            shell.rm(os.path.join("deps", "gitman_1"))

    def it_should_lock_repository_to_user_specified_rev(config):
        expect(gitman.update(depth=1, lock=False)) == True

        expect(gitman.lock("gitman_1@master", depth=1)) == True
        config.datafile.load()
        expect(config.datafile.text).contains(
            "63ddfd82d308ddae72d31b61cb8942c898fa05b5"
        )

    def it_should_lock_repository_to_latest_rev_in_user_specified_reference(config):
        expect(gitman.update(depth=1, lock=False)) == True

        expect(
            gitman.lock("gitman_1@63ddfd82d308ddae72d31b61cb8942c898fa05b5", depth=1)
        ) == True

        config.datafile.load()
        expect(config.datafile.text).contains(
            "63ddfd82d308ddae72d31b61cb8942c898fa05b5"
        )

    def it_should_skip_lock_to_invalid_user_specified_reference(config):
        expect(gitman.update(depth=1, lock=False)) == True

        expect(gitman.lock("gitman_1@deadbeef_ref", depth=1)) == False
