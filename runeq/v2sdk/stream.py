"""
V2 SDK functionality to support Stream operations.

"""
from runeq import errors
from . import client


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
        raise errors.InitializationError("Failed to initialize stream client.")

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
        raise errors.InitializationError("Failed to initialize stream client.")

    stream_url = client._stream_client._config.stream_url
    url = f"{stream_url}/v2/streams/{stream_id}/availability"

    # TODO: Currently it seems that only JSON availability is supported, but
    # CSV availability will be incorporated very soon!
    # https://runelabs.atlassian.net/browse/DATA-247?atlOrigin=eyJpIjoiYjhjYmE1ODM1ZWE4NGYwYmE1ZWVlOGQ1ZWM3MjUyZTUiLCJwIjoiaiJ9
    return client._stream_client._get(url, **params)
