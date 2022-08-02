"""
V2 SDK functionality to support Stream operations.

"""
from runeq import errors
from . import client


def get_stream(stream_id: str, **params):
    """
    Fetch stream data from the Stream API.

    Parameters
    ----------
    stream_id : str
        Unique string identifier for a stream.

    **params
        limit: Limits the number of points returned for the stream.
        format: 'csv' or 'json'. Defaults to csv.

    Returns
    -------
    Generator over stream data in the specified format, defaulting to csv.

    """
    if not client._stream_client:
        raise errors.InitializationError("Failed to initialize stream client.")

    url = f"{client._stream_client.config.stream_url}/v2/streams/{stream_id}"

    return client._stream_client.get_data(url, **params)


def get_availability(stream_id: str, **params):
    """
    Fetch stream data availability from the Stream API.

    Parameters
    ----------
    stream_id : str
        Unique string identifier for a stream.

    **params
        limit: Limits the number of points returned for the stream.
        format: 'csv' or 'json'. Defaults to csv.

    Returns
    -------
    Generator over stream availability data in the specified format,
    defaulting to csv.

    """
    if not client._stream_client:
        raise errors.InitializationError("Failed to initialize stream client.")

    stream_url = client._stream_client.config.stream_url
    url = f"{stream_url}/v2/streams/{stream_id}/availability"

    return client._stream_client.get_data(url, **params)
