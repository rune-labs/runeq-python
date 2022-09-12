"""
Tests for the V2 SDK Stream.

"""
from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import GraphClient
from runeq.resources.stream import get_stream_availability, get_stream_data


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

    def test_get_stream_data(self):
        """
        Test get a stream with specific stream_id and optional parameters.

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

        stream = get_stream_data('test_stream_id', client=self.mock_client)

        self.assertEqual(
            expected_data,
            stream.__next__()
        )

        self.assertEqual(
            expected_data,
            stream.__next__()
        )

    def test_get_stream_availability(self):
        """
        Test get a stream availability for a specific stream_id.

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

        availability = get_stream_availability(
            stream_id='test_stream_id',
            start_time=123,
            end_time=345,
            resolution=300,
            client=self.mock_client
        )

        self.assertEqual(
            expected_data,
            availability.__next__()
        )

        self.assertEqual(
            expected_data,
            availability.__next__()
        )

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

        self.assertEqual(
            expected_data,
            availability.__next__()
        )

        self.assertEqual(
            expected_data,
            availability.__next__()
        )
