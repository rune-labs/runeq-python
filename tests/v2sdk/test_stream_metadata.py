"""
Tests for the V2 SDK Stream.

"""
import json
from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import GraphClient, StreamClient
from runeq.resources.stream_metadata import (
    Dimension, StreamMetadata, StreamMetadataSet, StreamType,
    get_patient_stream_metadata, get_all_stream_types,
    get_stream_availability_dataframe, get_stream_dataframe,
    get_stream_metadata
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
            Config(
                client_key_id='test',
                client_access_key='config'
            )
        )

    def test_attributes(self):
        """
        Test attributes for an initialized Stream.

        """
        test_stream_type = StreamType(
            id="rotation",
            name="Rotation",
            description="Rotation rate (velocity) sampled in the time-domain.",
            dimensions=[]
        )

        self.assertEqual("rotation", test_stream_type.id)
        self.assertEqual("Rotation", test_stream_type.name)
        self.assertEqual(
            "Rotation rate (velocity) sampled in the time-domain.",
            test_stream_type.description
        )
        self.assertEqual([], test_stream_type.dimensions)

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
                                        "unit_abbrev": "ns"
                                    },
                                    {
                                        "id": "rotation",
                                        "data_type": "sfloat",
                                        "quantity_name": "Angular Velocity",
                                        "quantity_abbrev": "Rotation",
                                        "unit_name": "Radians per second",
                                        "unit_abbrev": "rps"
                                    }
                                ]
                            }
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
                                        "unit_abbrev": "ns"
                                    },
                                    {
                                        "id": "current",
                                        "data_type": "sfloat",
                                        "quantity_name": "Current",
                                        "quantity_abbrev": "I",
                                        "unit_name": "Amps",
                                        "unit_abbrev": "A"
                                    }
                                ]
                            }
                        }
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
                            "unit_abbrev": "ns"
                        },
                        {
                            "id": "rotation",
                            "data_type": "sfloat",
                            "quantity_name": "Angular Velocity",
                            "quantity_abbrev": "Rotation",
                            "unit_name": "Radians per second",
                            "unit_abbrev": "rps"
                        }
                    ]
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
                            "unit_abbrev": "ns"
                        },
                        {
                            "id": "current",
                            "data_type": "sfloat",
                            "quantity_name": "Current",
                            "quantity_abbrev": "I",
                            "unit_name": "Amps",
                            "unit_abbrev": "A"
                        }
                    ]
                }
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
            Config(
                client_key_id='test',
                client_access_key='config'
            )
        )

        self.mock_stream_client = StreamClient(
            Config(
                client_key_id='test',
                client_access_key='config'
            )
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
            max_time=1648234860
        )

        self.assertEqual("s1", test_stream.id)
        self.assertEqual(1629300943.9179766, test_stream.created_at)
        self.assertEqual("a1", test_stream.algorithm)
        self.assertEqual("d1", test_stream.device_id)
        self.assertEqual("p1", test_stream.patient_id)
        self.assertEqual(test_stream_type, test_stream.stream_type)
        self.assertEqual(1648231560, test_stream.min_time)
        self.assertEqual(1648234860, test_stream.max_time)

    def test_get_stream_metadata(self):
        """
        Test getting stream metadata.

        """
        self.mock_graph_client.execute = mock.Mock()
        self.mock_graph_client.execute.side_effect = [
            {
                "streamListByIds": {
                    "pageInfo": {
                        "endCursor": None
                    },
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
                                            "unit_abbrev": "s"
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s"
                                        }
                                    ]
                                }
                            },
                            "min_time": 1648231560,
                            "max_time": 1648234860
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
                                            "unit_abbrev": "s"
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s"
                                        }
                                    ]
                                }
                            },
                            "min_time": 1648231560,
                            "max_time": 1648234860
                        }
                    ]
                }
            }
        ]

        streams = get_stream_metadata(
            stream_id=["s1", "s2"],
            client=self.mock_graph_client
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
                                "id": "time"
                            },
                            {
                                "data_type": "sfloat",
                                "quantity_name": "Duration",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "Duration",
                                "unit_abbrev": "s",
                                "id": "duration"
                            }
                        ],
                        "id": "duration"
                    },
                    "min_time": 1648231560,
                    "max_time": 1648234860,
                    "id": "s1"
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
                                "id": "time"
                            },
                            {
                                "data_type": "sfloat",
                                "quantity_name": "Duration",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "Duration",
                                "unit_abbrev": "s",
                                "id": "duration"
                            }
                        ],
                        "id": "duration"
                    },
                    "min_time": 1648231560,
                    "max_time": 1648234860,
                    "id": "s2"
                }
            ],
            streams.to_list(),
        )


    def test_get_patient_streams_basic(self):
        """
        Test filtering streams by all parameters.

        """
        self.mock_graph_client.execute = mock.Mock()
        self.mock_graph_client.execute.side_effect = [
            {
                "streamList": {
                    "pageInfo": {
                        "endCursor": None
                    },
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
                                            "unit_abbrev": "s"
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s"
                                        }
                                    ]
                                }
                            },
                            "parameters": [
                                {
                                    "key": "category",
                                    "value": "motion"
                                },
                                {
                                    "key": "measurement",
                                    "value": "walking"
                                }
                            ],
                            "min_time": 1648231560,
                            "max_time": 1648234860
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
                                            "unit_abbrev": "s"
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s"
                                        }
                                    ]
                                }
                            },
                            "min_time": 1648231560,
                            "max_time": 1648234860
                        }
                    ]
                }
            }
        ]

        streams = get_patient_stream_metadata(
            patient_id="p1",
            client=self.mock_graph_client
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
                                "id": "time"
                            },
                            {
                                "data_type": "sfloat",
                                "quantity_name": "Duration",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "Duration",
                                "unit_abbrev": "s",
                                "id": "duration"
                            }
                        ],
                        "id": "duration"
                    },
                    "category": "motion",
                    "measurement": "walking",
                    "min_time": 1648231560,
                    "max_time": 1648234860,
                    "id": "s1"
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
                                "id": "time"
                            },
                            {
                                "data_type": "sfloat",
                                "quantity_name": "Duration",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "Duration",
                                "unit_abbrev": "s",
                                "id": "duration"
                            }
                        ],
                        "id": "duration"
                    },
                    "min_time": 1648231560,
                    "max_time": 1648234860,
                    "id": "s2"
                }
            ],
            streams.to_list(),
        )


    def test_get_patient_streams_paginated(self):
        """
        Test filtering streams by all parameters, where the user has to
        page through streams.

        """
        self.mock_graph_client.execute = mock.Mock()
        self.mock_graph_client.execute.side_effect = [
            {
                "streamList": {
                    "pageInfo": {
                        "endCursor": "test_check_next"
                    },
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
                                            "unit_abbrev": "s"
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s"
                                        }
                                    ]
                                }
                            },
                            "min_time": 1648231560,
                            "max_time": 1648234860
                        },
                    ]
                }
            },
            {
                "streamList": {
                    "pageInfo": {
                        "endCursor": None
                    },
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
                                            "unit_abbrev": "s"
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s"
                                        }
                                    ]
                                }
                            },
                            "min_time": 1648231560,
                            "max_time": 1648234860
                        }
                    ]
                }
            }
        ]

        streams = get_patient_stream_metadata(
            patient_id="p1",
            client=self.mock_graph_client
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
                                "id": "time"
                            },
                            {
                                "data_type": "sfloat",
                                "quantity_name": "Duration",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "Duration",
                                "unit_abbrev": "s",
                                "id": "duration"
                            }
                        ],
                        "id": "duration"
                    },
                    "min_time": 1648231560,
                    "max_time": 1648234860,
                    "id": "s1"
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
                                "id": "time"
                            },
                            {
                                "data_type": "sfloat",
                                "quantity_name": "Duration",
                                "unit_name": "Seconds",
                                "quantity_abbrev": "Duration",
                                "unit_abbrev": "s",
                                "id": "duration"
                            }
                        ],
                        "id": "duration"
                    },
                    "min_time": 1648231560,
                    "max_time": 1648234860,
                    "id": "s2"
                }
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
                        dimensions=[]
                    ),
                    min_time=10,
                    max_time=100,
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
                        dimensions=[]
                    ),
                    min_time=10,
                    max_time=100,
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
                        dimensions=[]
                    ),
                    min_time=10,
                    max_time=100,
                ),
            ]
        )

        device_streams = stream_set.filter(
            patient_id="p1",
            device_id="d1"
        )
        self.assertEqual(2, len(device_streams))
        self.assertIsNotNone(device_streams.get("stream1"))
        self.assertIsNone(device_streams.get("stream2"))
        self.assertIsNotNone(device_streams.get("stream3"))

        motion_streams = device_streams.filter(
            stream_type_id="motion"
        )
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
                    "pageInfo": {
                        "endCursor": None
                    },
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
                                            "unit_abbrev": "s"
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s"
                                        }
                                    ]
                                }
                            },
                            "min_time": 1648231560,
                            "max_time": 1648234860
                        }
                    ]
                }
            }
        ]

        stream_df = get_stream_dataframe(
            stream_id="s1",
            stream_client=self.mock_stream_client,
            graph_client=self.mock_graph_client
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
                    "6": "2022-07-28T14:26:45.36221Z"
                },
                "acceleration": {
                    "0": 0.0205251388,
                    "1": 0.0208349749,
                    "2": 0.0211828612,
                    "3": 0.022172993,
                    "4": 0.0235602502,
                    "5": 0.0248600878,
                    "6": 0.0260727517
                },
                "measurement_duration_ns": {
                    "0": 20000000,
                    "1": 20000000,
                    "2": 20000000,
                    "3": 20000000,
                    "4": 20000000,
                    "5": 20000000,
                    "6": 20000000
                },
                "created_at": {
                    "0": 1655226140.507999897,
                    "1": 1655226140.507999897,
                    "2": 1655226140.507999897,
                    "3": 1655226140.507999897,
                    "4": 1655226140.507999897,
                    "5": 1655226140.507999897,
                    "6": 1655226140.507999897
                },
                "algorithm": {
                    "0": "a1",
                    "1": "a1",
                    "2": "a1",
                    "3": "a1",
                    "4": "a1",
                    "5": "a1",
                    "6": "a1"
                },
                "device_id": {
                    "0": "d1",
                    "1": "d1",
                    "2": "d1",
                    "3": "d1",
                    "4": "d1",
                    "5": "d1",
                    "6": "d1"
                },
                "patient_id": {
                    "0": "p1",
                    "1": "p1",
                    "2": "p1",
                    "3": "p1",
                    "4": "p1",
                    "5": "p1",
                    "6": "p1"
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
                    "6": "s1"
                }
            },
            json.loads(stream_df.to_json())
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
                    "pageInfo": {
                        "endCursor": None
                    },
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
                                            "unit_abbrev": "s"
                                        },
                                        {
                                            "id": "duration",
                                            "data_type": "sfloat",
                                            "quantity_name": "Duration",
                                            "quantity_abbrev": "Duration",
                                            "unit_name": "Seconds",
                                            "unit_abbrev": "s"
                                        }
                                    ]
                                }
                            },
                            "min_time": 1648231560,
                            "max_time": 1648234860
                        }
                    ]
                }
            }
        ]

        stream_df = get_stream_availability_dataframe(
            stream_id="s1",
            start_time=123,
            end_time=345,
            resolution=300,
            stream_client=self.mock_stream_client,
            graph_client=self.mock_graph_client
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
                    "6": "2022-07-28T14:26:45.36221Z"
                },
                "availability": {
                    "0": 1,
                    "1": 1,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                    "5": 1,
                    "6": 1
                },
                "created_at": {
                    "0": 1655226140.507999897,
                    "1": 1655226140.507999897,
                    "2": 1655226140.507999897,
                    "3": 1655226140.507999897,
                    "4": 1655226140.507999897,
                    "5": 1655226140.507999897,
                    "6": 1655226140.507999897
                },
                "algorithm": {
                    "0": "a1",
                    "1": "a1",
                    "2": "a1",
                    "3": "a1",
                    "4": "a1",
                    "5": "a1",
                    "6": "a1"
                },
                "device_id": {
                    "0": "d1",
                    "1": "d1",
                    "2": "d1",
                    "3": "d1",
                    "4": "d1",
                    "5": "d1",
                    "6": "d1"
                },
                "patient_id": {
                    "0": "p1",
                    "1": "p1",
                    "2": "p1",
                    "3": "p1",
                    "4": "p1",
                    "5": "p1",
                    "6": "p1"
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
                    "6": "s1"
                }
            },
            json.loads(stream_df.to_json())
        )
