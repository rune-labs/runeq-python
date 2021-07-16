"""
Version 2 client for the Rune analysis API.

"""
from sys import stderr
from typing import Optional, Union

from runeq import Config
from .client import ClientSession


_beta_warned = False
"""
Whether the warning about beta usage has been printed.

"""


def beta_warning():
    """
    Issue a warning about using SDK code in beta testing.

    """
    global _beta_warned

    if not _beta_warned:
        print(
            "WARNING: You are accessing a part of the Rune SDK that is "
            "currently in Beta. Please be aware that Beta functionality is "
            "subject to change in future releases, and may break your code "
            "upon upgrade.",
            file=stderr,
        )
        _beta_warned = True


def session(
    config: Optional[Union[Config, str]] = None,
    caching=True,
    **kwarg,
):
    """
    Create a new Rune client session.

    This is the recommended way to initialize a new Rune session for reading
    patient data. Calling `runeq.session()` will initialize a client using
    your local configuration in `~/.rune/config`. This is the same as calling
    `runeq.session(runeq.Config())`.

    config
        (optional) If provided a `runeq.Config`, then the specified
        configuration is used.

    caching
        Set to `False` to disabling local caching of patient data. Disabling
        can impact performance for repeated queries over the same data.
        Default is `True`.

    **kwarg
        When `config` is omitted, you can also pass the configuration options
        directly as keyword parameters. This is shorthand for
        `runeq.session(runeq.Config(**kwarg))`.

    """
    beta_warning()

    if config is None:
        config = Config(**kwarg)
    elif isinstance(config, str):
        config = Config(config)

    return ClientSession(config=config, caching=caching)
