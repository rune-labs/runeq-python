"""
Tests for fetching org metadata.

"""

from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import GraphClient
from runeq.resources.event import (
    Event,
    _reformat_event,
    get_activity_events,
    get_medication_events,
    get_patient_events,
    get_wellbeing_events,
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
            display_name="Hello World",
            start_time=42.1,
            end_time=None,
            payload={"hello": "world"},
            # NOTE: these attributes are returned in the dict representation,
            # but are not set as class attributes
            classification={
                "namespace": "patient",
                "category": "activity",
                "enum": "testing",
            },
            tags=[{"name": "test", "display_name": "Test"}],
            method="manual",
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
                "customDetail": None,
                "payload": '{"hello": "world"}',
                "duration": {
                    "startTime": 42.1,
                    "endTime": 99,
                    "endTimeMax": None,
                },
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
                    "method": "manual",
                },
            )

        with self.subTest("end-time-max"):
            event = {
                "id": "id1",
                "patient_id": "abc",
                "display_name": "Sleep",
                "customDetail": {"displayName": ""},
                "payload": '{"hello": "world"}',
                "duration": {
                    "startTime": 42.1,
                    "endTime": 99,
                    "endTimeMax": 100,
                },
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
                    "end_time": 100,
                    "payload": {"hello": "world"},
                    "method": "manual",
                },
            )

        with self.subTest("custom-name"):
            event = {
                "id": "id1",
                "patient_id": "abc",
                "display_name": "Custom Event",
                "customDetail": {"displayName": "Spoonful of Sugar"},
                "payload": '{"hello": "world"}',
                "duration": {
                    "startTime": 42.1,
                    "endTime": None,
                    "endTimeMax": None,
                },
                "method": "manual",
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
                                    "display_name": "Running",
                                    "customDetail": None,
                                    "duration": {
                                        "startTime": 1671267538,
                                        "endTime": 1671268000,
                                        "endTimeMax": None,
                                    },
                                    "payload": "",
                                    "classification": {
                                        "namespace": "patient",
                                        "category": "activity",
                                        "enum": "running",
                                    },
                                    "tags": [
                                        {
                                            "name": "aerobic",
                                            "display_name": "Aerobic",
                                        }
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
                                    "customDetail": {
                                        "displayName": "Spoonful of Sugar"
                                    },
                                    "duration": {
                                        "startTime": 1731267538.123,
                                        "endTime": None,
                                        "endTimeMax": None,
                                    },
                                    "payload": '{"dosage": 1.0, "failed_dose": false}',
                                    "classification": {
                                        "namespace": "patient",
                                        "category": "medication",
                                        "enum": "custom",
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

        events = get_patient_events(patient_id="abc", client=self.mock_client)

        expected = [
            {
                "patient_id": "abc",
                "display_name": "Running",
                "start_time": 1671267538,
                "end_time": 1671268000,
                "payload": {},
                "classification": {
                    "namespace": "patient",
                    "category": "activity",
                    "enum": "running",
                },
                "tags": [
                    {
                        "name": "aerobic",
                        "display_name": "Aerobic",
                    }
                ],
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
                    "enum": "custom",
                },
                "tags": [],
                "method": "manual",
                "created_at": 1731267538.123,
                "updated_at": 1731267538.456,
                "id": "event2",
            },
        ]

        self.assertEqual(expected, events.to_list())
