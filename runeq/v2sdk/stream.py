"""
V2 SDK functionality to support Stream operations.

"""
from typing import Literal

from runeq import errors
from . import client


def get_stream(
    stream_id: str,
    limit: int = 100,
    format: Literal["csv", "json"] = "csv"
):
    """
    Fetch stream data from the Stream API.

    Parameters
    ----------
    stream_id : str
        Unique string identifier for a stream.

    limit: int
        Limits the number of points returned for the stream.
        Defaults to 100 points and maxes at 10000 points.

    format: str
        Format response as 'csv' or 'json'. Defaults to csv.

    Returns
    -------
    Generator over stream data in the specified format, defaulting to csv.

    With a 'csv' format, each iteration of the generator returns a string
    with column names and up to 'limit' rows of data. For example:

    "time,acceleration,measurement_duration_ns
    1648412619.2589417,-0.00386,20000000
    1648412620.2600197,-0.00816,20000000
    1648412621.2671237,-0.01420,20000000"

    With a 'json' format, each iteration of the generator returns a dict
    with data fields and cardinality up to 'limit' data points. For example:

    {
        "cardinality": 3,
        "data": {
            "time": [
                1648412619.2589417,
                1648412620.2600198,
                1648412621.2671237,
            ],
            "acceleration": [
                -0.00386,
                -0.00816,
                -0.0142,
            ],
            "measurement_duration_ns": [
                20000000,
                20000000,
                20000000,
            ]
        }
    }

    V2 API Documentation
    --------------------
    https://docs.runelabs.io/stream/v2/#tag/single-stream/paths/~1stream~1{stream_id}/get

    """
    if not client._stream_client:
        raise errors.InitializationError(
            'runeq must be initialized by calling'
            '`initialize` before this function can be used'
        )

    url = f"{client._stream_client.config.stream_url}/v2/streams/{stream_id}"

    params = {
        'limit': limit,
        'format': format,
    }

    return client._stream_client.get_data(url, **params)


def get_availability(
    stream_id: str,
    limit: int = 100,
    format: Literal["csv", "json"] = "csv"
):
    """
    Fetch stream data availability from the Stream API.

    Parameters
    ----------
    stream_id : str
        Unique string identifier for a stream.

    limit: int
        Limits the number of points returned for the stream.
        Defaults to 100 points and maxes at 10000 points.

    format: str
        Format response as 'csv' or 'json'. Defaults to csv.

    Returns
    -------
    Generator over stream availability data in the specified format,
    defaulting to csv.

    With a 'csv' format, each iteration of the generator returns a string
    with column names and up to 'limit' rows of data. For example:

    "time,availability
    1648412600,1
    1648412900,1
    1648413200,0"

    With a 'json' format, each iteration of the generator returns a dict
    with data fields and cardinality up to 'limit' data points. For example:

    {
        "approx_available_duration_s": 900,
        "cardinality": 5,
        "data": {
            "time": [
                1648412600,
                1648412900,
                1648413200,
            ],
            "availability": [
                1,
                1,
                0,
            ]
        }
    }

    V2 API Documentation
    --------------------
    https://docs.runelabs.io/stream/v2/#tag/single-stream/paths/~1stream~1{stream_id}~1availability/get

    """
    if not client._stream_client:
        raise errors.InitializationError(
            'runeq must be initialized by calling'
            '`initialize` before this function can be used'
        )

    stream_url = client._stream_client.config.stream_url
    url = f"{stream_url}/v2/streams/{stream_id}/availability"

    params = {
        'limit': limit,
        'format': format,
    }

    return client._stream_client.get_data(url, **params)
