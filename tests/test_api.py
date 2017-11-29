# pylint: disable=redefined-outer-name,unused-argument,unused-variable,singleton-comparison,expression-not-assigned,no-member

import os
import shutil
from contextlib import suppress
import logging

import pytest
from expecter import expect
from freezegun import freeze_time

import gitman
from gitman import shell
from gitman.models import Config
from gitman.exceptions import UncommittedChanges, InvalidRepository

from .utilities import strip


ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)))
TMP = os.path.join(ROOT, 'tmp')

CONFIG = """
location: deps
sources:
- name: gitman_1
  repo: https://github.com/jacebrowning/gitman-demo
  rev: example-branch
  link:
  scripts:
  -
- name: gitman_2
  repo: https://github.com/jacebrowning/gitman-demo
  rev: example-tag
  link:
  scripts:
  -
- name: gitman_3
  repo: https://github.com/jacebrowning/gitman-demo
  rev: 9bf18e16b956041f0267c21baad555a23237b52e
  link:
  scripts:
  -
""".lstrip()

log = logging.getLogger(__name__)


@pytest.yield_fixture
def config():
    log.info("Temporary directory: %s", TMP)

    with suppress(FileNotFoundError, PermissionError):
        shutil.rmtree(TMP)
    with suppress(FileExistsError):
        os.makedirs(TMP)
    os.chdir(TMP)

    os.system("touch .git")
    config = Config(root=TMP)
    config.__mapper__.text = CONFIG

    log.debug("File listing: %s", os.listdir(TMP))

    yield config

    os.chdir(ROOT)


def describe_init():

    def it_creates_a_new_config_file(tmpdir):
        tmpdir.chdir()

        expect(gitman.init()) == True

        expect(Config().__mapper__.text) == strip("""
        location: gitman_sources
        sources:
        - name: sample_dependency
          repo: https://github.com/githubtraining/hellogitworld
          rev: master
          link:
          scripts:
          -
        sources_locked:
        - name: sample_dependency
          repo: https://github.com/githubtraining/hellogitworld
          rev: ebbbf773431ba07510251bb03f9525c7bab2b13a
          link:
          scripts:
          -
        """)

    def it_does_not_modify_existing_config_file(config):
        expect(gitman.init()) == False

        expect(config.__mapper__.text) == CONFIG


def describe_install():

    def it_creates_missing_directories(config):
        shell.rm(config.location)

        expect(gitman.install('gitman_1', depth=1)) == True

        expect(os.listdir(config.location)) == ['gitman_1']

    def it_should_not_modify_config(config):
        expect(gitman.install('gitman_1', depth=1)) == True

        expect(config.__mapper__.text) == CONFIG

    def it_merges_sources(config):
        config.__mapper__.text = strip("""
        location: deps
        sources:
        - name: gitman_1
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-branch
          link:
          scripts:
          -
        sources_locked:
        - name: gitman_2
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-branch
          link:
          scripts:
          -
        - name: gitman_3
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
          link:
          scripts:
          -
        """)

        expect(gitman.install(depth=1)) == True

        expect(len(os.listdir(config.location))) == 3

    def it_can_handle_missing_locked_sources(config):
        config.__mapper__.text = strip("""
        location: deps
        sources:
        - name: gitman_1
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-branch
          link:
          scripts:
          -
        sources_locked:
        - name: gitman_2
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
          link:
          scripts:
          -
        """)

        expect(gitman.install('gitman_1', depth=1)) == True

        expect(os.listdir(config.location)) == ['gitman_1']

    def it_detects_invalid_repositories(config):
        shell.rm(os.path.join("deps", "gitman_1", ".git"))
        shell.mkdir(os.path.join("deps", "gitman_1", ".git"))

        try:
            with pytest.raises(InvalidRepository):
                expect(gitman.install('gitman_1', depth=1)) == False

        finally:
            shell.rm(os.path.join("deps", "gitman_1"))

    def describe_links():

        @pytest.fixture
        def config_with_link(config):
            config.__mapper__.text = strip("""
            location: deps
            sources:
            - name: gitman_1
              repo: https://github.com/jacebrowning/gitman-demo
              rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
              link: my_link
              scripts:
              -
            """)

            return config

        @pytest.mark.xfail(os.name == 'nt', reason="No symlinks on Windows")
        def it_should_create_links(config_with_link):
            expect(gitman.install(depth=1)) == True

            expect(os.listdir()).contains('my_link')

        @pytest.mark.xfail(os.name == 'nt', reason="No symlinks on Windows")
        def it_should_not_overwrite_files(config_with_link):
            os.system("touch my_link")

            with pytest.raises(RuntimeError):
                gitman.install(depth=1)

        @pytest.mark.xfail(os.name == 'nt', reason="No symlinks on Windows")
        def it_overwrites_files_with_force(config_with_link):
            os.system("touch my_link")

            expect(gitman.install(depth=1, force=True)) == True

    def describe_scripts():

        @pytest.fixture
        def config_with_scripts(config):
            config.__mapper__.text = strip("""
            location: deps
            sources:
            - name: gitman_1
              repo: https://github.com/jacebrowning/gitman-demo
              rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
              link:
              scripts:
              - make foobar
            """)

            return config

        def it_detects_failures_in_scripts(config_with_scripts):
            with pytest.raises(RuntimeError):
                expect(gitman.install())

        def script_failures_can_be_ignored(config_with_scripts):
            expect(gitman.install(force=True)) == True


