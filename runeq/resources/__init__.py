"""
Fetch data stored in the Rune Platform.

Metadata is fetched from Rune's GraphQL API (https://graph.runelabs.io/graphql),
using a :class:`~runeq.v2sdk.client.GraphClient`. Timeseries data is fetched
from the `V2 Stream API <https://docs.runelabs.io/stream/v2/index.html>`_, using
a :class:`~runeq.v2sdk.client.StreamClient`.

By default, globally-initialized clients are used for all API requests (see
:class:`~runeq.v2sdk.initialize`). Functions that make API requests also accept
an optional client, which can be used in lieu of the global initialization.

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
    Initialize the library with specified configuration options. Sets global
    clients for the Stream and GraphQL APIs.

    Note that these global clients are only used by the :class:`~runeq.v2sdk`
    module, NOT the :class:`~runeq.stream` module.

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
    There are several valid ways to use this function:

    >>> initialize()
    # Load the default config file (~/.rune/config)

    >>> initialize('./example_config.yaml')
    # Load values from a YAML file at a specified path

    >>> initialize(access_token_id='foo', access_token_secret='bar')
    >>> initialize(client_key_id='foo', client_access_key='bar')
    # Set configuration values using keyword arguments (instead
    # of a file). This can be used with any valid combination of
    # config options (e.g. with an access token OR a client key).

    """
    beta_warning()

    config = Config(*args, **kwargs)
    client._graph_client = client.GraphClient(config)
    client._stream_client = client.StreamClient(config)
