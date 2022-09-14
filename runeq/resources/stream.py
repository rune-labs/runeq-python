"""
V2 SDK functionality to support Stream operations.

"""
from datetime import datetime
import time
from typing import Iterator, List, Optional, Union

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
            (in nanoseconds).format: Optional enum "json" or "csv", which
            determines the content type of the response
        format: Either "csv" (default) or "json", which determines the content
            type of the API response.
        limit: Maximum number of timestamps to return, across *all pages*
            of the response. A limit of 0 (default) will fetch all
            available data.
        page_token: Token to fetch the subsequent page of results.
            The value is obtained from the 'X-Rune-Next-Page-Token'
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
            API. Otherwise, the global StreamClient is used.

    Returns:
        An iterator over paginated API responses. If format is "json", each
        response is a dict. If response is "csv", each response is a
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

    params = {
        'start_time': start_time,
        'start_time_ns': start_time_ns,
        'end_time': end_time,
        'end_time_ns': end_time_ns,
        'format': format,
        'limit': limit,
        'page_token': page_token,
        'timestamp': timestamp,
        'timezone': timezone,
        'translate_enums': translate_enums,
    }

    client = client or global_stream_client()
    path = f"/v2/streams/{stream_id}"
    yield from client.get_data(path, **params)


def get_stream_csv(
    stream_id: str,
    start_time: Optional[Union[float, datetime.date]] = None,
    start_time_ns: Optional[int] = None,
    end_time: Optional[Union[float, datetime.date]] = None,
    end_time_ns: Optional[int] = None,
    limit: Optional[int] = None,
    page_token: Optional[str] = None,
    timestamp: Optional[str] = "iso",
    timezone: Optional[int] = None,
    translate_enums: Optional[bool] = True,
    client: Optional[StreamClient] = None
) -> Iterator[str]:
    """
    Fetch raw data for a stream. Iterates over responses as CSV-formatted
    strings.

    Args:
        stream_id: ID of the stream
        start_time: Start time for the query, provided as a unix timestamp
                (in seconds) or a datetime.date.
        start_time_ns: Start time for the query, provided as a unix timestamp
            (in nanoseconds).
        end_time: End time for the query, provided as a unix timestamp
            (in seconds) or a datetime.date.
        end_time_ns: End time for the query, provided as a unix timestamp
            (in nanoseconds).format: Optional enum "json" or "csv", which
            determines the content type of the response
        limit: Maximum number of timestamps to return, across *all pages*
            of the response. A limit of 0 (default) will fetch all
            available data.
        page_token: Token to fetch the subsequent page of results.
            The value is obtained from the 'X-Rune-Next-Page-Token'
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
            API. Otherwise, the global StreamClient is used.

    Returns:
        An iterator over paginated API responses.

    """
    params = {
        'stream_id': stream_id,
        'start_time': start_time,
        'start_time_ns': start_time_ns,
        'end_time': end_time,
        'end_time_ns': end_time_ns,
        'format': 'csv',
        'limit': limit,
        'page_token': page_token,
        'timestamp': timestamp,
        'timezone': timezone,
        'translate_enums': translate_enums,
        'client': client,
    }
    return get_stream_data(**params)


