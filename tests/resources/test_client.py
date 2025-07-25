"""
Tests for the V2 SDK Client.

"""

from unittest import TestCase, mock

from runeq import errors
from runeq.config import BaseConfig
from runeq.resources.client import (
    GraphClient,
    StreamClient,
    StriveClient,
    global_graph_client,
    global_stream_client,
    global_strive_client,
    initialize,
    initialize_with_config,
)
from runeq.resources.stream import get_stream_data


class TestInitialize(TestCase):
    """
    Unit tests for the initialization of the user's credentials.

    """

    def test_init_invalid(self):
        """
        Test that access is restricted with no initialization.

        """
        with self.assertRaises(errors.InitializationError):
            get_stream_data("stream_id").__next__()

    def test_init_with_access_keys(self):
        """
        Test that the user is initialized but with invalid access keys.

        """
        initialize(
            access_token_id="foo",
            access_token_secret="bar",
        )

        with self.assertRaisesRegex(errors.APIError, "401 InvalidAuthentication"):
            get_stream_data("stream_id").__next__()

    def test_init_with_client_keys(self):
        """
        Test that the user is initialized but with invalid client keys.

        """
        initialize(
            client_key_id="foo",
            client_access_key="bar",
        )

        with self.assertRaisesRegex(errors.APIError, "401 InvalidAuthentication"):
            get_stream_data("stream_id").__next__()

    def test_initialize_with_config(self):
        """
        Test initializing with a config object.

        """
        config = mock.Mock(spec=BaseConfig)
        config.graph_url = "graph-url"
        config.stream_url = "stream-url"
        config.strive_url = "strive_url"
        config.auth_headers = {"hello": "world"}

        initialize_with_config(config)

        graph_client = global_graph_client()
        stream_client = global_stream_client()
        strive_config = global_strive_client()

        self.assertIs(graph_client.config, config)
        self.assertIs(stream_client.config, config)
        self.assertIs(strive_config.config, config)


class TestStreamClient(TestCase):
    """
    Unit tests for StreamClient

    """

    def _setup_mock_response(self, status_code, json_body):
        """Set up a mock response"""
        mock_response = mock.Mock()
        mock_response.ok = False
        mock_response.status_code = status_code
        mock_response.json.return_value = json_body
        return mock_response

    @mock.patch("runeq.resources.client.requests.get")
    def test_get_successful(self, mock_get):
        """Test successful request with get() method"""
        config = mock.Mock(spec=BaseConfig)
        config.stream_url = "https://stream.example.com"
        config.auth_headers = {"X-Auth": "token"}

        stream_client = StreamClient(config)

        # Set up successful response
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"data": "test_data"}
        mock_get.return_value = mock_response

        response = stream_client.get("/v2/streams/123", {"param1": "value1"})

        self.assertEqual(response, mock_response)

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "https://stream.example.com/v2/streams/123",
            headers={"X-Auth": "token"},
            params={"param1": "value1"},
        )

    def test_get_path_validation(self):
        """Test path validation in get() method"""
        config = mock.Mock(spec=BaseConfig)
        config.stream_url = "https://stream.example.com"

        stream_client = StreamClient(config)

        # Test with invalid path
        with self.assertRaises(ValueError):
            stream_client.get("/invalid/path", {})

    @mock.patch("runeq.resources.client.requests.get")
    def test_refresh_auth_on_4xx(self, mock_get):
        """If a request fails with a 4xx status code, refresh auth and retry"""
        config = mock.Mock(spec=BaseConfig)
        config.stream_url = ""
        config.refresh_auth.return_value = True

        stream_client = StreamClient(config)

        mock_response = self._setup_mock_response(400, {"error": "auth error"})
        mock_get.return_value = mock_response

        with self.assertRaises(errors.APIError):
            list(stream_client.get_data("/v2/streams/123"))

        self.assertEqual(mock_get.call_count, 2)
        config.refresh_auth.assert_called_once()

    @mock.patch("runeq.resources.client.requests.get")
    def test_no_retry_on_5xx(self, mock_get):
        """If a request fails with a 5xx status code, do not retry"""
        config = mock.Mock(spec=BaseConfig)
        config.stream_url = ""
        config.refresh_auth.return_value = True

        stream_client = StreamClient(config)

        mock_response = self._setup_mock_response(500, {"error": "internal"})
        mock_get.return_value = mock_response

        with self.assertRaises(errors.APIError):
            list(stream_client.get_data("/v2/streams/123"))

        self.assertEqual(mock_get.call_count, 1)
        config.refresh_auth.assert_not_called()


class TestGraphClient(TestCase):
    """
    Unit tests for GraphClient

    """

    @mock.patch("runeq.resources.client.GQLClient")
    def test_refresh_auth_on_error(self, mock_client_cls):
        """If a request fails with any error, refresh auth and retry"""
        config = mock.Mock(spec=BaseConfig)
        config.graph_url = ""
        config.auth_headers = {"hello": "world"}

        graph_client = GraphClient(config)

        mock_execute = mock_client_cls().execute
        excecute_err = ValueError("test exception")
        mock_execute.side_effect = excecute_err

        with self.assertRaisesRegex(ValueError, "test exception"):
            graph_client.execute("query fakeQuery($input: Input) { id }")

        self.assertEqual(mock_execute.call_count, 2)
        config.refresh_auth.assert_called_once()


class TestStriveClient(TestCase):
    """
    Unit tests for StriveClient

    """

    @mock.patch("runeq.resources.client.requests.get")
    def test_get_successful(self, mock_get):
        """Test successful GET request with get() method"""
        config = mock.Mock(spec=BaseConfig)
        config.strive_url = "https://strive.example.com"
        config.auth_headers = {"X-Auth": "token"}

        strive_client = StriveClient(config)

        # Set up successful response
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"data": "test_data"}
        mock_get.return_value = mock_response

        response = strive_client.get("/api/endpoint", param1="value1")

        self.assertEqual(response, mock_response)

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "https://strive.example.com/api/endpoint",
            headers={"X-Auth": "token"},
            param1="value1",
        )

    @mock.patch("runeq.resources.client.requests.post")
    def test_post_successful(self, mock_post):
        """Test successful POST request with post() method"""
        config = mock.Mock(spec=BaseConfig)
        config.strive_url = "https://strive.example.com"
        config.auth_headers = {"X-Auth": "token"}

        strive_client = StriveClient(config)

        # Set up successful response
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        test_json = {"key": "value"}
        response = strive_client.post("/api/endpoint", json=test_json)

        self.assertEqual(response, mock_response)

        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            "https://strive.example.com/api/endpoint",
            headers={"X-Auth": "token"},
            json=test_json,
        )

    @mock.patch("runeq.resources.client.requests.patch")
    def test_patch_successful(self, mock_patch):
        """Test successful PATCH request with patch() method"""
        config = mock.Mock(spec=BaseConfig)
        config.strive_url = "https://strive.example.com"
        config.auth_headers = {"X-Auth": "token"}

        strive_client = StriveClient(config)

        # Set up successful response
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"updated": True}
        mock_patch.return_value = mock_response

        test_json = {"updated_field": "new_value"}
        response = strive_client.patch("/api/endpoint", json=test_json)

        self.assertEqual(response, mock_response)

        # Verify the request was made correctly
        mock_patch.assert_called_once_with(
            "https://strive.example.com/api/endpoint",
            headers={"X-Auth": "token"},
            json=test_json,
        )