def describe_uninstall():

    def it_deletes_dependencies_when_they_exist(config):
        gitman.install('gitman_1', depth=1)
        expect(os.path.isdir(config.location)) == True

        expect(gitman.uninstall()) == True

        expect(os.path.exists(config.location)) == False

    def it_should_not_fail_when_no_dependnecies_exist(config):
        expect(os.path.isdir(config.location)) == False

        expect(gitman.uninstall()) == True

    def it_deletes_the_log_file(config):
        gitman.install('gitman_1', depth=1)
        gitman.list()
        expect(os.path.exists(config.log_path)) == True

        gitman.uninstall()
        expect(os.path.exists(config.log_path)) == False


def describe_keep_location():

    def it_deletes_dependencies_when_they_exist(config):
        gitman.install('gitman_1', depth=1)
        expect(os.path.isdir(config.location)) == True

        expect(gitman.uninstall(keep_location=True)) == True

        expect(os.path.exists(os.path.join(config.location, 'gitman_1'))) == False

        expect(os.path.exists(config.location)) == True

        gitman.uninstall()

    def it_should_not_fail_when_no_dependencies_exist(config):
        expect(os.path.isdir(config.location)) == False

        expect(gitman.uninstall(keep_location=True)) == True

        gitman.uninstall()

    def it_deletes_the_log_file(config):
        gitman.install('gitman_1', depth=1)
        gitman.list()
        expect(os.path.exists(config.log_path)) == True

        gitman.uninstall(keep_location=True)
        expect(os.path.exists(config.log_path)) == False

        gitman.uninstall()


def describe_update():

    def it_should_not_modify_config(config):
        gitman.update('gitman_1', depth=1)

        expect(config.__mapper__.text) == CONFIG

    def it_locks_previously_locked_dependnecies(config):
        config.__mapper__.text = strip("""
        location: deps
        sources:
        - name: gitman_1
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-branch
          link:
          scripts:
          -
        - name: gitman_2
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-tag
          link:
          scripts:
          -
        sources_locked:
        - name: gitman_2
          repo: https://github.com/jacebrowning/gitman-demo
          rev: (old revision)
          link:
          scripts:
          -
        """)

        gitman.update(depth=1)

        expect(config.__mapper__.text) == strip("""
        location: deps
        sources:
        - name: gitman_1
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-branch
          link:
          scripts:
          -
        - name: gitman_2
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-tag
          link:
          scripts:
          -
        sources_locked:
        - name: gitman_2
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
          link:
          scripts:
          -
        """)

    def it_should_not_lock_dependnecies_when_disabled(config):
        config.__mapper__.text = strip("""
        location: deps
        sources:
        - name: gitman_1
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-branch
          link:
          scripts:
          -
        - name: gitman_2
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-tag
          link:
          scripts:
          -
        sources_locked:
        - name: gitman_2
          repo: https://github.com/jacebrowning/gitman-demo
          rev: (old revision)
          link:
          scripts:
          -
        """)

        gitman.update(depth=1, lock=False)

        expect(config.__mapper__.text) == strip("""
        location: deps
        sources:
        - name: gitman_1
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-branch
          link:
          scripts:
          -
        - name: gitman_2
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-tag
          link:
          scripts:
          -
        sources_locked:
        - name: gitman_2
          repo: https://github.com/jacebrowning/gitman-demo
          rev: (old revision)
          link:
          scripts:
          -
        """)

    def it_should_lock_all_dependencies_when_enabled(config):
        gitman.update(depth=1, lock=True)

        expect(config.__mapper__.text) == CONFIG + strip("""
        sources_locked:
        - name: gitman_1
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 1de84ca1d315f81b035cd7b0ecf87ca2025cdacd
          link:
          scripts:
          -
        - name: gitman_2
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
          link:
          scripts:
          -
        - name: gitman_3
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 9bf18e16b956041f0267c21baad555a23237b52e
          link:
          scripts:
          -
        """)