def get_stream_json(
    stream_id: str,
    start_time: Optional[Union[float, datetime.date]] = None,
    start_time_ns: Optional[int] = None,
    end_time: Optional[Union[float, datetime.date]] = None,
    end_time_ns: Optional[int] = None,
    limit: Optional[int] = None,
    page_token: Optional[str] = None,
    timestamp: Optional[str] = "iso",
    timezone: Optional[int] = None,
    translate_enums: Optional[bool] = True,
    client: Optional[StreamClient] = None
) -> Iterator[dict]:
    """
    Fetch raw data for a stream. Iterates over the
    JSON-formatted results as dicts.

    Args:
        stream_id: ID of the stream
        start_time: Start time for the query, provided as a unix timestamp
                (in seconds) or a datetime.date.
        start_time_ns: Start time for the query, provided as a unix timestamp
            (in nanoseconds).
        end_time: End time for the query, provided as a unix timestamp
            (in seconds) or a datetime.date.
        end_time_ns: End time for the query, provided as a unix timestamp
            (in nanoseconds).format: Optional enum "json" or "csv", which
            determines the content type of the response
        limit: Maximum number of timestamps to return, across *all pages*
            of the response. A limit of 0 (default) will fetch all
            available data.
        page_token: Token to fetch the subsequent page of results.
            The value is obtained from the 'X-Rune-Next-Page-Token'
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
            API. Otherwise, the global StreamClient is used.

    Returns:
        An iterator over paginated API responses.

    """
    params = {
        'stream_id': stream_id,
        'start_time': start_time,
        'start_time_ns': start_time_ns,
        'end_time': end_time,
        'end_time_ns': end_time_ns,
        'format': 'json',
        'limit': limit,
        'page_token': page_token,
        'timestamp': timestamp,
        'timezone': timezone,
        'translate_enums': translate_enums,
        'client': client,
    }
    return get_stream_data(**params)


