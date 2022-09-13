"""
Tests for the V2 SDK Stream.

"""
from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import GraphClient
from runeq.resources.stream import (
    get_stream_availability, get_stream_availability_csv,
    get_stream_availability_json, get_stream_csv, get_stream_json
)


class TestStreamData(TestCase):
    """
    Unit tests for the data queries in the Stream class.

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
        self.maxDiff = None

    def test_get_stream_data_csv(self):
        """
        Test get a stream as csv with specific stream_id and optional
        parameters.

        """
        expected_data = """time,acceleration,measurement_duration_ns
2022-07-28T14:26:45.167568Z,0.020525138825178146,20000000
2022-07-28T14:26:45.361596Z,0.020834974944591522,20000000
2022-07-28T14:26:45.361796Z,0.021182861179113388,20000000
2022-07-28T14:26:45.3618588Z,0.022172993049025536,20000000
2022-07-28T14:26:45.3620749Z,0.02356025017797947,20000000
2022-07-28T14:26:45.362149Z,0.024860087782144547,20000000
2022-07-28T14:26:45.36221Z,0.026072751730680466,20000000"""

        self.mock_client.get_data = mock.Mock()
        self.mock_client.get_data.return_value = iter(
            [
                expected_data,
                expected_data
            ]
        )

        stream = get_stream_csv('test_stream_id', client=self.mock_client)

        expected = [expected_data, expected_data]
        actual = list(stream)
        self.assertEqual(expected, actual)

    def test_get_stream_data_json(self):
        """
        Test get a stream as json with specific stream_id and optional
        parameters.

        """
        expected_data = """{
   "cardinality":10,
   "data":{
      "acceleration":[
         0.020525138825178146,
         0.020834974944591522,
         0.021182861179113388,
         0.022172993049025536,
         0.02356025017797947,
         0.024860087782144547,
         0.026072751730680466,
         0.027338741347193718,
         0.028795091435313225,
         0.029819512739777565
      ],
      "measurement_duration_ns":[
         20000000,
         20000000,
         20000000,
         20000000,
         20000000,
         20000000,
         20000000,
         20000000,
         20000000,
         20000000
      ],
      "time":[
         "2022-07-28T14:26:45.167568Z",
         "2022-07-28T14:26:45.361596Z",
         "2022-07-28T14:26:45.361796Z",
         "2022-07-28T14:26:45.3618588Z",
         "2022-07-28T14:26:45.3620749Z",
         "2022-07-28T14:26:45.362149Z",
         "2022-07-28T14:26:45.36221Z",
         "2022-07-28T14:26:45.362269Z",
         "2022-07-28T14:26:45.36234Z",
         "2022-07-28T14:26:45.3624Z"
      ]
   }
}"""

        self.mock_client.get_data = mock.Mock()
        self.mock_client.get_data.return_value = iter(
            [
                expected_data,
                expected_data
            ]
        )

        stream = get_stream_json('test_stream_id', client=self.mock_client)

        expected = [expected_data, expected_data]
        actual = list(stream)
        self.assertEqual(expected, actual)

    def test_get_stream_availability_csv(self):
        """
        Test get a stream availability as csv for a specific stream_id.

        """
        expected_data = """time,availability
2022-07-28T14:26:45.167568Z,1
2022-07-28T14:26:45.361596Z,1
2022-07-28T14:26:45.361796Z,0
2022-07-28T14:26:45.3618588Z,0
2022-07-28T14:26:45.3620749Z,0
2022-07-28T14:26:45.362149Z,1
2022-07-28T14:26:45.36221Z,1
"""

        self.mock_client.get_data = mock.Mock()
        self.mock_client.get_data.return_value = iter(
            [
                expected_data,
                expected_data
            ]
        )

        availability = get_stream_availability_csv(
            stream_id='test_stream_id',
            start_time=123,
            end_time=345,
            resolution=300,
            client=self.mock_client
        )

        expected = [expected_data, expected_data]
        actual = list(availability)
        self.assertEqual(expected, actual)

    def test_get_stream_availability_json(self):
        """
        Test get a stream availability as json for a specific stream_id.

        """
        expected_data = """{
   "data":{
      "time":[
         "2022-07-28T14:25:00Z",
         "2022-07-28T14:30:00Z",
         "2022-07-28T14:35:00Z",
         "2022-07-28T14:40:00Z",
         "2022-07-28T14:45:00Z",
         "2022-07-28T14:50:00Z",
         "2022-07-28T14:55:00Z",
         "2022-07-28T15:00:00Z",
         "2022-07-28T15:05:00Z",
         "2022-07-28T15:10:00Z"
      ],
      "availability":[
         1,
         1,
         0,
         0,
         1,
         1,
         0,
         1,
         1,
         1
      ]
   },
   "approx_available_duration_s":3000,
   "cardinality":10
}
"""

        self.mock_client.get_data = mock.Mock()
        self.mock_client.get_data.return_value = iter(
            [
                expected_data,
                expected_data
            ]
        )

        availability = get_stream_availability_json(
            stream_id='test_stream_id',
            start_time=123,
            end_time=345,
            resolution=300,
            client=self.mock_client
        )

        expected = [expected_data, expected_data]
        actual = list(availability)
        self.assertEqual(expected, actual)

    def test_get_batch_stream_availability(self):
        """
        Test get batch stream availability for multiple stream_ids.

        """
        expected_data = """time,availability
2022-07-28T14:26:45.167568Z,1
2022-07-28T14:26:45.361596Z,1
2022-07-28T14:26:45.361796Z,0
2022-07-28T14:26:45.3618588Z,0
2022-07-28T14:26:45.3620749Z,0
2022-07-28T14:26:45.362149Z,1
2022-07-28T14:26:45.36221Z,1
"""

        self.mock_client.get_data = mock.Mock()
        self.mock_client.get_data.return_value = iter(
            [
                expected_data,
                expected_data
            ]
        )

        # Must include batch_operation when querying >1 stream
        with self.assertRaisesRegex(
            ValueError,
            "batch_operation must be specified"
        ):
            get_stream_availability(
                stream_id=['test_stream_id1', 'test_stream_id2'],
                start_time=123,
                end_time=345,
                resolution=300,
                client=self.mock_client
            ).__next__()

        availability = get_stream_availability(
            stream_id=['test_stream_id1', 'test_stream_id2'],
            start_time=123,
            end_time=345,
            resolution=300,
            batch_operation="all",
            client=self.mock_client
        )

        expected = [expected_data, expected_data]
        actual = list(availability)
        self.assertEqual(expected, actual)
