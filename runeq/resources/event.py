"""
Events are created by users of the StrivePD app. They fall into
many different categories, including:

    - Activities (manually logged or ingested from HealthKit)
    - Medication logs
    - Supplement logs
    - Wellbeing
    - etc.

Some utility functions are provided to fetch events of specific types.
Other event categories may exist: use the get_patient_events function to 
fetch events of any type.

TODO: touch up function docstrings

"""

import json
from typing import Iterable, Optional, Type

from .client import GraphClient, global_graph_client
from .common import ItemBase, ItemSet


class Event(ItemBase):
    """
    A single event.

    """

    def __init__(
        self,
        id: str,
        patient_id: str,
        display_name: str,
        start_time: float,
        end_time: Optional[float],
        payload: dict,
        **attributes,
    ):
        """
        Initialize with metadata.

        Args:
            id: event ID
            patient_id: patient ID
            display_name: display name of the event
            start_time: start time of the event
            end_time: end time of the event
            payload: event payload
            attributes: additional event metadata

        """
        self.patient_id = patient_id
        self.display_name = display_name
        self.start_time = start_time
        self.end_time = end_time
        self.payload = payload

        super().__init__(
            id=id,
            patient_id=patient_id,
            display_name=display_name,
            start_time=start_time,
            end_time=end_time,
            payload=payload,
            **attributes,
        )

    def __repr__(self):
        """
        Override repr, to include start time and name

        """
        return (
            f"{self.__class__.__name__}("
            f'name="{self.display_name}", start_time={self.start_time})'
        )


class EventSet(ItemSet):
    """
    A collection of Events.

    """

    def __init__(self, items: Iterable[Event] = ()):
        """
        Initialize with Events.

        """
        super().__init__(items=items)

    @property
    def _item_class(self) -> Type[ItemBase]:
        """
        Instance type of items in this set.

        """
        return Event


# GraphQL query to get patient events
_EVENT_GQL_QUERY = """
query getEventList(
    $patient_id: ID!,
    $cursor: Cursor,
    $start_time: Float!,
    $end_time: Float!,
    $include_filters: [EventClassificationFilter],
) {
    patient(id: $patient_id) {
        eventList(
            startTime: $start_time,
            endTime: $end_time,
            cursor: $cursor,
            includeFilters: $include_filters,
            excludeFilters: $exclude_filters,
        ) {
            events {
                id
                display_name: displayName
                customDetail {
                    displayName
                }
                duration {
                    startTime
                    endTime
                    endTimeMax
                }
                payload
                classification {
                    namespace
                    category
                    enum
                }
                tags {
                    name
                    display_name: displayName
                }
                method
                created_at: createdAt
                updated_at: updatedAt
            }
            pageInfo {
                endCursor
            }
        }
    }
}
"""


def _iter_events(
    patient_id: str,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    include_filters: Optional[list] = None,
    client: Optional[GraphClient] = None,
):
    """Query events for a patient and iterate over the results.

    Formats each event as kwargs that can be passed to Event.

    """
    graph_client = client or global_graph_client()

    next_cursor = None
    while True:
        result = graph_client.execute(
            statement=_EVENT_GQL_QUERY,
            # GraphQL variables
            patient_id=patient_id,
            cursor=next_cursor,
            start_time=start_time,
            end_time=end_time,
            include_filters=include_filters,
        )

        event_list = result["patient"]["eventList"]
        for event in event_list.get("events", []):
            _reformat_event(event)
            yield Event(patient_id=patient_id, **event)

        next_cursor = event_list.get("pageInfo", {}).get("endCursor")
        if not next_cursor:
            break


def _reformat_event(event: dict):
    """Reformat event in place, so it can be passed as kwargs to initialize Event."""
    # replace duration with start and end time
    duration = event.pop("duration") or {}
    event["start_time"] = duration.get("startTime")

    end_time = duration["endTime"]
    end_time_max = duration["endTimeMax"]
    if end_time_max is not None:
        end_time = end_time_max

    event["end_time"] = end_time

    # set a single display name, using customDetail if available
    custom_detail = event.pop("customDetail") or {}
    custom_name = custom_detail.get("displayName")
    if custom_name:
        event["display_name"] = custom_name

    # parse the payload as JSON
    payload = event.pop("payload") or "{}"
    event["payload"] = json.loads(payload)


def get_patient_events(
    patient_id: str,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    include_filters: Optional[list] = None,
    client: Optional[GraphClient] = None,
) -> EventSet:
    """Fetch all patient events."""
    events = _iter_events(
        patient_id=patient_id,
        start_time=start_time,
        end_time=end_time,
        include_filters=include_filters,
        client=client,
    )

    return EventSet(events)


def get_patient_activity_events(
    patient_id: str,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    client: Optional[GraphClient] = None,
) -> EventSet:
    """Fetch activity events"""
    include_filters = [
        {
            "namespace": "patient",
            "category": "activity",
            "enum": "*",
        }
    ]
    return get_patient_events(
        patient_id=patient_id,
        start_time=start_time,
        end_time=end_time,
        include_filters=include_filters,
        client=client,
    )


def get_patient_medication_events(
    patient_id: str,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    client: Optional[GraphClient] = None,
) -> EventSet:
    """Fetch medication events"""
    include_filters = [
        {
            "namespace": "patient",
            "category": "medication",
            "enum": "*",
        },
    ]
    return get_patient_events(
        patient_id=patient_id,
        start_time=start_time,
        end_time=end_time,
        include_filters=include_filters,
        client=client,
    )


def get_patient_wellbeing_events(
    patient_id: str,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    client: Optional[GraphClient] = None,
) -> EventSet:
    """Fetch wellbeing events"""
    include_filters = [
        {
            "namespace": "patient",
            "category": "wellbeing",
            "enum": "*",
        }
    ]
    return get_patient_events(
        patient_id=patient_id,
        start_time=start_time,
        end_time=end_time,
        include_filters=include_filters,
        client=client,
    )