def get_stream_availability(
    stream_id: Union[str, List[str]],
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
    Fetch the availability of 1 or multiple streams.

    Args:
        stream_id: 1 or multiple stream IDs. If multiple stream IDs are
            specified, must also specify batch_operation.
        start_time: Start time for the query, provided as a unix timestamp
            (in seconds) or a datetime.date.
        end_time: End time for the query, provided as a unix timestamp
            (in seconds) or a datetime.date.
        resolution: Interval between returned timestamps, in seconds.
        batch_operation: Either "any" or "all", which determines
            what type of batch calculation will determine availability for
            multiple streams. Availability values will equal 1 when
            data is available for "all" or "any" of the requested streams in
            the given interval.
            This argument is required when multiple stream IDs are specified.
        format: Either "csv" (default) or "json", which determines the content
            type of the API response.
        limit: Maximum number of timestamps to return, across *all pages*
            of the response. A limit of 0 (default) will fetch all
            available data.
        page_token: Token to fetch the subsequent page of results.
            The value is obtained from the 'X-Rune-Next-Page-Token'
            response header field.
        timestamp: One of "unix", "unixns", or "iso", which determines
            how timestamps are formatted in the response
        timezone: Timezone offset, in seconds, used to calculate
            string-based timestamp formats such as datetime and iso.
            For example, PST (UTC-0800) is represented as -28800.
            If omitted, the timezone is UTC.
        client: If specified, this client is used to fetch data from the
            API. Otherwise, the global StreamClient is used.

    Returns:
        An iterator over paginated API responses. If format is "json", each
        response is a dict. If response is "csv", each response is a
        CSV-formatted string.

    Raises:
        ValueError: if batch_operation is not specified and querying for
            more than 1 stream_id

    """
    params = {
        'stream_id': stream_id,
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

    if type(stream_id) is list:
        # If querying for batch availability, need batch_operation
        if not batch_operation:
            raise ValueError(
                "batch_operation must be specified for multiple stream IDs"
            )
        path = "/v2/batch/availability"
    else:
        path = f"/v2/streams/{stream_id}/availability"
        del params['stream_id']

    yield from client.get_data(path, **params)


def get_stream_availability_csv(
    stream_id: Union[str, List[str]],
    start_time: Union[float, datetime.date],
    end_time: Union[float, datetime.date],
    resolution: int,
    batch_operation: Optional[str] = None,
    limit: Optional[int] = None,
    page_token: Optional[str] = None,
    timestamp: Optional[str] = 'iso',
    timezone: Optional[int] = None,
    client: Optional[StreamClient] = None
) -> Iterator[str]:
    """
    Fetch the availability of 1 or multiple streams. Iterates over the
    results as CSV-formatted strings.

    Args:
        Args:
        stream_id: 1 or multiple stream IDs. If multiple stream IDs are
            specified, must also specify batch_operation.
        start_time: Start time for the query, provided as a unix timestamp
            (in seconds) or a datetime.date.
        end_time: End time for the query, provided as a unix timestamp
            (in seconds) or a datetime.date.
        resolution: Interval between returned timestamps, in seconds.
        batch_operation: Either "any" or "all", which determines
            what type of batch calculation will determine availability for
            multiple streams. Availability values will equal 1 when
            data is available for "all" or "any" of the requested streams in
            the given interval.
            This argument is required when multiple stream IDs are specified.
        limit: Maximum number of timestamps to return, across *all pages*
            of the response. A limit of 0 (default) will fetch all
            available data.
        page_token: Token to fetch the subsequent page of results.
            The value is obtained from the 'X-Rune-Next-Page-Token'
            response header field.
        timestamp: One of "unix", "unixns", or "iso", which determines
            how timestamps are formatted in the response
        timezone: Timezone offset, in seconds, used to calculate
            string-based timestamp formats such as datetime and iso.
            For example, PST (UTC-0800) is represented as -28800.
            If omitted, the timezone is UTC.
        client: If specified, this client is used to fetch data from the
            API. Otherwise, the global StreamClient is used.

    Returns:
        An iterator over paginated API responses.

    """
    params = {
        'stream_id': stream_id,
        'start_time': start_time,
        'end_time': end_time,
        'resolution': resolution,
        'batch_operation': batch_operation,
        'format': 'csv',
        'limit': limit,
        'page_token': page_token,
        'timestamp': timestamp,
        'timezone': timezone,
        'client': client,
    }
    return get_stream_availability(**params)


def get_stream_availability_json(
    stream_id: Union[str, List[str]],
    start_time: Union[float, datetime.date],
    end_time: Union[float, datetime.date],
    resolution: int,
    batch_operation: Optional[str] = None,
    limit: Optional[int] = None,
    page_token: Optional[str] = None,
    timestamp: Optional[str] = 'iso',
    timezone: Optional[int] = None,
    client: Optional[StreamClient] = None
) -> Iterator[dict]:
    """
    Fetch the availability of 1 or multiple streams. Iterates over the
    JSON-formatted results as dicts.

    Args:
        Args:
        stream_id: 1 or multiple stream IDs. If multiple stream IDs are
            specified, must also specify batch_operation.
        start_time: Start time for the query, provided as a unix timestamp
            (in seconds) or a datetime.date.
        end_time: End time for the query, provided as a unix timestamp
            (in seconds) or a datetime.date.
        resolution: Interval between returned timestamps, in seconds.
        batch_operation: Either "any" or "all", which determines
            what type of batch calculation will determine availability for
            multiple streams. Availability values will equal 1 when
            data is available for "all" or "any" of the requested streams in
            the given interval.
            This argument is required when multiple stream IDs are specified.
        limit: Maximum number of timestamps to return, across *all pages*
            of the response. A limit of 0 (default) will fetch all
            available data.
        page_token: Token to fetch the subsequent page of results.
            The value is obtained from the 'X-Rune-Next-Page-Token'
            response header field.
        timestamp: One of "unix", "unixns", or "iso", which determines
            how timestamps are formatted in the response
        timezone: Timezone offset, in seconds, used to calculate
            string-based timestamp formats such as datetime and iso.
            For example, PST (UTC-0800) is represented as -28800.
            If omitted, the timezone is UTC.
        client: If specified, this client is used to fetch data from the
            API. Otherwise, the global StreamClient is used.

    Returns:
        An iterator over paginated API responses.
    """
    params = {
        'stream_id': stream_id,
        'start_time': start_time,
        'end_time': end_time,
        'resolution': resolution,
        'batch_operation': batch_operation,
        'format': 'json',
        'limit': limit,
        'page_token': page_token,
        'timestamp': timestamp,
        'timezone': timezone,
        'client': client,
    }
    return get_stream_availability(**params)
