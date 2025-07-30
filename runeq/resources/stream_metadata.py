"""
Fetch metadata about streams, including stream types.

"""
import datetime
import json
from io import StringIO
from typing import Callable, Iterable, Iterator, List, Optional, Type, Union

import pandas as pd

from runeq.errors import RuneError

from .client import GraphClient, StreamClient, global_graph_client
from .common import ItemBase, ItemSet
from .patient import Device, Patient, get_patient
from .stream import _time_type, get_stream_availability, get_stream_data


class Dimension(ItemBase):
    """
    A dimension of a stream type. This is akin to a column in a table,
    where each value in the timeseries is a row.

    """

    def __init__(
        self, id: str, data_type: str, quantity_name: str, unit_name: str, **attributes
    ):
        """
        Initialize with metadata.

        Args:
            id: Dimension ID
            data_type: Data type (e.g. sfloat, timestamp, etc...)
            quantity_name: Name of the quantity measured
            unit_name: Name of the unit measurement

        """
        self.data_type = data_type
        self.quantity_name = quantity_name
        self.unit_name = unit_name

        super().__init__(
            id=id,
            data_type=data_type,
            quantity_name=quantity_name,
            unit_name=unit_name,
            **attributes,
        )


class StreamType(ItemBase):
    """
    A stream type to categorize streams.

    It represents the physical quantity being measured (voltage, acceleration,
    etc), including the unit of measurement. It also describes the shape of
    the stream’s data, as one or more dimensions.

    """

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        dimensions: List[Dimension],
        **attributes,
    ):
        """
        Initialize with metadata.

        Args:
            id: StreamType ID
            name: Human-readable name of the stream type
            description: Human-readable description of the stream type
            dimensions: List of Dimensions in this stream type

        """
        self.name = name
        self.description = description
        self.dimensions = dimensions

        super().__init__(
            id=id,
            name=name,
            description=description,
            dimensions=dimensions,
            **attributes,
        )

    def to_dict(self) -> dict:
        """
        Dictionary representation of the Stream Type attributes.

        """
        attrs = self._attributes.copy()
        attrs["dimensions"] = [dim.to_dict() for dim in self.dimensions]
        return attrs


class StreamTypeSet(ItemSet[StreamType]):
    """
    A collection of StreamTypes.

    """

    def __init__(self, items: Iterable[StreamType] = ()):
        """
        Initialize with StreamTypes.

        """
        super().__init__(items=items)

    @property
    def _item_class(self) -> Type[ItemBase]:
        """
        Instance type of items in this set.

        """
        return StreamType


def get_all_stream_types(client: Optional[GraphClient] = None) -> StreamTypeSet:
    """
    Get all stream types.

    Args:
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    """
    client = client or global_graph_client()
    query = """
        query getStreamTypes {
            streamTypeList {
                streamTypes {
                    id
                    name
                    description
                    shape {
                        dimensions {
                            id: identifier
                            data_type: dataType
                            quantity_name: quantityName
                            quantity_abbrev: quantityAbbrev
                            unit_name: unitName
                            unit_abbrev: unitAbbrev
                        }
                    }
                }
            }
        }
    """

    stream_type_set = StreamTypeSet()
    result = client.execute(statement=query)

    stream_type_list = result.get("streamTypeList", {})

    for stream_attrs in stream_type_list.get("streamTypes", []):
        stream_type = _parse_stream_type(stream_attrs)
        stream_type_set.add(stream_type)

    return stream_type_set


def _parse_stream_type(stream_type_attrs: dict) -> StreamType:
    """
    Parse stream type graphql response body.

    Args:
        stream_type_attrs: Attribute dictionary from a graph ql response
            representing a stream type.


    """
    # Create a dimension set from the stream's dimensions
    dimensions = []
    for dimension_attrs in stream_type_attrs["shape"].get("dimensions", []):
        dimensions.append(Dimension(**dimension_attrs))

    del stream_type_attrs["shape"]

    return StreamType(dimensions=dimensions, **stream_type_attrs)


