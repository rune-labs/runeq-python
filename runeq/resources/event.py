"""
Events are created by users of the StrivePD app. They fall into
many different categories, including:

    - Activities (manually logged or ingested from HealthKit)
    - Medication logs
    - Supplement logs
    - Wellbeing
    - etc.

Utility functions are provided to query events of specific types.
Other event categories may exist: use the get_patient_events function to
fetch events of any type.

NOTE: There is significant overlap between the Events that are selected by 
this class and the ones that are available to be queried through the Stream APIs.
One critical difference is that these Events can be updated if a StrivePD user makes
a change in the app. Stream API events are not updated in every case.
**We recommend using the classes in this module to query patient Events, whenever
possible.**

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
        start_time: float,
        end_time: Optional[float],
        classification: dict,
        display_name: str,
        payload: Optional[dict] = None,
        method: Optional[str] = None,
        **attributes,
    ):
        """
        Initialize an Event: an item recorded by a user of the StrivePD app.

        Args:
            id: Event ID
            patient_id: Patient ID
            start_time: Start time of the event
            end_time: End time of the event
            classification: Event classification (see below for details).
            display_name: display name of the event
            payload: Event payload
            **attributes: additional event metadata (included in the dict
                representation of the Event).


        Event classification is a three-level hierarchy, represented as a
        dictionary with 2 or 3 keys:
            - "namespace": the general source of the event (e.g. "patient")
            - "category": the type of event (e.g. "activity", "medication")
            - "enum": a specific enumeration within the category. Not all events
                have an enumeration

        Note that this classification uses similar (but not identical!) terminology to
        the events that are queryable through the V2 Stream API.

        """
        self.patient_id = patient_id
        self.start_time = start_time
        self.end_time = end_time

        # validate classification
        expected_keys = {"namespace", "category"}
        missing_keys = expected_keys - classification.keys()
        if missing_keys:
            raise ValueError(f"Classification missing required keys: {missing_keys}")

        self.classification = classification

        # parse classification into the stringified version (which
        # is a little more convenient for dataframes)
        parts = [
            classification["namespace"],
            classification["category"],
            classification.get("enum"),
        ]
        self.rune_classification = ".".join(filter(None, parts))

        self.display_name = display_name
        self.payload = payload or {}
        self.method = method

        super().__init__(
            id=id,
            patient_id=patient_id,
            start_time=start_time,
            end_time=end_time,
            classification=classification,
            rune_classification=self.rune_classification,
            display_name=display_name,
            payload=payload,
            method=method,
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
        ) {
            events {
                id
                display_name: displayName
                custom_detail: customDetail {
                    display_name: displayName
                }
                duration {
                    start_time: startTime
                    end_time: endTime
                    end_time_max: endTimeMax
                }
                payload
                classification {
                    namespace
                    category
                    enum
                }
                tags {
                    name
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
    start_time: float,
    end_time: float,
    include_filters: Optional[list] = None,
    client: Optional[GraphClient] = None,
):
    """Query events for a patient and iterate over the results.

    Formats each event as kwargs that can be passed to Event.

    """
    graph_client = client or global_graph_client()

    next_cursor = None

    variables = {}
    if include_filters:
        variables["include_filters"] = include_filters

    while True:
        result = graph_client.execute(
            statement=_EVENT_GQL_QUERY,
            # GraphQL variables
            patient_id=patient_id,
            cursor=next_cursor,
            start_time=start_time,
            end_time=end_time,
            **variables,
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
    event["start_time"] = duration.get("start_time")

    end_time = duration["end_time"]
    end_time_max = duration["end_time_max"]
    if end_time_max is not None:
        end_time = end_time_max

    event["end_time"] = end_time

    # set a single display name, using custom_detail if available
    custom_detail = event.pop("custom_detail") or {}
    custom_name = custom_detail.get("display_name")
    if custom_name:
        event["display_name"] = custom_name

    # parse the payload as JSON
    payload = event.pop("payload") or "{}"
    event["payload"] = json.loads(payload)

    # flatten tag names into a list
    tags = event.pop("tags") or []
    event["tags"] = [tag["name"] for tag in tags]


def get_patient_events(
    patient_id: str,
    start_time: float,
    end_time: float,
    include_filters: Optional[list] = None,
    client: Optional[GraphClient] = None,
) -> EventSet:
    """Fetch a patient's Events, in an optional time range.

    Args:
        patient_id: Patient ID
        start_time: Optional start time for the query range
        end_time: Optional end time for the query range
        include_filters: Event classification filters to include. If
            this is not specified, all events are returned.
        client: GraphClient instance (optional)

    """
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
    start_time: float,
    end_time: float,
    client: Optional[GraphClient] = None,
) -> EventSet:
    """Fetch a patient's activity Events.

    This includes activities that were manually logged through the
    StrivePD app and activities ingested from HealthKit (which can
    come from third party apps or devices).

    """
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
    start_time: float,
    end_time: float,
    client: Optional[GraphClient] = None,
) -> EventSet:
    """Fetch a patient's medication Events, as recorded through
    the StrivePD app.

    NOTES:
    - There are several ways to log a medication in StrivePD,
      including an "autolog" feature that automatically records a
      medication on a schedule. The "method" attribute of the Event
      object indicates how the medication event was created.
    - The display name for custom medications is only queryable by
      certain user roles. These event logs will default to a generic
      display name.

    """
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
    start_time: float,
    end_time: float,
    client: Optional[GraphClient] = None,
) -> EventSet:
    """Fetch a patient's wellbeing Events, as recorded through
    the StrivePD app.

    """
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
