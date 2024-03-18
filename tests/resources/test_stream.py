"""
Tests for fetching stream data.

"""
from datetime import datetime, timezone
from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import StreamClient
from runeq.resources.stream import get_stream_availability, get_stream_data


class TestStreamData(TestCase):
    """
    Unit tests for the data queries in the Stream class.

    """

    def setUp(self):
        """
        Set up mock graph client for testing.

        """
        self.stream_client = StreamClient(
            Config(client_key_id="test", client_access_key="config")
        )
        self.maxDiff = None

    @mock.patch("runeq.resources.client.requests")
    def test_get_stream_data_csv(self, mock_requests):
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

        # Mock a paginated response
        mock_response1 = mock.Mock()
        mock_response1.ok = True
        mock_response1.headers = {"X-Rune-Next-Page-Token": "foobar"}
        mock_response1.text = expected_data

        mock_response2 = mock.Mock()
        mock_response2.ok = True
        mock_response2.headers = {}
        mock_response2.text = expected_data

        mock_requests.get.side_effect = [mock_response1, mock_response2]

        stream = get_stream_data(
            "test_stream_id",
            client=self.stream_client,
        )

        expected = [expected_data, expected_data]
        actual = list(stream)
        self.assertEqual(expected, actual)
        self.assertEqual(mock_requests.get.call_count, 2)

    @mock.patch("runeq.resources.client.requests")
    def test_get_stream_data_params(self, mock_requests):
        """
        Check the request construction for fetching stream data

        """
        # Mock an empty response - this test is just for the request
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.headers = {}
        mock_response.json.return_value = {}
        mock_requests.get.return_value = mock_response

        data = get_stream_data(
            "stream1",
            start_time=1691760000,
            end_time=1691762094.123,
            format="json",
            limit=10,
            page_token="page-token",
            timestamp="unix",
            timezone_name="America/Los_Angeles",
            translate_enums=False,
            client=self.stream_client,
        )
        # call list() to consume the iterator
        _ = list(data)

        expected_headers = {
            "X-Rune-Client-Key-ID": "test",
            "X-Rune-Client-Access-Key": "config",
        }

        mock_requests.get.assert_called_once_with(
            "https://stream.runelabs.io/v2/streams/stream1",
            headers=expected_headers,
            params={
                "start_time": 1691760000,
                "start_time_ns": None,
                "end_time": 1691762094.123,
                "end_time_ns": None,
                "format": "json",
                "limit": 10,
                "page_token": "page-token",
                "timestamp": "unix",
                "timezone": None,
                "timezone_name": "America/Los_Angeles",
                "translate_enums": False,
            },
        )

        mock_requests.get.reset_mock()

        # Test timestamp conversion
        data = get_stream_data(
            "stream2",
            start_time=datetime(2023, 8, 1, tzinfo=timezone.utc),
            end_time=datetime(2023, 8, 11, 10, 26, 45, 1, tzinfo=timezone.utc),
            client=self.stream_client,
        )
        # call list() to consume the iterator
        _ = list(data)

        mock_requests.get.assert_called_once_with(
            "https://stream.runelabs.io/v2/streams/stream2",
            headers=expected_headers,
            params={
                "start_time": 1690848000.0,
                "start_time_ns": None,
                "end_time": 1691749605.000001,
                "end_time_ns": None,
                "format": "csv",
                "limit": None,
                "page_token": None,
                "timestamp": "iso",
                "timezone": None,
                "timezone_name": None,
                "translate_enums": True,
            },
        )

    @mock.patch("runeq.resources.client.requests")
    def test_get_stream_data_json(self, mock_requests):
        """
        Test get a stream as json with specific stream_id and optional
        parameters.

        """
        expected_data = {
            "cardinality": 10,
            "data": {
                "acceleration": [
                    0.020525138825178146,
                    0.020834974944591522,
                    0.021182861179113388,
                    0.022172993049025536,
                    0.02356025017797947,
                    0.024860087782144547,
                    0.026072751730680466,
                    0.027338741347193718,
                    0.028795091435313225,
                    0.029819512739777565,
                ],
                "measurement_duration_ns": [
                    20000000,
                    20000000,
                    20000000,
                    20000000,
                    20000000,
                    20000000,
                    20000000,
                    20000000,
                    20000000,
                    20000000,
                ],
                "time": [
                    "2022-07-28T14:26:45.167568Z",
                    "2022-07-28T14:26:45.361596Z",
                    "2022-07-28T14:26:45.361796Z",
                    "2022-07-28T14:26:45.3618588Z",
                    "2022-07-28T14:26:45.3620749Z",
                    "2022-07-28T14:26:45.362149Z",
                    "2022-07-28T14:26:45.36221Z",
                    "2022-07-28T14:26:45.362269Z",
                    "2022-07-28T14:26:45.36234Z",
                    "2022-07-28T14:26:45.3624Z",
                ],
            },
        }

        # Mock a paginated response
        mock_response1 = mock.Mock()
        mock_response1.ok = True
        mock_response1.headers = {"X-Rune-Next-Page-Token": "foobar"}
        mock_response1.json.return_value = expected_data

        mock_response2 = mock.Mock()
        mock_response2.ok = True
        mock_response2.headers = {}
        mock_response2.json.return_value = expected_data

        mock_requests.get.side_effect = [mock_response1, mock_response2]

        stream = get_stream_data(
            "test_stream_id",
            format="json",
            client=self.stream_client,
        )

        expected = [expected_data, expected_data]
        actual = list(stream)
        self.assertEqual(expected, actual)

    @mock.patch("runeq.resources.client.requests")
    def test_get_stream_availability_csv(self, mock_requests):
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

        # Mock a paginated response
        mock_response1 = mock.Mock()
        mock_response1.ok = True
        mock_response1.headers = {"X-Rune-Next-Page-Token": "foobar"}
        mock_response1.text = expected_data

        mock_response2 = mock.Mock()
        mock_response2.ok = True
        mock_response2.headers = {}
        mock_response2.text = expected_data

        mock_requests.get.side_effect = [mock_response1, mock_response2]

        availability = get_stream_availability(
            stream_ids="test_stream_id",
            start_time=123,
            end_time=345,
            resolution=300,
            format="csv",
            client=self.stream_client,
        )

        expected = [expected_data, expected_data]
        actual = list(availability)
        self.assertEqual(expected, actual)

    @mock.patch("runeq.resources.client.requests")
    def test_get_stream_availability_json(self, mock_requests):
        """
        Test get a stream availability as json for a specific stream_id.

        """
        expected_data = {
            "data": {
                "time": [
                    "2022-07-28T14:25:00Z",
                    "2022-07-28T14:30:00Z",
                    "2022-07-28T14:35:00Z",
                    "2022-07-28T14:40:00Z",
                    "2022-07-28T14:45:00Z",
                    "2022-07-28T14:50:00Z",
                    "2022-07-28T14:55:00Z",
                    "2022-07-28T15:00:00Z",
                    "2022-07-28T15:05:00Z",
                    "2022-07-28T15:10:00Z",
                ],
                "availability": [1, 1, 0, 0, 1, 1, 0, 1, 1, 1],
            },
            "approx_available_duration_s": 3000,
            "cardinality": 10,
        }

        # Mock a paginated response
        mock_response1 = mock.Mock()
        mock_response1.ok = True
        mock_response1.headers = {"X-Rune-Next-Page-Token": "foobar"}
        mock_response1.json.return_value = expected_data

        mock_response2 = mock.Mock()
        mock_response2.ok = True
        mock_response2.headers = {}
        mock_response2.json.return_value = expected_data

        mock_requests.get.side_effect = [mock_response1, mock_response2]

        availability = get_stream_availability(
            stream_ids="test_stream_id",
            start_time=123,
            end_time=345,
            resolution=300,
            format="json",
            client=self.stream_client,
        )

        expected = [expected_data, expected_data]
        actual = list(availability)
        self.assertEqual(expected, actual)

    @mock.patch("runeq.resources.client.requests")
    def test_get_batch_stream_availability(self, mock_requests):
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

        # Mock a paginated response
        mock_response1 = mock.Mock()
        mock_response1.ok = True
        mock_response1.headers = {"X-Rune-Next-Page-Token": "foobar"}
        mock_response1.text = expected_data

        mock_response2 = mock.Mock()
        mock_response2.ok = True
        mock_response2.headers = {}
        mock_response2.text = expected_data

        mock_requests.get.side_effect = [mock_response1, mock_response2]

        # Must include batch_operation when querying >1 stream
        with self.assertRaisesRegex(ValueError, "batch_operation must be specified"):
            get_stream_availability(
                stream_ids=["test_stream_id1", "test_stream_id2"],
                start_time=123,
                end_time=345,
                resolution=300,
                format="csv",
                client=self.stream_client,
            ).__next__()

        availability = get_stream_availability(
            stream_ids=["test_stream_id1", "test_stream_id2"],
            start_time=123,
            end_time=345,
            resolution=300,
            batch_operation="all",
            client=self.stream_client,
        )

        expected = [expected_data, expected_data]
        actual = list(availability)
        self.assertEqual(expected, actual)
