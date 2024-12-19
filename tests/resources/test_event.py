"""
Tests for fetching org metadata.

"""

from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import GraphClient
from runeq.resources.event import (
    Event,
    EventSet,
    _reformat_event,
    get_patient_activity_events,
    get_patient_events,
    get_patient_medication_events,
    get_patient_symptom_events,
    get_patient_wellbeing_events,
)


class TestEvent(TestCase):
    """
    Unit tests for the Event class.

    """

    def setUp(self):
        """
        Set up mock graph client for testing.

        """
        self.mock_client = GraphClient(
            Config(client_key_id="test", client_access_key="config")
        )
        self.test_event = Event(
            id="id1",
            patient_id="abc",
            start_time=42.1,
            end_time=None,
            classification={
                "namespace": "patient",
                "category": "activity",
                "enum": "testing",
            },
            display_name="Hello World",
            payload={"hello": "world"},
            method="manual",
            # NOTE: these attributes are returned in the dict representation,
            # but are not set as class attributes
            tags=[{"name": "test", "display_name": "Test"}],
            created_at=123,
            updated_at=456,
        )

    def test_attributes(self):
        """
        Test attributes for an initialized Event.

        """
        self.assertEqual(self.test_event.id, "id1")
        self.assertEqual(self.test_event.patient_id, "abc")
        self.assertEqual(self.test_event.display_name, "Hello World")
        self.assertEqual(self.test_event.start_time, 42.1)
        self.assertEqual(self.test_event.end_time, None)
        self.assertEqual(self.test_event.payload, {"hello": "world"})
        self.assertEqual(
            self.test_event.classification,
            {
                "namespace": "patient",
                "category": "activity",
                "enum": "testing",
            },
        )
        self.assertEqual(self.test_event.method, "manual")

    def test_to_dict(self):
        """Test dictionary representation"""
        self.assertEqual(
            self.test_event.to_dict(),
            {
                "display_name": "Hello World",
                "end_time": None,
                "id": "id1",
                "patient_id": "abc",
                "payload": {"hello": "world"},
                "start_time": 42.1,
                "classification": {
                    "namespace": "patient",
                    "category": "activity",
                    "enum": "testing",
                },
                "tags": [
                    {
                        "name": "test",
                        "display_name": "Test",
                    }
                ],
                "method": "manual",
                "created_at": 123,
                "updated_at": 456,
            },
        )

    def test_repr(self):
        """
        Test __repr__

        """
        self.assertEqual(
            'Event(name="Hello World", start_time=42.1)', repr(self.test_event)
        )

    def test__reformat_event(self):
        """
        Test _reformat_event

        """
        with self.subTest("no-end-time-max"):
            event = {
                "id": "id1",
                "patient_id": "abc",
                "display_name": "Sleep",
                "custom_detail": None,
                "payload": '{"hello": "world"}',
                "duration": {
                    "start_time": 42.1,
                    "end_time": 99,
                    "end_time_max": None,
                },
                "tags": [],
                "method": "manual",
            }
            _reformat_event(event)

            self.assertEqual(
                event,
                {
                    "id": "id1",
                    "patient_id": "abc",
                    "display_name": "Sleep",
                    "start_time": 42.1,
                    "end_time": 99,
                    "payload": {"hello": "world"},
                    "tags": [],
                    "method": "manual",
                },
            )

        with self.subTest("end-time-max"):
            event = {
                "id": "id1",
                "patient_id": "abc",
                "display_name": "Sleep",
                "custom_detail": {"display_name": ""},
                "payload": '{"hello": "world"}',
                "duration": {
                    "start_time": 42.1,
                    "end_time": 99,
                    "end_time_max": 100,
                },
                "method": "manual",
                "tags": [],
            }
            _reformat_event(event)

            self.assertEqual(
                event,
                {
                    "id": "id1",
                    "patient_id": "abc",
                    "display_name": "Sleep",
                    "start_time": 42.1,
                    "end_time": 100,
                    "payload": {"hello": "world"},
                    "method": "manual",
                    "tags": [],
                },
            )

        with self.subTest("custom-name"):
            event = {
                "id": "id1",
                "patient_id": "abc",
                "display_name": "Custom Event",
                "custom_detail": {"display_name": "Spoonful of Sugar"},
                "payload": '{"hello": "world"}',
                "duration": {
                    "start_time": 42.1,
                    "end_time": None,
                    "end_time_max": None,
                },
                "method": "manual",
                "tags": [],
            }
            _reformat_event(event)

            self.assertEqual(
                event,
                {
                    "id": "id1",
                    "patient_id": "abc",
                    "display_name": "Spoonful of Sugar",
                    "start_time": 42.1,
                    "end_time": None,
                    "payload": {"hello": "world"},
                    "method": "manual",
                    "tags": [],
                },
            )

        with self.subTest("tags"):
            event = {
                "id": "id1",
                "patient_id": "abc",
                "display_name": "Sleep",
                "custom_detail": None,
                "payload": '{"hello": "world"}',
                "duration": {
                    "start_time": 42.1,
                    "end_time": 99,
                    "end_time_max": None,
                },
                "tags": [{"name": "activity.aerobic"}, {"name": "activity.strength"}],
                "method": "manual",
            }
            _reformat_event(event)

            self.assertEqual(
                event,
                {
                    "id": "id1",
                    "patient_id": "abc",
                    "display_name": "Sleep",
                    "start_time": 42.1,
                    "end_time": 99,
                    "payload": {"hello": "world"},
                    "tags": ["activity.aerobic", "activity.strength"],
                    "method": "manual",
                },
            )

    def test_get_patient_events(self):
        """
        Test get_patient_events

        """
        self.mock_client.execute = mock.Mock(
            side_effect=[
                # empty response for the first "chunk" of time in the query range
                {"patient": {"eventList": None}},
                {
                    "patient": {
                        "eventList": {
                            "events": [
                                {
                                    "id": "event1",
                                    "display_name": "Boxing",
                                    "custom_detail": None,
                                    "duration": {
                                        "start_time": 1671267538,
                                        "end_time": 1671268000,
                                        "end_time_max": None,
                                    },
                                    "payload": "",
                                    "classification": {
                                        "namespace": "patient",
                                        "category": "activity",
                                        "enum": "boxing",
                                    },
                                    "tags": [
                                        {
                                            "name": "activity.aerobic",
                                        },
                                        {
                                            "name": "activity.strength",
                                        },
                                    ],
                                    "method": "manual",
                                    "created_at": 1671268000,
                                    "updated_at": 1671268000,
                                }
                            ],
                            "pageInfo": {"endCursor": "cursor!"},
                        }
                    }
                },
                {
                    "patient": {
                        "eventList": {
                            "events": [
                                {
                                    "id": "event2",
                                    "display_name": "Custom Event",
                                    "custom_detail": {
                                        "display_name": "Spoonful of Sugar"
                                    },
                                    "duration": {
                                        "start_time": 1731267538.123,
                                        "end_time": None,
                                        "end_time_max": None,
                                    },
                                    "payload": '{"dosage": 1.0, "failed_dose": false}',
                                    "classification": {
                                        "namespace": "patient",
                                        "category": "medication",
                                        "enum": "custom-123",
                                    },
                                    "tags": [],
                                    "method": "manual",
                                    "created_at": 1731267538.123,
                                    "updated_at": 1731267538.456,
                                }
                            ]
                        }
                    }
                },
            ]
        )

        # Use a time range that is longer than the max.
        # The function should handle splitting it up into chunks.
        events = get_patient_events(
            patient_id="abc",
            start_time=1,
            end_time=10 + 90 * 24 * 60 * 60,
            client=self.mock_client,
        )

        expected = [
            {
                "patient_id": "abc",
                "display_name": "Boxing",
                "start_time": 1671267538,
                "end_time": 1671268000,
                "payload": {},
                "classification": {
                    "namespace": "patient",
                    "category": "activity",
                    "enum": "boxing",
                },
                "tags": ["activity.aerobic", "activity.strength"],
                "method": "manual",
                "created_at": 1671268000,
                "updated_at": 1671268000,
                "id": "event1",
            },
            {
                "patient_id": "abc",
                "display_name": "Spoonful of Sugar",
                "start_time": 1731267538.123,
                "end_time": None,
                "payload": {"dosage": 1.0, "failed_dose": False},
                "classification": {
                    "namespace": "patient",
                    "category": "medication",
                    "enum": "custom-123",
                },
                "tags": [],
                "method": "manual",
                "created_at": 1731267538.123,
                "updated_at": 1731267538.456,
                "id": "event2",
            },
        ]

        self.assertEqual(expected, events.to_list())

    def test_to_dataframe(self):
        """
        Test converting events to a dataframe

        """
        expected_columns = [
            "patient_id",
            "start_time",
            "end_time",
            "namespace",
            "category",
            "enum",
            "display_name",
            "method",
            "payload",
            "tags",
            "created_at",
            "updated_at",
            "id",
        ]

        # Make sure empty dataframe works
        empty_df = EventSet([]).to_dataframe()
        self.assertListEqual(list(empty_df.columns), expected_columns)

        # Test with a few events
        ev2 = Event(
            id="id2",
            patient_id="abc",
            start_time=100,
            end_time=140,
            classification={
                "namespace": "patient",
                "category": "activity",
                "enum": "healthkit-running",
            },
            display_name="Hello World",
            payload={"hello": "world"},
            method="healthkit",
            tags=[],
            created_at=123,
            updated_at=456,
        )

        # same start time as ev2, but an earlier end time
        ev3 = Event(
            id="id3",
            patient_id="abc",
            start_time=100,
            end_time=100,
            classification={
                "namespace": "patient",
                "category": "note",
            },
            display_name="Hello World",
            payload={"hello": "world"},
            method="manual",
            tags=[],
            created_at=123,
            updated_at=456,
        )

        # add events to the event set out of order (they should be sorted
        # by time in the dataframe)
        event_set = EventSet([ev3, self.test_event, ev2])

        df = event_set.to_dataframe()
        self.assertListEqual(list(df.columns), expected_columns)

        # check ids to make sure sorting was done correctly
        self.assertEqual(list(df.id), ["id1", "id3", "id2"])

        # check that classification was expanded into columns
        self.assertEqual(list(df.namespace), ["patient", "patient", "patient"])
        self.assertEqual(list(df.category), ["activity", "note", "activity"])
        self.assertEqual(list(df.enum), ["testing", None, "healthkit-running"])

    def test_event_type_helpers(self):
        """Minimal test to exercise the helpers that fetch one type of event.

        Only asserts that the expected filters were passed to the GraphQL client.

        """
        self.mock_client.execute = mock.Mock(
            return_value={"patient": {"eventList": None}},
        )

        # activity
        get_patient_activity_events(
            "abc", start_time=1, end_time=10, client=self.mock_client
        )
        self.mock_client.execute.assert_called_once_with(
            statement=mock.ANY,
            # GraphQL variables
            patient_id="abc",
            cursor=None,
            start_time=1,
            end_time=10,
            include_filters=[
                {
                    "namespace": "patient",
                    "category": "activity",
                    "enum": "*",
                }
            ],
        )

        # medication
        self.mock_client.execute.reset_mock()

        get_patient_medication_events(
            "abc", start_time=1, end_time=10, client=self.mock_client
        )

        self.mock_client.execute.assert_called_once_with(
            statement=mock.ANY,
            # GraphQL variables
            patient_id="abc",
            cursor=None,
            start_time=1,
            end_time=10,
            include_filters=[
                {
                    "namespace": "patient",
                    "category": "medication",
                    "enum": "*",
                }
            ],
        )

        # symptom
        self.mock_client.execute.reset_mock()

        get_patient_symptom_events(
            "abc", start_time=1, end_time=10, client=self.mock_client
        )

        self.mock_client.execute.assert_called_once_with(
            statement=mock.ANY,
            # GraphQL variables
            patient_id="abc",
            cursor=None,
            start_time=1,
            end_time=10,
            include_filters=[
                {
                    "namespace": "patient",
                    "category": "symptom",
                    "enum": "*",
                }
            ],
        )

        # wellbeing
        self.mock_client.execute.reset_mock()

        get_patient_wellbeing_events(
            "abc", start_time=1, end_time=10, client=self.mock_client
        )

        self.mock_client.execute.assert_called_once_with(
            statement=mock.ANY,
            # GraphQL variables
            patient_id="abc",
            cursor=None,
            start_time=1,
            end_time=10,
            include_filters=[
                {
                    "namespace": "patient",
                    "category": "wellbeing",
                    "enum": "*",
                }
            ],
        )
