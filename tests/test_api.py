# pylint: disable=no-self-use,redefined-outer-name,unused-variable,unused-argument

import os
import shutil
from contextlib import suppress
import logging

import pytest

import gitman
from gitman.config import Config
from gitman.exceptions import InvalidRepository

from .utilities import strip


CONFIG = """
location: deps
sources:
- dir: gitman_1
  link: ''
  repo: https://github.com/jacebrowning/gitman-demo
  rev: example-branch
- dir: gitman_2
  link: ''
  repo: https://github.com/jacebrowning/gitman-demo
  rev: example-tag
- dir: gitman_3
  link: ''
  repo: https://github.com/jacebrowning/gitman-demo
  rev: 9bf18e16b956041f0267c21baad555a23237b52e
""".lstrip()

log = logging.getLogger(__name__)


@pytest.fixture
def config(root="/tmp/gitman-shared"):
    with suppress(FileNotFoundError):
        shutil.rmtree(root)
    with suppress(FileExistsError):
        os.makedirs(root)
    os.chdir(root)
    log.info("Temporary directory: %s", root)

    os.system("touch .git")
    config = Config(root=root)
    config.__mapper__.text = CONFIG  # pylint: disable=no-member

    log.debug("File listing: %s", os.listdir(root))

    return config


def describe_install():

    def it_should_create_missing_directories(config):
        assert not os.path.isdir(config.location)

        assert gitman.install('gitman_1', depth=1)

        assert ['gitman_1'] == os.listdir(config.location)

    def it_should_not_modify_config(config):
        assert gitman.install('gitman_1', depth=1)

        assert CONFIG == config.__mapper__.text

    def it_should_use_locked_sources_if_available(config):
        config.__mapper__.text = strip("""
        location: deps
        sources:
        - dir: gitman_1
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-branch
        sources_locked:
        - dir: gitman_2
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
        """)

        assert gitman.install(depth=1)

        assert ['gitman_2'] == os.listdir(config.location)

    def describe_links():

        @pytest.fixture
        def config_with_link(config):
            config.__mapper__.text = strip("""
            location: deps
            sources:
            - dir: gitman_1
              link: my_link
              repo: https://github.com/jacebrowning/gitman-demo
              rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
            """)

            return config

        def it_should_create(config_with_link):
            assert gitman.install(depth=1)

            assert 'my_link' in os.listdir()

        def it_should_not_overwrite(config_with_link):
            os.system("touch my_link")

            with pytest.raises(RuntimeError):
                gitman.install(depth=1)

        def it_should_overwrite_with_force(config_with_link):
            os.system("touch my_link")

            assert gitman.install(depth=1, force=True)


def describe_uninstall():

    def it_should_delete_dependencies_when_they_exist(config):
        gitman.install('gitman_1', depth=1)
        assert os.path.isdir(config.location)

        assert gitman.uninstall()

        assert not os.path.exists(config.location)

    def it_should_not_fail_when_no_dependnecies_exist(config):
        assert not os.path.isdir(config.location)

        assert gitman.uninstall()


def describe_update():

    def it_should_not_modify_config(config):
        gitman.update('gitman_1', depth=1)

        assert CONFIG == config.__mapper__.text

    def it_should_lock_previously_locked_dependnecies(config):
        config.__mapper__.text = strip("""
        location: deps
        sources:
        - dir: gitman_1
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-branch
        - dir: gitman_2
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-tag
        sources_locked:
        - dir: gitman_2
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: (old revision)
        """)

        gitman.update(depth=1)

        assert strip("""
        location: deps
        sources:
        - dir: gitman_1
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-branch
        - dir: gitman_2
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-tag
        sources_locked:
        - dir: gitman_2
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
        """) == config.__mapper__.text

    def it_should_not_lock_dependnecies_when_disabled(config):
        config.__mapper__.text = strip("""
        location: deps
        sources:
        - dir: gitman_1
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-branch
        - dir: gitman_2
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-tag
        sources_locked:
        - dir: gitman_2
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: (old revision)
        """)

        gitman.update(depth=1, lock=False)

        assert strip("""
        location: deps
        sources:
        - dir: gitman_1
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-branch
        - dir: gitman_2
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: example-tag
        sources_locked:
        - dir: gitman_2
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: (old revision)
        """) == config.__mapper__.text

    def it_should_lock_all_when_enabled(config):
        gitman.update(depth=1, lock=True)

        assert CONFIG + strip("""
        sources_locked:
        - dir: gitman_1
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: eb37743011a398b208dd9f9ef79a408c0fc10d48
        - dir: gitman_2
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
        - dir: gitman_3
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 9bf18e16b956041f0267c21baad555a23237b52e
        """) == config.__mapper__.text


def describe_lock():

    def it_should_record_all_versions_when_no_arguments(config):
        assert gitman.update(depth=1, lock=False)
        assert gitman.lock()

        assert CONFIG + strip("""
        sources_locked:
        - dir: gitman_1
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: eb37743011a398b208dd9f9ef79a408c0fc10d48
        - dir: gitman_2
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 7bd138fe7359561a8c2ff9d195dff238794ccc04
        - dir: gitman_3
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 9bf18e16b956041f0267c21baad555a23237b52e
        """) == config.__mapper__.text

    def it_should_record_specified_dependencies(config):
        assert gitman.update(depth=1, lock=False)
        assert gitman.lock('gitman_1', 'gitman_3')

        assert CONFIG + strip("""
        sources_locked:
        - dir: gitman_1
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: eb37743011a398b208dd9f9ef79a408c0fc10d48
        - dir: gitman_3
          link: ''
          repo: https://github.com/jacebrowning/gitman-demo
          rev: 9bf18e16b956041f0267c21baad555a23237b52e
        """) == config.__mapper__.text

    def it_should_fail_on_invalid_repositories(config):
        os.system("mkdir deps && touch deps/gitman_1")

        with pytest.raises(InvalidRepository):
            gitman.lock()

        assert "<unknown>" not in config.__mapper__.text
