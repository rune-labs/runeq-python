"""
V2 SDK functionality to support Stream operations.

"""
from runeq import errors
from runeq.v2sdk import client


NOT_INITIALIZED_ERROR = (
    "User not initialized. Call runeq.v2sdk.initialize() to get started."
)
"""
Error raised when a user has not initialized their API credentials.

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
    if not client._stream_client:
        raise errors.RuneError(NOT_INITIALIZED_ERROR)

    url = f"{client._stream_client._config.stream_url}/v2/streams/{stream_id}"
    return client._stream_client._get(url, **params)


def get_availability(stream_id, **params):
    """
    Fetch stream data availability from the Stream API.

    Args:
        stream_id: Unique string identifier for a stream.

        **params:
            limit: Limits the number of points returned for the stream.
            format: 'csv' or 'json'. Defaults to csv.
    """
    if not client._stream_client:
        raise errors.RuneError(NOT_INITIALIZED_ERROR)

    stream_url = client._stream_client._config.stream_url
    url = f"{stream_url}/v2/streams/{stream_id}/availability"

    # TODO: Currently it seems that only JSON availability is supported, but
    # CSV availability will be incorporated very soon!
    # https://runelabs.atlassian.net/browse/DATA-247?atlOrigin=eyJpIjoiYjhjYmE1ODM1ZWE4NGYwYmE1ZWVlOGQ1ZWM3MjUyZTUiLCJwIjoiaiJ9
    return client._stream_client._get(url, **params)