def describe_list():

    @freeze_time("2012-01-14 12:00:01")
    def it_updates_the_log(config):
        gitman.install()
        gitman.list()

        with open(config.log_path) as stream:
            contents = stream.read().replace(TMP, "tmp").replace('\\', '/')
        expect(contents) == strip("""
        2012-01-14 12:00:01
        tmp/deps/gitman_1: https://github.com/jacebrowning/gitman-demo @ 1de84ca1d315f81b035cd7b0ecf87ca2025cdacd
        tmp/deps/gitman_1/gitman_sources/gdm_3: https://github.com/jacebrowning/gdm-demo @ 050290bca3f14e13fd616604202b579853e7bfb0
        tmp/deps/gitman_1/gitman_sources/gdm_3/gitman_sources/gdm_3: https://github.com/jacebrowning/gdm-demo @ fb693447579235391a45ca170959b5583c5042d8
        tmp/deps/gitman_1/gitman_sources/gdm_3/gitman_sources/gdm_4: https://github.com/jacebrowning/gdm-demo @ 63ddfd82d308ddae72d31b61cb8942c898fa05b5
        tmp/deps/gitman_1/gitman_sources/gdm_4: https://github.com/jacebrowning/gdm-demo @ 63ddfd82d308ddae72d31b61cb8942c898fa05b5
        tmp/deps/gitman_2: https://github.com/jacebrowning/gitman-demo @ 7bd138fe7359561a8c2ff9d195dff238794ccc04
        tmp/deps/gitman_3: https://github.com/jacebrowning/gitman-demo @ 9bf18e16b956041f0267c21baad555a23237b52e
        """, end='\n\n')


def describe_lock():

    def it_records_all_versions_when_no_arguments(config):
        expect(gitman.update(depth=1, lock=False)) == True
        expect(gitman.lock()) == True

        expect(config.__mapper__.text) == CONFIG + strip("""
        sources_locked:
        - name: gitman_1
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 1de84ca1d315f81b035cd7b0ecf87ca2025cdacd
          link:
          scripts:
          -
        - name: gitman_2
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
          link:
          scripts:
          -
        - name: gitman_3
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 9bf18e16b956041f0267c21baad555a23237b52e
          link:
          scripts:
          -
        """) == config.__mapper__.text

    def it_records_specified_dependencies(config):
        expect(gitman.update(depth=1, lock=False)) == True
        expect(gitman.lock('gitman_1', 'gitman_3')) == True

        expect(config.__mapper__.text) == CONFIG + strip("""
        sources_locked:
        - name: gitman_1
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 1de84ca1d315f81b035cd7b0ecf87ca2025cdacd
          link:
          scripts:
          -
        - name: gitman_3
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 9bf18e16b956041f0267c21baad555a23237b52e
          link:
          scripts:
          -
        """) == config.__mapper__.text

    def it_should_fail_on_dirty_repositories(config):
        expect(gitman.update(depth=1, lock=False)) == True
        shell.rm(os.path.join("deps", "gitman_1", ".project"))

        try:
            with pytest.raises(UncommittedChanges):
                gitman.lock()

            expect(config.__mapper__.text).does_not_contain("<dirty>")

        finally:
            shell.rm(os.path.join("deps", "gitman_1"))

    def it_should_fail_on_missing_repositories(config):
        shell.mkdir("deps")
        shell.rm(os.path.join("deps", "gitman_1"))

        with pytest.raises(InvalidRepository):
            gitman.lock()

        expect(config.__mapper__.text).does_not_contain("<unknown>")

    def it_should_fail_on_invalid_repositories(config):
        shell.mkdir("deps")
        shell.rm(os.path.join("deps", "gitman_1", ".git"))
        shell.mkdir(os.path.join("deps", "gitman_1", ".git"))

        try:
            with pytest.raises(InvalidRepository):
                gitman.lock()

            expect(config.__mapper__.text).does_not_contain("<unknown>")

        finally:
            shell.rm(os.path.join("deps", "gitman_1"))
