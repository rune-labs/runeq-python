"""
Clients for Rune's GraphQL API and V2 Stream API.

"""
from functools import wraps
import time
from typing import Dict, Iterator, Union
import urllib.parse

from gql import Client as GQLClient
from gql import gql
from gql.transport.requests import RequestsHTTPTransport
import requests

from runeq.config import Config
from runeq import errors

# Error when a client is not initialized
INITIALIZATION_ERROR = errors.InitializationError(
    'runeq must be initialized by calling'
    '`initialize` before this function can be used'
)

# Rune GraphQL Client to query stream metadata.
_graph_client = None

# Rune Stream API Client to query stream data.
_stream_client = None


def _retry(exceptions, max_attempts=3, max_sleep_secs=0):
    """
    Returns an exponential retry decorator.

    """
    if isinstance(exceptions, type):
        exceptions = (exceptions,)
    else:
        exceptions = tuple(exceptions)

    def inner_func(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == max_attempts - 1:
                        raise

                wait_secs = 2 ** attempt
                if max_sleep_secs > 0:
                    wait_secs = min(wait_secs, max_sleep_secs)

                time.sleep(wait_secs)

        return wrapper

    return inner_func


class GraphClient:
    """
    Rune GraphQL Client to query stream metadata.

    """

    # Configuration details for the graph client.
    config: Config = None

    # The GraphQL client.
    _gql_client: GQLClient

    def __init__(self, config: Config):
        """
        Initialize the Graph API Client.

        """
        self.config = config
        transport = RequestsHTTPTransport(
            # NOTE: retries are managed by the requests.HTTPAdapter, which
            # doesn't retry failed connections
            retries=3,
            url=f"{config.graph_url}/graphql",
            use_json=True,
            headers={
                "Content-Type": "application/json",
                **config.auth_headers
            },
        )
        self._gql_client = GQLClient(
            transport=transport,
        )

    @_retry(requests.exceptions.ConnectionError)
    def execute(self, statement: str, **variables) -> Dict:
        """
        Execute a GraphQL query against the API.

        """
        return self._gql_client.execute(
            gql(statement),
            variable_values=variables
        )


class StreamClient:
    """
    Client to query the V2 Stream API.

    """

    # Pagination token to get the next page of results.
    HEADER_NEXT_PAGE = "X-Rune-Next-Page-Token"

    # Configuration details for the stream client.
    config: Config = None

    def __init__(self, config: Config):
        """
        Initialize the Stream API Client.

        """
        self.config = config

    def get_data(self, path: str, **params) -> Iterator[Union[str, dict]]:
        """
        Makes request(s) to an endpoint of the V2 Stream API. Iterates over
        responses, following pagination headers until all data has been
        fetched.

        Args:
            path: Path for an endpoint of the V2 Stream API.
            **params: Query parameters. If the format parameter is "json",
                responses are parsed as JSON. Otherwise, the response is
                returned as text.

        Returns:
            Iterator over the API responses. If the format parameter is "json",
            each value is a dictionary. Otherwise, each value is a
            CSV-formatted string (the default for the V2 API).

        Raises:
            errors.APIError

        """
        if not path.startswith("/v2"):
            raise ValueError("path must begin with /v2")

        url = urllib.parse.urljoin(self.config.stream_url, path)

        # V2 endpoints return CSV-formatted responses by default
        return_json = params.get("format") == "json"

        while True:
            r = requests.get(
                url,
                headers=self.config.auth_headers,
                params=params
            )

            self._check_response(r)
            r.raise_for_status()

            if return_json:
                yield r.json()
            else:
                yield r.text

            if self.HEADER_NEXT_PAGE not in r.headers:
                return

            params["page_token"] = r.headers[self.HEADER_NEXT_PAGE]

    def _check_response(self, r: requests.Response) -> None:
        """
        Raise an exception if the request was not successful.

        """
        if r.ok:
            return

        # When possible, the API returns details about what went wrong in
        # the json body of the response. Incorporate that detail into the error
        # raised.
        try:
            data = r.json()
        except Exception:
            r.raise_for_status()
            return

        if "error" in data:
            raise errors.APIError(r.status_code, data["error"])


def initialize(*args, **kwargs):
    """
    Initializes the library with specified configuration options. Sets global
    clients for requests to the GraphQL API and the V2 Stream API.

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
    config = Config(*args, **kwargs)

    global _graph_client, _stream_client
    _graph_client = GraphClient(config)
    _stream_client = StreamClient(config)


def global_graph_client() -> GraphClient:
    """
    Returns the globally configured GraphQL client. Use
    :class:`~runeq.resources.client.initialize` to configure the client.

    Raises:
        errors.InitializationError: if the library was not initialized.

    """
    if not _graph_client:
        raise INITIALIZATION_ERROR

    return _graph_client


def global_stream_client() -> StreamClient:
    """
    Returns the globally configured Stream API client. Use
    :class:`~runeq.resources.client.initialize` to configure the client.

    Raises:
        errors.InitializationError: if the library was not initialized.


    """
    if not _stream_client:
        raise INITIALIZATION_ERROR

    return _stream_client
