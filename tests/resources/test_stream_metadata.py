"""
Tests for fetching stream metadata.

"""
import copy
import json
from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import GraphClient, StreamClient
from runeq.resources.stream_metadata import (
    Dimension,
    StreamMetadata,
    StreamMetadataSet,
    StreamType,
    get_all_stream_types,
    get_patient_stream_metadata,
    get_stream_availability_dataframe,
    get_stream_dataframe,
    get_stream_metadata,
)


class TestDimension(TestCase):
    """
    Unit tests for the Dimension class.

    """

    def test_attributes(self):
        """
        Test attributes for an initialized Dimension.

        """
        test_dim = Dimension(
            id="time",
            data_type="timestamp",
            quantity_name="Time",
            unit_name="Nanoseconds",
            quantity_abbrev="t",
            unitAbbrev="ns",
        )

        self.assertEqual("time", test_dim.id)
        self.assertEqual("timestamp", test_dim.data_type)
        self.assertEqual("Time", test_dim.quantity_name)
        self.assertEqual("Nanoseconds", test_dim.unit_name)


class TestStreamType(TestCase):
    """
    Unit tests for the StreamType class.

    """

    def setUp(self):
        """
        Set up mock graph client for testing.

        """
        self.mock_client = GraphClient(
            Config(client_key_id="test", client_access_key="config")
        )

    def test_attributes(self):
        """
        Test attributes for an initialized Stream.

        """
        test_stream_type = StreamType(
            id="rotation",
            name="Rotation",
            description="Rotation rate (velocity) sampled in the time-domain.",
            dimensions=[],
        )

        self.assertEqual("rotation", test_stream_type.id)
        self.assertEqual("Rotation", test_stream_type.name)
        self.assertEqual(
            "Rotation rate (velocity) sampled in the time-domain.",
            test_stream_type.description,
        )
        self.assertEqual([], test_stream_type.dimensions)

    def test_repr(self):
        """
        Test __repr__

        """
        test_stream_type = StreamType(
            id="rotation",
            name="Rotation",
            description="Rotation rate (velocity) sampled in the time-domain.",
            dimensions=[],
        )
        self.assertEqual(
            'StreamType(id="rotation", name="Rotation")', repr(test_stream_type)
        )

    def test_get_all_stream_types(self):
        """
        Test get all stream types.

        """
        self.mock_client.execute = mock.Mock()
        self.mock_client.execute.side_effect = [
            {
                "streamTypeList": {
                    "streamTypes": [
                        {
                            "id": "rotation",
                            "name": "Rotation",
                            "description": "Rotation rate (angular velocity)",
                            "shape": {
                                "dimensions": [
                                    {
                                        "id": "time",
                                        "data_type": "timestamp",
                                        "quantity_name": "Time",
                                        "quantity_abbrev": "t",
                                        "unit_name": "Nanoseconds",
                                        "unit_abbrev": "ns",
                                    },
                                    {
                                        "id": "rotation",
                                        "data_type": "sfloat",
                                        "quantity_name": "Angular Velocity",
                                        "quantity_abbrev": "Rotation",
                                        "unit_name": "Radians per second",
                                        "unit_abbrev": "rps",
                                    },
                                ]
                            },
                        },
                        {
                            "id": "current",
                            "name": "Current",
                            "description": "Electric current (in Amperes)",
                            "shape": {
                                "dimensions": [
                                    {
                                        "id": "time",
                                        "data_type": "timestamp",
                                        "quantity_name": "Time",
                                        "quantity_abbrev": "t",
                                        "unit_name": "Nanoseconds",
                                        "unit_abbrev": "ns",
                                    },
                                    {
                                        "id": "current",
                                        "data_type": "sfloat",
                                        "quantity_name": "Current",
                                        "quantity_abbrev": "I",
                                        "unit_name": "Amps",
                                        "unit_abbrev": "A",
                                    },
                                ]
                            },
                        },
                    ]
                }
            }
        ]

        stream_types = get_all_stream_types(client=self.mock_client)

        self.assertEqual(
            [
                {
                    "id": "rotation",
                    "name": "Rotation",
                    "description": "Rotation rate (angular velocity)",
                    "dimensions": [
                        {
                            "id": "time",
                            "data_type": "timestamp",
                            "quantity_name": "Time",
                            "quantity_abbrev": "t",
                            "unit_name": "Nanoseconds",
                            "unit_abbrev": "ns",
                        },
                        {
                            "id": "rotation",
                            "data_type": "sfloat",
                            "quantity_name": "Angular Velocity",
                            "quantity_abbrev": "Rotation",
                            "unit_name": "Radians per second",
                            "unit_abbrev": "rps",
                        },
                    ],
                },
                {
                    "id": "current",
                    "name": "Current",
                    "description": "Electric current (in Amperes)",
                    "dimensions": [
                        {
                            "id": "time",
                            "data_type": "timestamp",
                            "quantity_name": "Time",
                            "quantity_abbrev": "t",
                            "unit_name": "Nanoseconds",
                            "unit_abbrev": "ns",
                        },
                        {
                            "id": "current",
                            "data_type": "sfloat",
                            "quantity_name": "Current",
                            "quantity_abbrev": "I",
                            "unit_name": "Amps",
                            "unit_abbrev": "A",
                        },
                    ],
                },
            ],
            stream_types.to_list(),
        )


