"""
Version 2 client for the Rune analysis API.

"""
from sys import stderr

from runeq import Config
from runeq.v2sdk import client


# Whether the warning about beta usage has been printed.
_beta_warned = False


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


def initialize(*args, **kwargs):
    """
    Initialize configuration options. Authenticate the user and globally
    initialize internal graph and stream clients.

    Parameters
    ----------
    *args
        Accepts at most 1; a filename. If provided, values will be
        loaded from the file. It is invalid to provide both a filename
        **and** keyword arguments.
    **kwargs
        Initialize client with keyword arguments.
        If using client keys, specify the client_key_id & client_access_key.
        If using access tokens, specify access_token_id & access_token_secret.

    Examples
    --------
    There are four valid ways to initialize the Rune V2 Client:

    >>> initialize()
    # Load from default file location (~/.rune/config)

    >>> initialize('./example_config.yaml')
    # Load from a specified YAML file

    >>> initialize(client_key_id='foo', client_access_key='bar')
    # Set values using keyword arguments

    >>> initialize(access_token_id='foo', access_token_secret='bar')
    # Set values using keyword arguments

    """
    beta_warning()

    config = Config(*args, **kwargs)
    client._gql_client = client.GraphClient(config)
    client._stream_client = client.StreamClient(config)
