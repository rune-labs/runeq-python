"""
Query data directly from the V2 Stream API.

"""
from datetime import datetime
import time
from typing import Iterable, Iterator, Optional, Union

from .client import StreamClient, global_stream_client


def get_stream_data(
    stream_id: str,
    start_time: Optional[Union[float, datetime.date]] = None,
    start_time_ns: Optional[int] = None,
    end_time: Optional[Union[float, datetime.date]] = None,
    end_time_ns: Optional[int] = None,
    format: Optional[str] = "csv",
    limit: Optional[int] = None,
    page_token: Optional[str] = None,
    timestamp: Optional[str] = "iso",
    timezone: Optional[int] = None,
    translate_enums: Optional[bool] = True,
    client: Optional[StreamClient] = None
) -> Iterator[Union[str, dict]]:
    """
    Fetch raw data for a stream.

    Args:
        stream_id: ID of the stream
        start_time: Start time for the query, provided as a unix timestamp
                (in seconds) or a datetime.date.
        start_time_ns: Start time for the query, provided as a unix timestamp
            (in nanoseconds).
        end_time: End time for the query, provided as a unix timestamp
            (in seconds) or a datetime.date.
        end_time_ns: End time for the query, provided as a unix timestamp
            (in nanoseconds).
        format: Either "csv" (default) or "json". Determines the content type
            of the API response.
        limit: Maximum number of timestamps to return, across *all pages*
            of the response. A limit of 0 (default) will fetch all
            available data.
        page_token: Token to fetch the subsequent page of results.
            The value is obtained from the "X-Rune-Next-Page-Token"
            response header field.
        timestamp: One of "unix", "unixns", or "iso", which determines
            how timestamps are formatted in the response
        timezone: Timezone offset, in seconds, used to calculate
            string-based timestamp formats such as datetime and iso.
            For example, PST (UTC-0800) is represented as -28800.
            If omitted, the timezone is UTC.
        translate_enums: If True, enum values are returned as their string
            representation. Otherwise, enums are returned as integer values.
        client: If specified, this client is used to fetch data from the
            API. Otherwise, the global
            :class:`~runeq.resources.client.StreamClient` is used.

    Returns:
        An iterator over paginated API responses. If format is "json", each
        response is a dict. If format is "csv", each response is a
        CSV-formatted string.

    """
    if start_time and start_time_ns:
        raise ValueError(
            "only start_time or start_time_ns can be defined, not both."
        )

    if end_time and end_time_ns:
        raise ValueError(
            "only end_time or end_time_ns can be defined, not both."
        )

    # Convert datetime.date times to float unix times in seconds
    if type(start_time) is datetime.date:
        start_time = time.mktime(start_time.timetuple())
    if type(end_time) is datetime.date:
        end_time = time.mktime(end_time.timetuple())

    client = client or global_stream_client()
    path = f"/v2/streams/{stream_id}"

    yield from client.get_data(
        path,
        start_time=start_time,
        start_time_ns=start_time_ns,
        end_time=end_time,
        end_time_ns=end_time_ns,
        format=format,
        limit=limit,
        page_token=page_token,
        timestamp=timestamp,
        timezone=timezone,
        translate_enums=translate_enums,
    )


def get_stream_availability(
    stream_ids: Union[str, Iterable[str]],
    start_time: Union[float, datetime.date],
    end_time: Union[float, datetime.date],
    resolution: int,
    batch_operation: Optional[str] = None,
    format: Optional[str] = 'csv',
    limit: Optional[int] = None,
    page_token: Optional[str] = None,
    timestamp: Optional[str] = 'iso',
    timezone: Optional[int] = None,
    client: Optional[StreamClient] = None
) -> Iterator[Union[str, dict]]:
    """
    Fetch the availability of 1 or multiple streams. When multiple stream
    IDs are specified, this fetches the availability of **all** or **any**
    of the streams (depending on the **batch_operation**).

    Args:
        stream_ids: 1 or multiple stream IDs. If multiple stream IDs are
            specified, **batch_operation** is also required.
        start_time: Start time for the query, provided as a unix timestamp
            (in seconds) or a datetime.date.
        end_time: End time for the query, provided as a unix timestamp
            (in seconds) or a datetime.date.
        resolution: Interval between returned timestamps, in seconds.
        batch_operation: Either "any" or "all", which determines
            what type of batch calculation will determine availability for
            multiple streams. Availability values will equal 1 when
            data is available for "all" or "any" of the requested streams in
            the given interval. This argument is required when multiple
            **stream_ids** are specified.
        format: Either "csv" (default) or "json". Determines the content type
            of the API response.
        limit: Maximum number of timestamps to return, across *all pages*
            of the response. A limit of 0 (default) will fetch all
            available data.
        page_token: Token to fetch the subsequent page of results.
            The value is obtained from the "X-Rune-Next-Page-Token"
            response header field.
        timestamp: One of "unix", "unixns", or "iso", which determines
            how timestamps are formatted in the response
        timezone: Timezone offset, in seconds, used to calculate
            string-based timestamp formats such as datetime and iso.
            For example, PST (UTC-0800) is represented as -28800.
            If omitted, the timezone is UTC.
        client: If specified, this client is used to fetch data from the
            API. Otherwise, the global
            :class:`~runeq.resources.client.StreamClient` is used.

    Returns:
        An iterator over paginated API responses. If format is "json", each
        response is a dict. If format is "csv", each response is a
        CSV-formatted string.

    Raises:
        ValueError: if batch_operation is not specified and querying for
            more than 1 stream_id

    """
    params = {
        'start_time': start_time,
        'end_time': end_time,
        'resolution': resolution,
        'batch_operation': batch_operation,
        'format': format,
        'limit': limit,
        'page_token': page_token,
        'timestamp': timestamp,
        'timezone': timezone,
    }

    if type(start_time) is datetime.date:
        params['start_time'] = time.mktime(start_time.timetuple())
    if type(end_time) is datetime.date:
        params['end_time'] = time.mktime(end_time.timetuple())

    client = client or global_stream_client()

    # If stream_ids is not a string, convert it to a list so that we can
    if type(stream_ids) is not str:
        stream_ids = list(stream_ids)

    if type(stream_ids) is str:
        path = f"/v2/streams/{stream_ids}/availability"
    elif len(stream_ids) == 1:
        path = f"/v2/streams/{stream_ids[0]}/availability"
    else:
        # If querying for batch availability, need batch_operation
        if not batch_operation:
            raise ValueError(
                "batch_operation must be specified for multiple stream IDs"
            )

        path = "/v2/batch/availability"
        params["stream_id"] = stream_ids

    yield from client.get_data(path, **params)