class TestStreamMetadata(TestCase):
    """
    Unit tests for the StreamMetadata class.

    """

    def setUp(self):
        """
        Set up mock graph and stream clients for testing.

        """
        self.mock_graph_client = GraphClient(
            Config(client_key_id="test", client_access_key="config")
        )

        self.mock_stream_client = StreamClient(
            Config(client_key_id="test", client_access_key="config")
        )

        self.maxDiff = None

    def test_attributes(self):
        """
        Test attributes for an initialized Stream.

        """
        test_stream_type = StreamType(
            id="st1",
            name="stream_type_1",
            description="stream type one",
            dimensions=[],
        )

        test_stream = StreamMetadata(
            id="s1",
            created_at=1629300943.9179766,
            algorithm="a1",
            device_id="d1",
            patient_id="p1",
            stream_type=test_stream_type,
            min_time=1648231560,
            max_time=1648234860,
            parameters={"category": "vitals"},
        )

        self.assertEqual("s1", test_stream.id)
        self.assertEqual(1629300943.9179766, test_stream.created_at)
        self.assertEqual("a1", test_stream.algorithm)
        self.assertEqual("d1", test_stream.device_id)
        self.assertEqual("p1", test_stream.patient_id)
        self.assertEqual(test_stream_type, test_stream.stream_type)
        self.assertEqual(1648231560, test_stream.min_time)
        self.assertEqual(1648234860, test_stream.max_time)
        self.assertEqual({"category": "vitals"}, test_stream.parameters)

    def test_repr(self):
        """
        Test __repr__

        """
        test_stream = StreamMetadata(
            id="s1",
            created_at=1629300943.9179766,
            algorithm="a1",
            device_id="d1",
            patient_id="p1",
            stream_type=None,
            min_time=1648231560,
            max_time=1648234860,
            parameters={"category": "vitals"},
        )
        self.assertEqual('StreamMetadata(id="s1")', repr(test_stream))

    def test_get_stream_metadata(self):
        """
        Test getting stream metadata.

        """
        self.mock_graph_client.execute = mock.Mock()
        self.mock_graph_client.execute.side_effect = [
            {
                "streamListByIds": {
                    "pageInfo": {"endCursor": None},
                    "streams": [
                        {
                            "id": "s1",
                            "created_at": 1655226140.508,
                            "algorithm": "a1",
                            "device_id": "patient-p1,device-d1",
                            "patient_id": "p1",
                            "streamType": {
                                "id": "duration",
                                "name": "Duration",
                                "description": "Duration over time.",
                                "shape": {
                                    "dimensions": [
                                        {
                                            "id": "time",
                                            "data_type": "timestamp",
                                            "quantity_name": "Time",
                                            "quantity_abbrev": "t",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                    ]
                                },
                            },
                            "min_time": 1648231560,
                            "max_time": 1648234860,
                        },
                        {
                            "id": "s2",
                            "created_at": 1655226140.501,
                            "algorithm": "a2",
                            "device_id": "patient-p2,device-d2",
                            "patient_id": "p2",
                            "streamType": {
                                "id": "duration",
                                "name": "Duration",
                                "description": "Duration over time.",
                                "shape": {
                                    "dimensions": [
                                        {
                                            "id": "time",
                                            "data_type": "timestamp",
                                            "quantity_name": "Time",
                                            "quantity_abbrev": "t",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                    ]
                                },
                            },
                            "min_time": 1648231560,
                            "max_time": 1648234860,
                        },
                    ],
                }
            }
        ]

        streams = get_stream_metadata(
            stream_ids=["s1", "s2"], client=self.mock_graph_client
        )

        self.assertEqual(
            [
                {
                    "created_at": 1655226140.508,
                    "algorithm": "a1",
                    "device_id": "d1",
                    "patient_id": "p1",
                    "stream_type": {
                        "name": "Duration",
                        "description": "Duration over time.",
                        "dimensions": [
                            {
                                "data_type": "timestamp",
                                "quantity_name": "Time",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "t",
                                "unit_abbrev": "s",
                                "id": "time",
                            },
                            {
                                "data_type": "sfloat",
                                "quantity_name": "Duration",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "Duration",
                                "unit_abbrev": "s",
                                "id": "duration",
                            },
                        ],
                        "id": "duration",
                    },
                    "parameters": {},
                    "min_time": 1648231560,
                    "max_time": 1648234860,
                    "id": "s1",
                },
                {
                    "created_at": 1655226140.501,
                    "algorithm": "a2",
                    "device_id": "d2",
                    "patient_id": "p2",
                    "stream_type": {
                        "name": "Duration",
                        "description": "Duration over time.",
                        "dimensions": [
                            {
                                "data_type": "timestamp",
                                "quantity_name": "Time",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "t",
                                "unit_abbrev": "s",
                                "id": "time",
                            },
                            {
                                "data_type": "sfloat",
                                "quantity_name": "Duration",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "Duration",
                                "unit_abbrev": "s",
                                "id": "duration",
                            },
                        ],
                        "id": "duration",
                    },
                    "parameters": {},
                    "min_time": 1648231560,
                    "max_time": 1648234860,
                    "id": "s2",
                },
            ],
            streams.to_list(),
        )

    def test_get_over_hundred_stream_metadata(self):
        """
        Test get stream metadata can query for >100 streams by batching
        by requests of size <=100 streams.

        """
        self.mock_graph_client.execute = mock.Mock()

        stream_resp = {
            "created_at": 1655226140.508,
            "algorithm": "a1",
            "device_id": "patient-p1,device-d1",
            "patient_id": "p1",
            "streamType": {
                "id": "duration",
                "name": "Duration",
                "description": "Duration over time.",
                "shape": {
                    "dimensions": [
                        {
                            "id": "time",
                            "data_type": "timestamp",
                            "quantity_name": "Time",
                            "quantity_abbrev": "t",
                            "unit_name": "Seconds",
                            "unit_abbrev": "s",
                        },
                        {
                            "id": "duration",
                            "data_type": "sfloat",
                            "quantity_name": "Duration",
                            "quantity_abbrev": "Duration",
                            "unit_name": "Seconds",
                            "unit_abbrev": "s",
                        },
                    ]
                },
            },
            "min_time": 1648231560,
            "max_time": 1648234860,
        }

        first_hundred_streams = []
        for i in range(100):
            resp = copy.deepcopy(stream_resp)
            resp["id"] = str(i)
            first_hundred_streams.append(resp)

        next_fifty_streams = []
        for i in range(100, 150):
            resp = copy.deepcopy(stream_resp)
            resp["id"] = str(i)
            next_fifty_streams.append(resp)

        self.mock_graph_client.execute.side_effect = [
            {
                "streamListByIds": {
                    "pageInfo": {"endCursor": None},
                    "streams": first_hundred_streams,
                }
            },
            {
                "streamListByIds": {
                    "pageInfo": {"endCursor": None},
                    "streams": next_fifty_streams,
                }
            },
        ]

        streams = get_stream_metadata(
            stream_ids=[str(i) for i in range(150)], client=self.mock_graph_client
        )

        self.assertEqual(150, len(streams.to_list()))

    @mock.patch("runeq.resources.stream_metadata.get_patient")
    def test_get_patient_stream_metadata_no_access(self, get_patient):
        """
        Test get_patient_stream_metadata fails if the user doesn't have access
        to the patient ID or if the patient doesn't exist.
        """
        get_patient.side_effect = Exception("NotFoundError")

        with self.assertRaises(Exception) as context:
            get_patient_stream_metadata(patient_id="foo", client=self.mock_graph_client)

        self.assertTrue("NotFoundError" in str(context.exception))

    @mock.patch("runeq.resources.stream_metadata.get_patient")
    def test_get_patient_streams_basic(self, _):
        """
        Test filtering streams by all parameters.

        """
        self.mock_graph_client.execute = mock.Mock()
        self.mock_graph_client.execute.side_effect = [
            {
                "streamList": {
                    "pageInfo": {"endCursor": None},
                    "streams": [
                        {
                            "id": "s1",
                            "created_at": 1655226140.508,
                            "algorithm": "a1",
                            "device_id": "patient-p1,device-d1",
                            "patient_id": "p1",
                            "streamType": {
                                "id": "duration",
                                "name": "Duration",
                                "description": "Duration over time.",
                                "shape": {
                                    "dimensions": [
                                        {
                                            "id": "time",
                                            "data_type": "timestamp",
                                            "quantity_name": "Time",
                                            "quantity_abbrev": "t",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                    ]
                                },
                            },
                            "parameters": [
                                {"key": "category", "value": "motion"},
                                {"key": "measurement", "value": "walking"},
                            ],
                            "min_time": 1648231560,
                            "max_time": 1648234860,
                        },
                        {
                            "id": "s2",
                            "created_at": 1655226140.501,
                            "algorithm": "a2",
                            "device_id": "patient-p2,device-d2",
                            "patient_id": "p1",
                            "streamType": {
                                "id": "duration",
                                "name": "Duration",
                                "description": "Duration over time.",
                                "shape": {
                                    "dimensions": [
                                        {
                                            "id": "time",
                                            "data_type": "timestamp",
                                            "quantity_name": "Time",
                                            "quantity_abbrev": "t",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                    ]
                                },
                            },
                            "min_time": 1648231560,
                            "max_time": 1648234860,
                        },
                    ],
                }
            }
        ]

        streams = get_patient_stream_metadata(
            patient_id="p1", client=self.mock_graph_client
        )

        self.assertEqual(
            [
                {
                    "created_at": 1655226140.508,
                    "algorithm": "a1",
                    "device_id": "d1",
                    "patient_id": "p1",
                    "stream_type": {
                        "name": "Duration",
                        "description": "Duration over time.",
                        "dimensions": [
                            {
                                "data_type": "timestamp",
                                "quantity_name": "Time",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "t",
                                "unit_abbrev": "s",
                                "id": "time",
                            },
                            {
                                "data_type": "sfloat",
                                "quantity_name": "Duration",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "Duration",
                                "unit_abbrev": "s",
                                "id": "duration",
                            },
                        ],
                        "id": "duration",
                    },
                    "category": "motion",
                    "measurement": "walking",
                    "parameters": {"category": "motion", "measurement": "walking"},
                    "min_time": 1648231560,
                    "max_time": 1648234860,
                    "id": "s1",
                },
                {
                    "created_at": 1655226140.501,
                    "algorithm": "a2",
                    "device_id": "d2",
                    "patient_id": "p1",
                    "stream_type": {
                        "name": "Duration",
                        "description": "Duration over time.",
                        "dimensions": [
                            {
                                "data_type": "timestamp",
                                "quantity_name": "Time",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "t",
                                "unit_abbrev": "s",
                                "id": "time",
                            },
                            {
                                "data_type": "sfloat",
                                "quantity_name": "Duration",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "Duration",
                                "unit_abbrev": "s",
                                "id": "duration",
                            },
                        ],
                        "id": "duration",
                    },
                    "parameters": {},
                    "min_time": 1648231560,
                    "max_time": 1648234860,
                    "id": "s2",
                },
            ],
            streams.to_list(),
        )

    @mock.patch("runeq.resources.stream_metadata.get_patient")
    def test_get_patient_streams_paginated(self, _):
        """
        Test filtering streams by all parameters, where the user has to
        page through streams.

        """
        self.mock_graph_client.execute = mock.Mock()
        self.mock_graph_client.execute.side_effect = [
            {
                "streamList": {
                    "pageInfo": {"endCursor": "test_check_next"},
                    "streams": [
                        {
                            "id": "s1",
                            "created_at": 1655226140.508,
                            "algorithm": "a1",
                            "device_id": "patient-p1,device-d1",
                            "patient_id": "p1",
                            "streamType": {
                                "id": "duration",
                                "name": "Duration",
                                "description": "Duration over time.",
                                "shape": {
                                    "dimensions": [
                                        {
                                            "id": "time",
                                            "data_type": "timestamp",
                                            "quantity_name": "Time",
                                            "quantity_abbrev": "t",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                    ]
                                },
                            },
                            "min_time": 1648231560,
                            "max_time": 1648234860,
                        },
                    ],
                }
            },
            {
                "streamList": {
                    "pageInfo": {"endCursor": None},
                    "streams": [
                        {
                            "id": "s2",
                            "created_at": 1655226140.501,
                            "algorithm": "a2",
                            "device_id": "patient-p2,device-d2",
                            "patient_id": "p1",
                            "streamType": {
                                "id": "duration",
                                "name": "Duration",
                                "description": "Duration over time.",
                                "shape": {
                                    "dimensions": [
                                        {
                                            "id": "time",
                                            "data_type": "timestamp",
                                            "quantity_name": "Time",
                                            "quantity_abbrev": "t",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                    ]
                                },
                            },
                            "min_time": 1648231560,
                            "max_time": 1648234860,
                        }
                    ],
                }
            },
        ]

        streams = get_patient_stream_metadata(
            patient_id="p1", client=self.mock_graph_client
        )

        self.assertEqual(
            [
                {
                    "created_at": 1655226140.508,
                    "algorithm": "a1",
                    "device_id": "d1",
                    "patient_id": "p1",
                    "stream_type": {
                        "name": "Duration",
                        "description": "Duration over time.",
                        "dimensions": [
                            {
                                "data_type": "timestamp",
                                "quantity_name": "Time",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "t",
                                "unit_abbrev": "s",
                                "id": "time",
                            },
                            {
                                "data_type": "sfloat",
                                "quantity_name": "Duration",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "Duration",
                                "unit_abbrev": "s",
                                "id": "duration",
                            },
                        ],
                        "id": "duration",
                    },
                    "parameters": {},
                    "min_time": 1648231560,
                    "max_time": 1648234860,
                    "id": "s1",
                },
                {
                    "created_at": 1655226140.501,
                    "algorithm": "a2",
                    "device_id": "d2",
                    "patient_id": "p1",
                    "stream_type": {
                        "name": "Duration",
                        "description": "Duration over time.",
                        "dimensions": [
                            {
                                "data_type": "timestamp",
                                "quantity_name": "Time",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "t",
                                "unit_abbrev": "s",
                                "id": "time",
                            },
                            {
                                "data_type": "sfloat",
                                "quantity_name": "Duration",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "Duration",
                                "unit_abbrev": "s",
                                "id": "duration",
                            },
                        ],
                        "id": "duration",
                    },
                    "parameters": {},
                    "min_time": 1648231560,
                    "max_time": 1648234860,
                    "id": "s2",
                },
            ],
            streams.to_list(),
        )

    def test_stream_set_filter(self):
        """
        Test filtering streams within a stream set.

        """
        stream_set = StreamMetadataSet(
            [
                StreamMetadata(
                    id="stream1",
                    created_at=123,
                    algorithm="alg1",
                    device_id="d1",
                    patient_id="p1",
                    stream_type=StreamType(
                        id="acceleration",
                        name="Acceleration",
                        description="Acceleration rate",
                        dimensions=[],
                    ),
                    min_time=10,
                    max_time=100,
                    parameters={},
                ),
                StreamMetadata(
                    id="stream2",
                    created_at=123,
                    algorithm="alg1",
                    device_id="d2",
                    patient_id="p1",
                    stream_type=StreamType(
                        id="acceleration",
                        name="Acceleration",
                        description="Acceleration rate",
                        dimensions=[],
                    ),
                    min_time=10,
                    max_time=100,
                    parameters={},
                ),
                StreamMetadata(
                    id="stream3",
                    created_at=123,
                    algorithm="alg1",
                    device_id="d1",
                    patient_id="p1",
                    stream_type=StreamType(
                        id="motion",
                        name="Motion",
                        description="Motion movement",
                        dimensions=[],
                    ),
                    min_time=10,
                    max_time=100,
                    parameters={},
                ),
            ]
        )

        device_streams = stream_set.filter(patient_id="p1", device_id="d1")
        self.assertEqual(2, len(device_streams))
        self.assertIsNotNone(device_streams.get("stream1"))
        self.assertIsNotNone(device_streams.get("stream3"))

        motion_streams = device_streams.filter(stream_type_id="motion")
        self.assertEqual(1, len(motion_streams))
        self.assertIsNotNone(motion_streams.get("stream3"))

        stream1_streams = stream_set.filter(
            filter_function=lambda stream: stream.id == "stream1"
        )
        self.assertEqual(1, len(stream1_streams))
        self.assertIsNotNone(stream1_streams.get("stream1"))

    def test_get_stream_dataframe(self):
        """
        Test get stream as dataframe with stream metadata and data.

        """
        self.mock_stream_client.get_data = mock.Mock()
        self.mock_stream_client.get_data.return_value = iter(
            [
                """time,acceleration,measurement_duration_ns
2022-07-28T14:26:45.167568Z,0.020525138825178146,20000000
2022-07-28T14:26:45.361596Z,0.020834974944591522,20000000
2022-07-28T14:26:45.361796Z,0.021182861179113388,20000000
2022-07-28T14:26:45.3618588Z,0.022172993049025536,20000000
2022-07-28T14:26:45.3620749Z,0.02356025017797947,20000000
2022-07-28T14:26:45.362149Z,0.024860087782144547,20000000
2022-07-28T14:26:45.36221Z,0.026072751730680466,20000000"""
            ]
        )

        self.mock_graph_client.execute = mock.Mock()
        self.mock_graph_client.execute.side_effect = [
            {
                "streamListByIds": {
                    "pageInfo": {"endCursor": None},
                    "streams": [
                        {
                            "id": "s1",
                            "created_at": 1655226140.508,
                            "algorithm": "a1",
                            "device_id": "patient-p1,device-d1",
                            "patient_id": "p1",
                            "streamType": {
                                "id": "duration",
                                "name": "Duration",
                                "description": "Duration over time.",
                                "shape": {
                                    "dimensions": [
                                        {
                                            "id": "time",
                                            "data_type": "timestamp",
                                            "quantity_name": "Time",
                                            "quantity_abbrev": "t",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                    ]
                                },
                            },
                            "min_time": 1648231560,
                            "max_time": 1648234860,
                        }
                    ],
                }
            }
        ]

        stream_df = get_stream_dataframe(
            stream_ids="s1",
            stream_client=self.mock_stream_client,
            graph_client=self.mock_graph_client,
        )

        self.assertEqual(
            {
                "time": {
                    "0": "2022-07-28T14:26:45.167568Z",
                    "1": "2022-07-28T14:26:45.361596Z",
                    "2": "2022-07-28T14:26:45.361796Z",
                    "3": "2022-07-28T14:26:45.3618588Z",
                    "4": "2022-07-28T14:26:45.3620749Z",
                    "5": "2022-07-28T14:26:45.362149Z",
                    "6": "2022-07-28T14:26:45.36221Z",
                },
                "acceleration": {
                    "0": 0.0205251388,
                    "1": 0.0208349749,
                    "2": 0.0211828612,
                    "3": 0.022172993,
                    "4": 0.0235602502,
                    "5": 0.0248600878,
                    "6": 0.0260727517,
                },
                "measurement_duration_ns": {
                    "0": 20000000,
                    "1": 20000000,
                    "2": 20000000,
                    "3": 20000000,
                    "4": 20000000,
                    "5": 20000000,
                    "6": 20000000,
                },
                "algorithm": {
                    "0": "a1",
                    "1": "a1",
                    "2": "a1",
                    "3": "a1",
                    "4": "a1",
                    "5": "a1",
                    "6": "a1",
                },
                "device_id": {
                    "0": "d1",
                    "1": "d1",
                    "2": "d1",
                    "3": "d1",
                    "4": "d1",
                    "5": "d1",
                    "6": "d1",
                },
                "patient_id": {
                    "0": "p1",
                    "1": "p1",
                    "2": "p1",
                    "3": "p1",
                    "4": "p1",
                    "5": "p1",
                    "6": "p1",
                },
                "stream_type_id": {
                    "0": "duration",
                    "1": "duration",
                    "2": "duration",
                    "3": "duration",
                    "4": "duration",
                    "5": "duration",
                    "6": "duration",
                },
                "stream_id": {
                    "0": "s1",
                    "1": "s1",
                    "2": "s1",
                    "3": "s1",
                    "4": "s1",
                    "5": "s1",
                    "6": "s1",
                },
            },
            json.loads(stream_df.to_json()),
        )

    def test_get_stream_dataframe_dicts(self):
        """
        Test that the stringified JSON of dict dimensions is unpacked in
        the dataframe representation

        """
        self.mock_stream_client.get_data = mock.Mock()
        self.mock_stream_client.get_data.return_value = iter(
            [
                """time,event,measurement_duration_ns
1648231560.000000,"{""hello"":""world""}",0
1648231565.000000,"{""rune"":""labs""}",0"""
            ]
        )

        self.mock_graph_client.execute = mock.Mock()
        self.mock_graph_client.execute.side_effect = [
            {
                "streamListByIds": {
                    "pageInfo": {"endCursor": None},
                    "streams": [
                        {
                            "id": "s1",
                            "created_at": 1655226140,
                            "algorithm": "a1",
                            "device_id": "patient-p1,device-d1",
                            "patient_id": "p1",
                            "streamType": {
                                "id": "event",
                                "name": "Event",
                                "description": "",
                                "shape": {
                                    "dimensions": [
                                        {
                                            "id": "time",
                                            "data_type": "timestamp",
                                            "quantity_name": "Time",
                                            "quantity_abbrev": "t",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                        {
                                            "data_type": "dict",
                                            "quantity_name": "Payload",
                                            "unit_name": "",
                                            "quantity_abbrev": "Payload",
                                            "unit_abbrev": "",
                                            "id": "event",
                                        },
                                    ]
                                },
                            },
                            "min_time": 1648231560,
                            "max_time": 1648231565,
                        }
                    ],
                }
            }
        ]

        stream_df = get_stream_dataframe(
            stream_ids="s1",
            stream_client=self.mock_stream_client,
            graph_client=self.mock_graph_client,
        )

        self.assertEqual(
            {
                "time": {
                    "0": 1648231560.0,
                    "1": 1648231565.0,
                },
                "event": {"0": {"hello": "world"}, "1": {"rune": "labs"}},
                "measurement_duration_ns": {"0": 0, "1": 0},
                "algorithm": {
                    "0": "a1",
                    "1": "a1",
                },
                "device_id": {
                    "0": "d1",
                    "1": "d1",
                },
                "patient_id": {
                    "0": "p1",
                    "1": "p1",
                },
                "stream_type_id": {
                    "0": "event",
                    "1": "event",
                },
                "stream_id": {
                    "0": "s1",
                    "1": "s1",
                },
            },
            json.loads(stream_df.to_json()),
        )

    def test_get_multiple_stream_dataframe(self):
        """
        Test get multiple streams as a dataframe

        """
        self.mock_stream_client.get_data = mock.Mock()
        self.mock_stream_client.get_data.side_effect = [
            iter(
                [
                    """time,acceleration,measurement_duration_ns
2022-07-28T14:26:45.167568Z,0.014469802379608154,20000000
2022-07-28T14:26:45.361596Z,0.03278458118438721,20000000
2022-07-28T14:26:45.361796Z,0.03711885213851929,20000000
2022-07-28T14:26:45.3618588Z,0.02531599998474121,20000000
2022-07-28T14:26:45.3620749Z,0.03168576955795288,20000000"""
                ]
            ),
            iter(
                [
                    """time,acceleration,measurement_duration_ns
2022-07-28T14:26:45.167568Z,0.020525138825178146,20000000
2022-07-28T14:26:45.361596Z,0.020834974944591522,20000000
2022-07-28T14:26:45.361796Z,0.021182861179113388,20000000
2022-07-28T14:26:45.3618588Z,0.022172993049025536,20000000
2022-07-28T14:26:45.3620749Z,0.02356025017797947,20000000"""
                ]
            ),
        ]

        self.mock_graph_client.execute = mock.Mock()
        self.mock_graph_client.execute.side_effect = [
            {
                "streamListByIds": {
                    "pageInfo": {"endCursor": "None"},
                    "streams": [
                        {
                            "id": "s1",
                            "created_at": 1659018576.73,
                            "algorithm": "a1",
                            "device_id": "patient-p1,device-d1",
                            "patient_id": "p1",
                            "streamType": {
                                "id": "acceleration",
                                "name": "Acceleration",
                                "description": "Acceleration sampled in time.",
                                "shape": {
                                    "dimensions": [
                                        {
                                            "id": "time",
                                            "data_type": "timestamp",
                                            "quantity_name": "Time",
                                            "quantity_abbrev": "t",
                                            "unit_name": "Nanoseconds",
                                            "unit_abbrev": "ns",
                                        },
                                        {
                                            "id": "acceleration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Acceleration",
                                            "quantity_abbrev": "Accel",
                                            "unit_name": "Gs",
                                            "unit_abbrev": "G",
                                        },
                                    ]
                                },
                            },
                            "parameters": [
                                {"key": "axis", "value": "z"},
                                {"key": "category", "value": "motion"},
                                {"key": "measurement", "value": "user"},
                            ],
                            "min_time": 1659018405.167568,
                            "max_time": 1659027683.492028,
                        },
                        {
                            "id": "s2",
                            "created_at": 1659018576.448,
                            "algorithm": "a1",
                            "device_id": "patient-p1,device-d1",
                            "patient_id": "p1",
                            "streamType": {
                                "id": "acceleration",
                                "name": "Acceleration",
                                "description": "Acceleration sampled in time.",
                                "shape": {
                                    "dimensions": [
                                        {
                                            "id": "time",
                                            "data_type": "timestamp",
                                            "quantity_name": "Time",
                                            "quantity_abbrev": "t",
                                            "unit_name": "Nanoseconds",
                                            "unit_abbrev": "ns",
                                        },
                                        {
                                            "id": "acceleration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Acceleration",
                                            "quantity_abbrev": "Accel",
                                            "unit_name": "Gs",
                                            "unit_abbrev": "G",
                                        },
                                    ]
                                },
                            },
                            "parameters": [
                                {"key": "axis", "value": "x"},
                                {"key": "category", "value": "motion"},
                                {"key": "measurement", "value": "gravity"},
                            ],
                            "min_time": 1659018405.167568,
                            "max_time": 1659027683.492028,
                        },
                    ],
                }
            }
        ]

        stream_df = get_stream_dataframe(
            stream_ids=["s1", "s2"],
            stream_client=self.mock_stream_client,
            graph_client=self.mock_graph_client,
        )

        self.assertEqual(
            {
                "time": {
                    "0": "2022-07-28T14:26:45.167568Z",
                    "1": "2022-07-28T14:26:45.361596Z",
                    "2": "2022-07-28T14:26:45.361796Z",
                    "3": "2022-07-28T14:26:45.3618588Z",
                    "4": "2022-07-28T14:26:45.3620749Z",
                    "5": "2022-07-28T14:26:45.167568Z",
                    "6": "2022-07-28T14:26:45.361596Z",
                    "7": "2022-07-28T14:26:45.361796Z",
                    "8": "2022-07-28T14:26:45.3618588Z",
                    "9": "2022-07-28T14:26:45.3620749Z",
                },
                "acceleration": {
                    "0": 0.0144698024,
                    "1": 0.0327845812,
                    "2": 0.0371188521,
                    "3": 0.025316,
                    "4": 0.0316857696,
                    "5": 0.0205251388,
                    "6": 0.0208349749,
                    "7": 0.0211828612,
                    "8": 0.0221729930,
                    "9": 0.0235602502,
                },
                "measurement_duration_ns": {
                    "0": 20000000,
                    "1": 20000000,
                    "2": 20000000,
                    "3": 20000000,
                    "4": 20000000,
                    "5": 20000000,
                    "6": 20000000,
                    "7": 20000000,
                    "8": 20000000,
                    "9": 20000000,
                },
                "algorithm": {
                    "0": "a1",
                    "1": "a1",
                    "2": "a1",
                    "3": "a1",
                    "4": "a1",
                    "5": "a1",
                    "6": "a1",
                    "7": "a1",
                    "8": "a1",
                    "9": "a1",
                },
                "device_id": {
                    "0": "d1",
                    "1": "d1",
                    "2": "d1",
                    "3": "d1",
                    "4": "d1",
                    "5": "d1",
                    "6": "d1",
                    "7": "d1",
                    "8": "d1",
                    "9": "d1",
                },
                "patient_id": {
                    "0": "p1",
                    "1": "p1",
                    "2": "p1",
                    "3": "p1",
                    "4": "p1",
                    "5": "p1",
                    "6": "p1",
                    "7": "p1",
                    "8": "p1",
                    "9": "p1",
                },
                "axis": {
                    "0": "z",
                    "1": "z",
                    "2": "z",
                    "3": "z",
                    "4": "z",
                    "5": "x",
                    "6": "x",
                    "7": "x",
                    "8": "x",
                    "9": "x",
                },
                "category": {
                    "0": "motion",
                    "1": "motion",
                    "2": "motion",
                    "3": "motion",
                    "4": "motion",
                    "5": "motion",
                    "6": "motion",
                    "7": "motion",
                    "8": "motion",
                    "9": "motion",
                },
                "measurement": {
                    "0": "user",
                    "1": "user",
                    "2": "user",
                    "3": "user",
                    "4": "user",
                    "5": "gravity",
                    "6": "gravity",
                    "7": "gravity",
                    "8": "gravity",
                    "9": "gravity",
                },
                "stream_type_id": {
                    "0": "acceleration",
                    "1": "acceleration",
                    "2": "acceleration",
                    "3": "acceleration",
                    "4": "acceleration",
                    "5": "acceleration",
                    "6": "acceleration",
                    "7": "acceleration",
                    "8": "acceleration",
                    "9": "acceleration",
                },
                "stream_id": {
                    "0": "s1",
                    "1": "s1",
                    "2": "s1",
                    "3": "s1",
                    "4": "s1",
                    "5": "s2",
                    "6": "s2",
                    "7": "s2",
                    "8": "s2",
                    "9": "s2",
                },
            },
            json.loads(stream_df.to_json()),
        )

    def test_get_stream_availability_dataframe(self):
        """
        Test get stream as dataframe with stream metadata and availability.

        """
        self.mock_stream_client.get_data = mock.Mock()
        self.mock_stream_client.get_data.return_value = iter(
            [
                """time,availability
2022-07-28T14:26:45.167568Z,1
2022-07-28T14:26:45.361596Z,1
2022-07-28T14:26:45.361796Z,0
2022-07-28T14:26:45.3618588Z,0
2022-07-28T14:26:45.3620749Z,0
2022-07-28T14:26:45.362149Z,1
2022-07-28T14:26:45.36221Z,1
"""
            ]
        )

        self.mock_graph_client.execute = mock.Mock()
        self.mock_graph_client.execute.side_effect = [
            {
                "streamListByIds": {
                    "pageInfo": {"endCursor": None},
                    "streams": [
                        {
                            "id": "s1",
                            "created_at": 1655226140.508,
                            "algorithm": "a1",
                            "device_id": "patient-p1,device-d1",
                            "patient_id": "p1",
                            "streamType": {
                                "id": "duration",
                                "name": "Duration",
                                "description": "Duration over time.",
                                "shape": {
                                    "dimensions": [
                                        {
                                            "id": "time",
                                            "data_type": "timestamp",
                                            "quantity_name": "Time",
                                            "quantity_abbrev": "t",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s",
                                        },
                                    ]
                                },
                            },
                            "min_time": 1648231560,
                            "max_time": 1648234860,
                        }
                    ],
                }
            }
        ]

        stream_df = get_stream_availability_dataframe(
            stream_ids="s1",
            start_time=123,
            end_time=345,
            resolution=300,
            stream_client=self.mock_stream_client,
            graph_client=self.mock_graph_client,
        )

        self.assertEqual(
            {
                "time": {
                    "0": "2022-07-28T14:26:45.167568Z",
                    "1": "2022-07-28T14:26:45.361596Z",
                    "2": "2022-07-28T14:26:45.361796Z",
                    "3": "2022-07-28T14:26:45.3618588Z",
                    "4": "2022-07-28T14:26:45.3620749Z",
                    "5": "2022-07-28T14:26:45.362149Z",
                    "6": "2022-07-28T14:26:45.36221Z",
                },
                "availability": {
                    "0": 1,
                    "1": 1,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                    "5": 1,
                    "6": 1,
                },
                "algorithm": {
                    "0": "a1",
                    "1": "a1",
                    "2": "a1",
                    "3": "a1",
                    "4": "a1",
                    "5": "a1",
                    "6": "a1",
                },
                "device_id": {
                    "0": "d1",
                    "1": "d1",
                    "2": "d1",
                    "3": "d1",
                    "4": "d1",
                    "5": "d1",
                    "6": "d1",
                },
                "patient_id": {
                    "0": "p1",
                    "1": "p1",
                    "2": "p1",
                    "3": "p1",
                    "4": "p1",
                    "5": "p1",
                    "6": "p1",
                },
                "stream_type_id": {
                    "0": "duration",
                    "1": "duration",
                    "2": "duration",
                    "3": "duration",
                    "4": "duration",
                    "5": "duration",
                    "6": "duration",
                },
                "stream_id": {
                    "0": "s1",
                    "1": "s1",
                    "2": "s1",
                    "3": "s1",
                    "4": "s1",
                    "5": "s1",
                    "6": "s1",
                },
            },
            json.loads(stream_df.to_json()),
        )

    def test_get_batch_stream_availability_dataframe(self):
        """
        Test get stream availability as dataframe with multiple stream results
        in a simplified dataframe without metadata.

        """
        self.mock_stream_client.get_data = mock.Mock()
        self.mock_stream_client.get_data.return_value = iter(
            [
                """time,availability
2022-07-28T14:26:45.167568Z,1
2022-07-28T14:26:45.361596Z,1
2022-07-28T14:26:45.361796Z,0
2022-07-28T14:26:45.3618588Z,0
2022-07-28T14:26:45.3620749Z,0
2022-07-28T14:26:45.362149Z,1
2022-07-28T14:26:45.36221Z,1
"""
            ]
        )

        stream_df = get_stream_availability_dataframe(
            stream_ids=["s1", "s2"],
            start_time=123,
            end_time=345,
            resolution=300,
            batch_operation="all",
            stream_client=self.mock_stream_client,
        )

        self.assertEqual(
            {
                "time": {
                    "0": "2022-07-28T14:26:45.167568Z",
                    "1": "2022-07-28T14:26:45.361596Z",
                    "2": "2022-07-28T14:26:45.361796Z",
                    "3": "2022-07-28T14:26:45.3618588Z",
                    "4": "2022-07-28T14:26:45.3620749Z",
                    "5": "2022-07-28T14:26:45.362149Z",
                    "6": "2022-07-28T14:26:45.36221Z",
                },
                "availability": {
                    "0": 1,
                    "1": 1,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                    "5": 1,
                    "6": 1,
                },
            },
            json.loads(stream_df.to_json()),
        )