class StreamMetadata(ItemBase):
    """
    Metadata for a stream (i.e. timeseries data). This class also has methods
    that fetch data for the stream.

    """

    def __init__(
        self,
        id: str,
        created_at: float,
        algorithm: str,
        device_id: str,
        patient_id: str,
        stream_type: StreamType,
        min_time: float,
        max_time: float,
        parameters: dict,
        **attributes,
    ):
        """
        Initialize with metadata.

        Args:
            id: Stream ID
            created_at: When the stream was created, as a Unix timestamp, as
                a Unix timestamp (in seconds).
            algorithm: A versioned label that describes the process that was
                used to derive this timeseries.
            device_id: Device ID
            patient_id: Patient ID
            stream_type: Stream type, which categorizes the stream data.
            min_time: The earliest timestamp in the stream, as a Unix timestamp
                (in seconds).
            max_time: The latest timestamp in the stream, as a Unix timestamp
                (in seconds).
            parameters: Key/value pairs that label the stream.

        """
        self.created_at = created_at
        self.algorithm = algorithm
        self.device_id = device_id
        self.patient_id = patient_id
        self.stream_type = stream_type
        self.min_time = min_time
        self.max_time = max_time
        self.parameters = parameters

        super().__init__(
            id=id,
            created_at=created_at,
            algorithm=algorithm,
            device_id=device_id,
            patient_id=patient_id,
            stream_type=stream_type,
            min_time=min_time,
            max_time=max_time,
            parameters=parameters,
            **attributes,
        )

    def to_dict(self) -> dict:
        """
        Dictionary representation of the StreamMetadata attributes.

        """
        attrs = self._attributes.copy()
        attrs["stream_type"] = self.stream_type.to_dict()
        return attrs

    def iter_stream_data(
        self,
        start_time: Optional[_time_type] = None,
        start_time_ns: Optional[int] = None,
        end_time: Optional[_time_type] = None,
        end_time_ns: Optional[int] = None,
        format: Optional[str] = "csv",
        limit: Optional[int] = None,
        page_token: Optional[str] = None,
        timestamp: Optional[str] = "iso",
        timezone: Optional[int] = None,
        translate_enums: Optional[bool] = True,
        client: Optional[StreamClient] = None,
    ) -> Iterator[Union[str, dict]]:
        """
        Iterate over CSV-formatted data for this stream.

        Args:
            start_time: Start time for the query, provided as a unix timestamp
                (in seconds), a datetime.datetime, or a datetime.date.
            start_time_ns: Start time for the query, provided as a unix
                timestamp (in nanoseconds).
            end_time: End time for the query, provided as a unix timestamp
                (in seconds), a datetime.datetime, or a datetime.date.
            end_time_ns: End time for the query, provided as a unix timestamp
                (in nanoseconds).
            format: Either "csv" (default) or "json". Determines the content
                type of the API response, as well as the type that
                is returned from this function.
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
                representation. Otherwise, enums are returned as integer
                values.
            client: If specified, this client is used to fetch data from the
                API. Otherwise, the global
                :class:`~runeq.resources.client.StreamClient` is used.

        Returns:
            An iterator over paginated API responses. If format is "json", each
            response is a dict. If format is "csv", each response is a
            CSV-formatted string.

        """
        return get_stream_data(
            stream_id=self.id,
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
            client=client,
        )

    def _add_metadata_to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Returns a new dataframe, with metadata columns added.

        """
        return df.assign(
            stream_id=self.id,
            stream_type_id=self.stream_type.id,
            patient_id=self.patient_id,
            device_id=self.device_id,
            algorithm=self.algorithm,
            **self.parameters,
        )

    def get_stream_dataframe(
        self,
        start_time: Optional[Union[float, datetime.date]] = None,
        start_time_ns: Optional[int] = None,
        end_time: Optional[Union[float, datetime.date]] = None,
        end_time_ns: Optional[int] = None,
        limit: Optional[int] = None,
        page_token: Optional[str] = None,
        timestamp: Optional[str] = "iso",
        timezone: Optional[int] = None,
        translate_enums: Optional[bool] = True,
        stream_client: Optional[StreamClient] = None,
    ) -> pd.DataFrame:
        """
        Get stream data as an enriched Pandas dataframe. In addition to the raw
        stream data, the dataframe also includes columns with stream metadata.
        This allows for the concatenation of dataframes with data from
        multiple streams.

        Args:
            start_time: Start time for the query, provided as a unix timestamp
                    (in seconds) or a datetime.date.
            start_time_ns: Start time for the query, provided as a unix
                timestamp (in nanoseconds).
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
            timestamp: Optional enum "unix", "unixns", or "iso", which
                determines how timestamps are formatted in the response
            timezone: Optional timezone offset, in seconds, used to calculate
                string-based timestamp formats such as datetime and iso.
                For example, PST (UTC-0800) is represented as -28800.
                If omitted, the timezone is UTC.
            translate_enums: If True, enum values are returned as their string
                representation. Otherwise, enums are returned as integer
                values.
            stream_client: If specified, this client is used to fetch data
                from the API. Otherwise, the global StreamClient is used.

        """
        params = {
            "stream_id": self.id,
            "start_time": start_time,
            "start_time_ns": start_time_ns,
            "end_time": end_time,
            "end_time_ns": end_time_ns,
            "format": "csv",
            "limit": limit,
            "page_token": page_token,
            "timestamp": timestamp,
            "timezone": timezone,
            "translate_enums": translate_enums,
        }

        all_stream_dfs = []
        for resp in get_stream_data(client=stream_client, **params):
            all_stream_dfs.append(pd.read_csv(StringIO(resp), sep=","))

        stream_df = pd.concat(all_stream_dfs, axis=0, ignore_index=True)

        # Convert "dict" dimensions to native dicts (from strings)
        for dim in self.stream_type.dimensions:
            if dim.data_type == "dict":
                stream_df[dim.id] = stream_df[dim.id].apply(json.loads)

        # Add metadata before returning the dataframe
        return self._add_metadata_to_dataframe(stream_df)

    def get_stream_availability_dataframe(
        self,
        start_time: Union[float, datetime.date],
        end_time: Union[float, datetime.date],
        resolution: int,
        limit: Optional[int] = None,
        page_token: Optional[str] = None,
        timestamp: Optional[str] = "iso",
        timezone: Optional[int] = None,
        stream_client: Optional[StreamClient] = None,
    ) -> pd.DataFrame:
        """
        Get stream availability as an enriched Pandas dataframe. The dataframe
        includes columns with metadata for this stream. This allows for the
        concatenation of dataframes with availability for multiple streams.

        Args:
            start_time: Start time for the query, provided as a unix timestamp
                    (in seconds) or a datetime.date.
            end_time: End time for the query, provided as a unix timestamp
                (in seconds) or a datetime.date.
            resolution: Interval between returned timestamps, in seconds.
            limit: Maximum number of timestamps to return, across *all pages*
                of the response. A limit of 0 (default) will fetch all
                available data.
            page_token: Token to fetch the subsequent page of results.
                The value is obtained from the 'X-Rune-Next-Page-Token'
                response header field.
            timestamp: Optional enum "unix", "unixns", or "iso", which
                determines how timestamps are formatted in the response
            timezone: Optional timezone offset, in seconds, used to calculate
                string-based timestamp formats such as datetime and iso.
                For example, PST (UTC-0800) is represented as -28800.
                If omitted, the timezone is UTC.
            stream_client: If specified, this client is used to fetch data
                from the API. Otherwise, the global StreamClient is used.

        """
        responses = get_stream_availability(
            stream_ids=self.id,
            start_time=start_time,
            end_time=end_time,
            resolution=resolution,
            format="csv",
            limit=limit,
            page_token=page_token,
            timestamp=timestamp,
            timezone=timezone,
            client=stream_client,
        )

        all_stream_dfs = []
        for resp in responses:
            all_stream_dfs.append(pd.read_csv(StringIO(resp), sep=","))

        stream_df = pd.concat(all_stream_dfs, axis=0, ignore_index=True)
        # Add metadata before returning the dataframe
        return self._add_metadata_to_dataframe(stream_df)


class StreamMetadataSet(ItemSet[StreamMetadata]):
    """
    A collection of StreamMetadata.

    """

    def __init__(self, items: Iterable[StreamMetadata] = ()):
        """
        Initialize with StreamMetadatas

        """
        super().__init__(items=items)

    @property
    def _item_class(self) -> Type[ItemBase]:
        """
        Instance type of items in this set.

        """
        return StreamMetadata

    def filter(
        self,
        stream_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        device_id: Optional[str] = None,
        stream_type_id: Optional[str] = None,
        algorithm: Optional[str] = None,
        category: Optional[str] = None,
        measurement: Optional[str] = None,
        filter_function: Optional[Callable[[StreamMetadata], bool]] = None,
        **parameters,
    ) -> "StreamMetadataSet":
        """
        Filters streams for those that match ALL optional filter parameters.
        Returns a new StreamMetadataSet.

        Args:
            stream_id: Stream ID
            patient_id: Patient ID
            device_id: Device ID
            stream_type_id: Stream type ID
            algorithm: A versioned label that describes the process that was
                used to derive this timeseries.
            category: A broad categorization of the data type (e.g. neural,
                vitals, etc)
            measurement: A specific label for what is being measured
                (e.g. heart_rate, step_count, etc).
            filter_function: User-defined filter function which accepts a
                Stream as a single argument and returns a boolean indicating
                whether to keep that stream.

        """
        new_stream_set = StreamMetadataSet()

        for stream in self._items.values():
            if (
                (not stream_id or stream.id == stream_id)
                and (not patient_id or stream.patient_id == patient_id)
                and (not device_id or stream.device_id == device_id)
                and (not stream_type_id or stream.stream_type.id == stream_type_id)
                and (not algorithm or stream.algorithm == algorithm)
                and (not category or stream.get("category") == category)
                and (not measurement or stream.get("measurement") == measurement)
                and all(
                    stream.get(param_name) == param
                    for param_name, param in parameters.items()
                )
                and (not filter_function or filter_function(stream))
            ):
                new_stream_set.add(stream)

        return new_stream_set

    def get_stream_dataframe(
        self,
        start_time: Optional[Union[float, datetime.date]] = None,
        start_time_ns: Optional[int] = None,
        end_time: Optional[Union[float, datetime.date]] = None,
        end_time_ns: Optional[int] = None,
        limit: Optional[int] = None,
        page_token: Optional[str] = None,
        timestamp: Optional[str] = "iso",
        timezone: Optional[int] = None,
        translate_enums: Optional[bool] = True,
        stream_client: Optional[StreamClient] = None,
    ) -> pd.DataFrame:
        """
        Get raw data for all streams in the collection, as an enriched Pandas
        dataframe. The dataframe includes columns with metadata for each
        stream.

        Args:
            start_time: Start time for the query, provided as a unix timestamp
                    (in seconds) or a datetime.date.
            start_time_ns: Start time for the query, provided as a unix
                timestamp (in nanoseconds).
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
            timestamp: Optional enum "unix", "unixns", or "iso", which
                determines how timestamps are formatted in the response
            timezone: Optional timezone offset, in seconds, used to calculate
                string-based timestamp formats such as datetime and iso.
                For example, PST (UTC-0800) is represented as -28800.
                If omitted, the timezone is UTC.
            translate_enums: If True, enum values are returned as their string
                representation. Otherwise, enums are returned as integer
                values.
            stream_client: If specified, this client is used to fetch data
                from the API. Otherwise, the global StreamClient is used.

        """
        all_stream_dfs = []
        for stream_meta in self._items.values():
            stream_df = stream_meta.get_stream_dataframe(
                start_time=start_time,
                start_time_ns=start_time_ns,
                end_time=end_time,
                end_time_ns=end_time_ns,
                limit=limit,
                page_token=page_token,
                timestamp=timestamp,
                timezone=timezone,
                translate_enums=translate_enums,
                stream_client=stream_client,
            )
            all_stream_dfs.append(stream_df)

        return pd.concat(all_stream_dfs, axis=0, ignore_index=True)

    def get_batch_availability_dataframe(
        self,
        start_time: Union[float, datetime.date],
        end_time: Union[float, datetime.date],
        resolution: int,
        batch_operation: Optional[str] = None,
        limit: Optional[int] = None,
        page_token: Optional[str] = None,
        timestamp: Optional[str] = "iso",
        timezone: Optional[int] = None,
        stream_client: Optional[StreamClient] = None,
    ) -> pd.DataFrame:
        """
        Get stream availability data as a Pandas dataframe. Depending on the
        specified **batch_operation**, this fetches the availability of **all**
        or **any** of the streams in the collection.

        If you want to gather the availability of each *individual* stream in a
        dataframe, see get_stream_availability_dataframe()

        Args:
            start_time: Start time for the query, provided as a unix timestamp
                    (in seconds) or a datetime.date.
            end_time: End time for the query, provided as a unix timestamp
                (in seconds) or a datetime.date.
            resolution: Interval between returned timestamps, in seconds.
            batch_operation: Either "any" or "all", which determines
                what type of batch calculation will determine availability for
                the batch of streams. Availability values will equal 1 when
                data is available for "all" or "any" of the requested streams
                in the given interval.
            limit: Maximum number of timestamps to return, across *all pages*
                of the response. A limit of 0 (default) will fetch all
                available data.
            page_token: Token to fetch the subsequent page of results.
                The value is obtained from the 'X-Rune-Next-Page-Token'
                response header field.
            timestamp: Optional enum "unix", "unixns", or "iso", which
                determines how timestamps are formatted in the response
            timezone: Optional timezone offset, in seconds, used to calculate
                string-based timestamp formats such as datetime and iso.
                For example, PST (UTC-0800) is represented as -28800.
                If omitted, the timezone is UTC.
            stream_client: If specified, this client is used to fetch data
                from the API. Otherwise, the global StreamClient is used.

        """
        responses = get_stream_availability(
            stream_ids=self.ids(),
            start_time=start_time,
            end_time=end_time,
            resolution=resolution,
            batch_operation=batch_operation,
            format="csv",
            limit=limit,
            page_token=page_token,
            timestamp=timestamp,
            timezone=timezone,
            client=stream_client,
        )

        all_stream_dfs = []
        for resp in responses:
            all_stream_dfs.append(pd.read_csv(StringIO(resp), sep=","))

        stream_df = pd.concat(all_stream_dfs, axis=0, ignore_index=True)

        return stream_df


def get_stream_metadata(
    stream_ids: Union[str, Iterable[str]], client: Optional[GraphClient] = None
) -> Union[StreamMetadata, StreamMetadataSet]:
    """
    Get stream metadata for the specified stream_id(s).

    Args:
        stream_ids: ID of the stream or list of IDs
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    Returns:
        StreamMetadata: if a single stream ID is specified
        StreamMetadataSet: if multiple stream IDs are specified

    Raises:
        RuneError: if any of the stream IDs are not found

    """
    client = client or global_graph_client()
    query = """
        query getStreamListByIds($stream_ids: [String]) {
            streamListByIds(streamIds: $stream_ids) {
              pageInfo {
                  endCursor
              }
              streams {
                id
                created_at: createdAt
                algorithm
                device_id: deviceId
                patient_id: patientId
                streamType {
                  id
                  name
                  description
                  shape {
                        dimensions {
                            id: identifier
                            data_type: dataType
                            quantity_name: quantityName
                            quantity_abbrev: quantityAbbrev
                            unit_name: unitName
                            unit_abbrev: unitAbbrev
                        }
                    }
                }
                parameters {
                    key
                    value
                }
                min_time: minTime
                max_time: maxTime
              }
            }
        }
    """
    stream_set = StreamMetadataSet()

    if type(stream_ids) is str:
        stream_ids = [stream_ids]
    else:
        stream_ids = list(stream_ids)

    # Query stream list in batches of <= 100 streams, since graph api cannot
    # query for more than 100 streams at once.
    stream_list_results = []
    for start in range(0, len(stream_ids), 100):
        result = client.execute(
            statement=query,
            stream_ids=stream_ids[start : start + 100],
        )
        stream_list_results.append(result)

    seen_stream_ids = set(stream_ids)
    for result in stream_list_results:
        stream_list = result.get("streamListByIds", {})
        for stream_attrs in stream_list.get("streams", []):
            stream_type = _parse_stream_type(stream_attrs["streamType"])

            del stream_attrs["streamType"]
            norm_dev_id = Device.normalize_id(stream_attrs["device_id"])
            stream_attrs["device_id"] = norm_dev_id

            # Add query parameters to stream attributes
            params = {}
            if stream_attrs.get("parameters"):
                for param in stream_attrs["parameters"]:
                    stream_attrs[param["key"]] = param["value"]
                    params[param["key"]] = param["value"]
                del stream_attrs["parameters"]

            stream = StreamMetadata(
                stream_type=stream_type, parameters=params, **stream_attrs
            )
            stream_set.add(stream)

            try:
                seen_stream_ids.remove(stream.id)
            except KeyError:
                pass

    if len(seen_stream_ids) > 0:
        raise RuneError(f"1+ stream ID(s) not found: {','.join(seen_stream_ids)}")

    if len(stream_set) == 1:
        return list(stream_set)[0]

    return stream_set


def get_patient_stream_metadata(
    patient_id: str,
    device_id: Optional[str] = None,
    stream_type_id: Optional[str] = None,
    algorithm: Optional[str] = None,
    category: Optional[str] = None,
    measurement: Optional[str] = None,
    client: Optional[GraphClient] = None,
    **parameters,
) -> StreamMetadataSet:
    """
    Get stream metadata for a patient's streams, matching ALL filter
    parameters. Only the patient ID is required.

    Args:
        patient_id: Patient ID
        device_id: Device ID
        stream_type_id: Stream type ID
        algorithm: A versioned label that describes the process that was
            used to derive this timeseries.
        category: A broad categorization of the data type (e.g. neural,
            vitals, etc)
        measurement: A specific label for what is being measured
            (e.g. heart_rate, step_count, etc).
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.
        **parameters: Key/value pairs that label the stream.

    """
    if not patient_id:
        raise ValueError("must provide a patient_id")

    # Checks whether patient is accessible, otherwise raises NotFoundError.
    get_patient(patient_id=patient_id, client=client)

    client = client or global_graph_client()
    query = """
        query getStreamList($cursor: Cursor, $filters: StreamQueryFilters) {
            streamList(filters: $filters, cursor: $cursor) {
                pageInfo {
                    endCursor
                }
                streams {
                    id
                    created_at: createdAt
                    algorithm
                    device_id: deviceId
                    patient_id: patientId
                    streamType {
                        id
                        name
                        description
                        shape {
                            dimensions {
                                id: identifier
                                data_type: dataType
                                quantity_name: quantityName
                                quantity_abbrev: quantityAbbrev
                                unit_name: unitName
                                unit_abbrev: unitAbbrev
                            }
                        }
                    }
                    parameters {
                        key
                        value
                    }
                    min_time: minTime
                    max_time: maxTime
                }
            }
        }
    """
    patient_id = Patient.normalize_id(patient_id)

    if device_id:
        device_id = Device.denormalize_id(patient_id, device_id)

    # Add category to params and format params list for filter query
    if category:
        parameters["category"] = category

    # Add measurement to params and format params list for filter query
    if measurement:
        parameters["measurement"] = measurement

    params = []
    for key, val in parameters.items():
        params.append(
            {
                "key": key,
                "value": val,
            }
        )

    filters = {
        "patientId": patient_id,
        "deviceId": device_id,
        "streamTypeId": stream_type_id,
        "algorithm": algorithm,
        "parameters": params,
    }

    next_cursor = None
    stream_set = StreamMetadataSet()

    # Use cursor to page through all filtered streams
    while True:
        result = client.execute(statement=query, filters=filters, cursor=next_cursor)

        stream_list = result.get("streamList", {})
        for stream_attrs in stream_list.get("streams", []):
            stream_type = _parse_stream_type(stream_attrs["streamType"])

            del stream_attrs["streamType"]
            norm_dev_id = Device.normalize_id(stream_attrs["device_id"])
            stream_attrs["device_id"] = norm_dev_id

            # Add query parameters to stream attributes
            params = {}
            if stream_attrs.get("parameters"):
                for param in stream_attrs["parameters"]:
                    stream_attrs[param["key"]] = param["value"]
                    params[param["key"]] = param["value"]
                del stream_attrs["parameters"]

            stream = StreamMetadata(
                stream_type=stream_type, parameters=params, **stream_attrs
            )
            stream_set.add(stream)

        # next_cursor is None when there are no more streams
        next_cursor = stream_list.get("pageInfo", {}).get("endCursor")
        if not next_cursor:
            break

    return stream_set


def get_stream_dataframe(
    stream_ids: Union[str, Iterable[str]],
    start_time: Optional[Union[float, datetime.date]] = None,
    start_time_ns: Optional[int] = None,
    end_time: Optional[Union[float, datetime.date]] = None,
    end_time_ns: Optional[int] = None,
    limit: Optional[int] = None,
    page_token: Optional[str] = None,
    timestamp: Optional[str] = "iso",
    timezone: Optional[int] = None,
    translate_enums: Optional[bool] = True,
    stream_client: Optional[StreamClient] = None,
    graph_client: Optional[GraphClient] = None,
) -> pd.DataFrame:
    """
    Get stream(s) as enriched dataframe with stream data and metadata.

    Args:
        stream_ids: 1 or multiple stream IDs
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
        timestamp: Optional enum "unix", "unixns", or "iso", which determines
            how timestamps are formatted in the response
        timezone: Optional timezone offset, in seconds, used to calculate
            string-based timestamp formats such as datetime and iso.
            For example, PST (UTC-0800) is represented as -28800.
            If omitted, the timezone is UTC.
        translate_enums: If True, enum values are returned as their string
            representation. Otherwise, enums are returned as integer values.
        stream_client: If specified, this client is used to fetch data from the
            API. Otherwise, the global StreamClient is used.
        graph_client: If specified, this client is used to fetch metadata from
            the API. Otherwise, the global GraphClient is used.

    Raises:
        RuneError: if any of the stream IDs is not found.

    """
    stream_meta_set = get_stream_metadata(stream_ids=stream_ids, client=graph_client)

    return stream_meta_set.get_stream_dataframe(
        start_time=start_time,
        start_time_ns=start_time_ns,
        end_time=end_time,
        end_time_ns=end_time_ns,
        limit=limit,
        page_token=page_token,
        timestamp=timestamp,
        timezone=timezone,
        translate_enums=translate_enums,
        stream_client=stream_client,
    )


def get_stream_availability_dataframe(
    stream_ids: Union[str, Iterable[str]],
    start_time: Union[float, datetime.date],
    end_time: Union[float, datetime.date],
    resolution: int,
    batch_operation: Optional[str] = None,
    limit: Optional[int] = None,
    page_token: Optional[str] = None,
    timestamp: Optional[str] = "iso",
    timezone: Optional[int] = None,
    stream_client: Optional[StreamClient] = None,
    graph_client: Optional[GraphClient] = None,
) -> pd.DataFrame:
    """
    Get stream availability data as a dataframe. If a single stream_id is
    passed in, the dataframe will be enriched with the stream's metadata.
    Otherwise it will contain just the availability data.

    Note that this is different from the get_stream_availability_dataframe
    method on the :class:`~runeq.resources.stream_metadata.StreamMetadataSet`.
    This dataframe contains the availability of each *individual* stream.

    Args:
        stream_ids: 1 or multiple stream IDs
        start_time: Start time for the query, provided as a unix timestamp
                (in seconds) or a datetime.date.
        end_time: End time for the query, provided as a unix timestamp
            (in seconds) or a datetime.date.
        resolution: Interval between returned timestamps, in seconds.
        batch_operation: Either "any" or "all", which determines
            what type of batch calculation will determine availability for the
            batch of streams. Availability values will equal 1 when
            data is available for "all" or "any" of the requested streams in
            the given interval.
        limit: Maximum number of timestamps to return, across *all pages*
            of the response. A limit of 0 (default) will fetch all
            available data.
        page_token: Token to fetch the subsequent page of results.
            The value is obtained from the 'X-Rune-Next-Page-Token'
            response header field.
        timestamp: Optional enum "unix", "unixns", or "iso", which determines
            how timestamps are formatted in the response
        timezone: Optional timezone offset, in seconds, used to calculate
            string-based timestamp formats such as datetime and iso.
            For example, PST (UTC-0800) is represented as -28800.
            If omitted, the timezone is UTC.
        stream_client: If specified, this client is used to fetch data from the
            API. Otherwise, the global StreamClient is used.
        graph_client: If specified, this client is used to fetch metadata from
            the API. Otherwise, the global GraphClient is used.

    """
    # Standardize iterable stream_ids to a list (so that we can use len)
    if type(stream_ids) is not str:
        stream_ids = list(stream_ids)

    # If there are multiple stream ids, there is no need to get metadata
    # since the dataframe response will be simplified
    if type(stream_ids) is list and len(stream_ids) > 1:
        responses = get_stream_availability(
            stream_ids=stream_ids,
            start_time=start_time,
            end_time=end_time,
            resolution=resolution,
            batch_operation=batch_operation,
            format="csv",
            limit=limit,
            page_token=page_token,
            timestamp=timestamp,
            timezone=timezone,
            client=stream_client,
        )

        all_stream_dfs = []
        for resp in responses:
            all_stream_dfs.append(pd.read_csv(StringIO(resp), sep=","))

        stream_df = pd.concat(all_stream_dfs, axis=0, ignore_index=True)

        return stream_df

    # Since there is only one stream id, we can enrich the dataframe with
    # metadata
    stream_meta = get_stream_metadata(stream_ids=stream_ids, client=graph_client)

    return stream_meta.get_stream_availability_dataframe(
        start_time=start_time,
        end_time=end_time,
        resolution=resolution,
        limit=limit,
        page_token=page_token,
        timestamp=timestamp,
        timezone=timezone,
        stream_client=stream_client,
    )
