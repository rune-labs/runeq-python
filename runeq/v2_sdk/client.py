import requests

from gql import Client as GQLClient
from gql.transport.requests import RequestsHTTPTransport

from runeq import Config, errors


NOT_INITIALIZED_ERROR = (
    "User not initialized. Call runeq.v2sdk.initialize() to get started."
)
"""
Error raised when a user has not initialized their API credentials with initialize().

"""

_gql_client = None
"""
Rune GraphQL Client to query stream metadata.

"""

_stream_client = None
"""
Rune Stream API Client to query stream data.

"""


def get_stream(stream_id, **params):
    """
    Fetch stream data from the Stream API.

    Args:
        stream_id: Unique string identifier for a stream.

        **params:
            limit: Limits the number of points returned for the stream.
            format: 'csv' or 'json'. Defaults to csv.
    """
    if not _stream_client:
        raise errors.RuneError(NOT_INITIALIZED_ERROR)

    url = f"{_stream_client._config.stream_url}/v2/streams/{stream_id}"
    return _stream_client._get(url, **params)


def get_availability(stream_id, **params):
    """
    Fetch stream data availability from the Stream API.

    Args:
        stream_id: Unique string identifier for a stream.

        **params:
            limit: Limits the number of points returned for the stream.
            format: 'csv' or 'json'. Defaults to csv.
    """
    if not _stream_client:
        raise errors.RuneError(NOT_INITIALIZED_ERROR)

    url = f"{_stream_client._config.stream_url}/v2/streams/{stream_id}/availability"

    # TODO: Currently it seems that only JSON availability is supported, but
    # CSV availability will be incorporated very soon!
    # https://runelabs.atlassian.net/browse/DATA-247?atlOrigin=eyJpIjoiYjhjYmE1ODM1ZWE4NGYwYmE1ZWVlOGQ1ZWM3MjUyZTUiLCJwIjoiaiJ9
    return _stream_client._get(url, **params)


class GraphClient:
    """
    Rune GraphQL Client to query stream metadata.

    """

    _gql_client: GQLClient
    """
    The GraphQL client.

    """

    def __init__(self, config: Config):
        """
        Initialize the Graph API Client.

        """
        self._config = config
        transport = RequestsHTTPTransport(
            retries=10,
            url=f"{config.graph_url}/graphql",
            use_json=True,
            headers={"Content-Type": "application/json", **config.auth_headers},
        )
        self._gql_client = GQLClient(
            transport=transport,
        )


class StreamClient:
    """
    V2 Rune Stream API Client to query stream data.

    """

    HEADER_NEXT_PAGE = "X-Rune-Next-Page-Token"
    """
    Pagination token to get the next page of results.

    """

    def __init__(self, config: Config):
        """
        Initialize the Stream API Client.

        """
        self._config = config

    def _get(self, url, **params):
        """
        Fetch stream data from the specified url and params.

        """
        while True:
            r = requests.get(url, headers=self._config.auth_headers, params=params)
            self._check_response(r)
            r.raise_for_status()

            if params.get("json"):
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
