"""
Tests for fetching org metadata.

"""

from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import GraphClient
from runeq.resources.event import Event, _reformat_event, get_patient_events


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
        self.assertEqual(
            self.test_event.rune_classification, "patient.activity.testing"
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
                "rune_classification": "patient.activity.testing",
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

        events = get_patient_events(
            patient_id="abc", start_time=1, end_time=2, client=self.mock_client
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
                "rune_classification": "patient.activity.boxing",
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
                },
                "rune_classification": "patient.medication",
                "tags": [],
                "method": "manual",
                "created_at": 1731267538.123,
                "updated_at": 1731267538.456,
                "id": "event2",
            },
        ]

        self.assertEqual(expected, events.to_list())
