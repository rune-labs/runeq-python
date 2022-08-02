"""
V2 SDK Client to support graph and stream clients.

"""

import requests

from gql import Client as GQLClient
from gql.transport.requests import RequestsHTTPTransport

from runeq import Config, errors

# Rune GraphQL Client to query stream metadata.
_gql_client = None

# Rune Stream API Client to query stream data.
_stream_client = None


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

    # Default response size per data fetch
    DEFAULT_RESPONSE_SIZE = 100

    # Max response size per data fetch
    MAX_RESPONSE_SIZE = 10000

    # Pagination token to get the next page of results.
    HEADER_NEXT_PAGE = "X-Rune-Next-Page-Token"

    # Configuration details for the stream client.
    config: Config = None

    def __init__(self, config: Config):
        """
        Initialize the Stream API Client.

        """
        self.config = config

    def get_data(self, url: str, **params):
        """
        Fetch stream data from the specified url and params.

        """
        if params.get('limit'):
            params['limit'] = min(params['limit'], self.MAX_RESPONSE_SIZE)
        else:
            params['limit'] = self.DEFAULT_RESPONSE_SIZE

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
