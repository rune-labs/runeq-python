"""
V2 SDK Client to support graph and stream clients.

"""

import requests

from gql import Client as GQLClient
from gql.transport.requests import RequestsHTTPTransport

from runeq import Config, errors


_gql_client = None
"""
Rune GraphQL Client to query stream metadata.

"""

_stream_client = None
"""
Rune Stream API Client to query stream data.

"""


class GraphClient:
    """
    Rune GraphQL Client to query stream metadata.

    """

    config: Config = None
    """
    Configuration details for the graph client.

    """

    _gql_client: GQLClient
    """
    The GraphQL client.

    """

    def __init__(self, config: Config):
        """
        Initialize the Graph API Client.

        """
        self.config = config
        transport = RequestsHTTPTransport(
            retries=10,
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


class StreamClient:
    """
    V2 Rune Stream API Client to query stream data.

    """

    HEADER_NEXT_PAGE = "X-Rune-Next-Page-Token"
    """
    Pagination token to get the next page of results.

    """

    config: Config = None
    """
    Configuration details for the stream client.

    """

    def __init__(self, config: Config):
        """
        Initialize the Stream API Client.

        """
        self.config = config

    def get_data(self, url: str, **params):
        """
        Fetch stream data from the specified url and params.

        """
        while True:
            r = requests.get(
                url,
                headers=self.config.auth_headers,
                params=params
            )

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
