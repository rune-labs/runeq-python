from typing import Optional, Union

from .common import MemberType, MemberBase, MemberSet
from .patient import PatientSet
from .device import DeviceSet


class Dimension(MemberBase):
    """
    Dimension of a stream of data, including it's data_type, quantity, and units.
    """

    MemberType.DIMENSION


class DimensionSet(MemberSet):
    """
    Representational state for a set of Dimensions.
    """

    MemberType.DIMENSION


class StreamType(MemberBase):
    """
    StreamType is a categorization of streams, representing the physical quantity being measured
    (voltage, acceleration, status, etc). The stream type dictates not only the semantics,
    but also the Dimensions of individual observations.
    """

    member_type = MemberType.STREAM_TYPE


class StreamTypeSet(MemberSet):
    """
    Representational state for a set of StreamTypes.
    """

    member_type = MemberType.STREAM_TYPE


def get_stream_types() -> StreamTypeSet:
    """
    get_stream_types returns a set of all StreamTypes that are queryable.
    """


class Stream(MemberBase):
    """
    A Stream is a single timeseries. A stream has a stream type (see above). It also is defined by
    a unique combination of parameters. Some parameters are always set, like the patient_id, device_id,
    and the algorithm.
    """

    member_type = MemberType.STREAM


class StreamSet(MemberSet):
    """
    Representational state for a set of Streams.
    """

    member_type = MemberType.STREAM

    def filter(
        stream_ids: Optional[Union[StreamSet, list[str]]],
        patient_ids: Optional[Union[PatientSet, list[str]]],
        device_ids: Optional[Union[DeviceSet, list[str]]],
        stream_type_ids: Optional[Union[StreamTypeSet, list[str]]],
        algorithms: Optional[list[str]],
        categories: Optional[list[str]],
        **parameters
    ) -> StreamSet:
        """
        filter() returns a set of all streams which match ALL the parameters. This function can be chained.
        """


def filter_streams(
    stream_ids: Optional[list[str]],
    patient_ids: Optional[list[str]],
    device_ids: Optional[list[str]],
    stream_type_ids: Optional[list[str]],
    algorithms: Optional[list[str]],
    categories: Optional[list[str]],
    **parameters
) -> StreamSet:
    """
    filter_streams() returns a set of all streams which match ALL the parameters.
    """
