import os
from unittest import TestCase, mock

from runeq import Config

TEST_ROOT = os.path.dirname(os.path.realpath(__file__))


class TestConfig(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.access_token_good_config = f"{TEST_ROOT}/data/access_token_good_config.yaml"
        cls.access_token_bad_config = f"{TEST_ROOT}/data/access_token_bad_config.yaml"
        cls.client_keys_good_config = f"{TEST_ROOT}/data/client_keys_good_config.yaml"
        cls.client_keys_bad_config = f"{TEST_ROOT}/data/client_keys_bad_config.yaml"

    def test_init_file(self):
        """
        Test initializing using a yaml file
        """
        # Test access tokens init
        cfg = Config(self.access_token_good_config)
        expected = {
            "X-Rune-User-Access-Token-Id": "foo",
            "X-Rune-User-Access-Token-Secret": "bar",
        }
        self.assertEqual(expected, cfg.auth_headers)
        self.assertEqual(expected, cfg.access_token_auth_headers)

        with self.assertRaises(ValueError):
            _ = cfg.jwt_auth_headers

        with self.assertRaises(ValueError):
            _ = cfg.client_auth_headers

        # Test client keys init
        cfg = Config(self.client_keys_good_config)

        expected = {
            "X-Rune-Client-Key-ID": "abc",
            "X-Rune-Client-Access-Key": "def",
        }
        self.assertEqual(expected, cfg.auth_headers)
        self.assertEqual(expected, cfg.client_auth_headers)
        with self.assertRaises(ValueError):
            _ = cfg.jwt_auth_headers

        with self.assertRaises(ValueError):
            _ = cfg.access_token_auth_headers

        self.assertEqual("https://foo.runelabs.io", cfg.stream_url)

    def test_init_file_invalid(self):
        """
        Test initializing with an invalid YAML file
        """
        # Test invalid access token file
        with self.assertRaises(ValueError):
            Config(self.access_token_bad_config)

        # Test invalid client keys file
        with self.assertRaises(ValueError):
            Config(self.client_keys_bad_config)

    def test_init_kwargs(self):
        """
        Test initializing with valid kwargs
        """
        # access token
        cfg = Config(access_token_id="foo", access_token_secret="bar")
        access_token_headers = {
            "X-Rune-User-Access-Token-Id": "foo",
            "X-Rune-User-Access-Token-Secret": "bar",
        }
        self.assertEqual(access_token_headers, cfg.auth_headers)
        self.assertEqual(access_token_headers, cfg.access_token_auth_headers)
        with self.assertRaises(ValueError):
            _ = cfg.client_auth_headers

        with self.assertRaises(ValueError):
            _ = cfg.jwt_auth_headers

        # client keys
        cfg = Config(
            client_key_id="abc",
            client_access_key="123",
        )
        client_headers = {
            "X-Rune-Client-Key-ID": "abc",
            "X-Rune-Client-Access-Key": "123",
        }
        self.assertEqual(client_headers, cfg.auth_headers)
        self.assertEqual(client_headers, cfg.client_auth_headers)
        with self.assertRaises(ValueError):
            _ = cfg.jwt_auth_headers

        with self.assertRaises(ValueError):
            _ = cfg.access_token_auth_headers

        # jwt
        cfg = Config(jwt="abc123")
        jwt_headers = {"X-Rune-User-Access-Token": "abc123"}
        self.assertEqual(jwt_headers, cfg.auth_headers)
        self.assertEqual(jwt_headers, cfg.jwt_auth_headers)
        with self.assertRaises(ValueError):
            _ = cfg.client_auth_headers

        with self.assertRaises(ValueError):
            _ = cfg.access_token_auth_headers

        # cognito refresh token
        with mock.patch("runeq.config.boto3.client") as boto3_client:
            mock_cognito = mock.Mock()
            mock_cognito.initiate_auth.return_value = {
                "AuthenticationResult": {"AccessToken": "def456"}
            }
            boto3_client.return_value = mock_cognito

            cfg = Config(cognito_refresh_token="ref", cognito_client_id="cli")

        cognito_jwt_headers = {"X-Rune-User-Access-Token": "def456"}
        self.assertEqual(cognito_jwt_headers, cfg.auth_headers)
        self.assertEqual(cognito_jwt_headers, cfg.jwt_auth_headers)
        with self.assertRaises(ValueError):
            _ = cfg.client_auth_headers

        with self.assertRaises(ValueError):
            _ = cfg.access_token_auth_headers

    @mock.patch("runeq.config.boto3.client")
    def test_refresh_auth(self, mock_boto3):
        """Test that refresh_auth updates JWT value and returns a bool"""
        mock_cognito = mock.Mock()
        mock_cognito.initiate_auth.return_value = {
            "AuthenticationResult": {"AccessToken": "jwt1"}
        }
        mock_boto3.return_value = mock_cognito

        # refresh_auth returns False if the Config isn't using a refresh token
        for cfg in (
            Config(client_key_id="abc", client_access_key="123"),
            Config(access_token_id="foo", access_token_secret="bar"),
            Config(jwt="abc123"),
        ):
            self.assertFalse(cfg.refresh_auth())
            mock_cognito.initiate_auth.assert_not_called()

        # with a refresh token, initiate_auth is called once on init
        cfg = Config(cognito_refresh_token="ref", cognito_client_id="cli")
        self.assertEqual(mock_cognito.initiate_auth.call_count, 1)
        self.assertEqual(cfg.auth_headers, {"X-Rune-User-Access-Token": "jwt1"})

        # check that auth headers change after refreshing
        mock_cognito.initiate_auth.return_value = {
            "AuthenticationResult": {"AccessToken": "jwt2"}
        }
        self.assertTrue(cfg.refresh_auth())

        self.assertEqual(mock_cognito.initiate_auth.call_count, 2)
        self.assertEqual(cfg.auth_headers, {"X-Rune-User-Access-Token": "jwt2"})

    def test_init_kwargs_invalid(self):
        """
        Test initializing with invalid kwargs.

        """
        with self.assertRaises(ValueError):
            Config(client_key_id="abc")

        with self.assertRaises(ValueError):
            Config(client_access_key="123")

        with self.assertRaises(ValueError):
            Config(client_access_key="123", jwt="abc123")

        with self.assertRaises(ValueError):
            Config(access_token_id="foo")

        with self.assertRaises(ValueError):
            Config(access_token_id="foo", client_access_key="123")

        with self.assertRaises(ValueError):
            Config(access_token_id="foo", client_access_key="123", jwt="zee")

        with self.assertRaises(ValueError):
            Config(
                jwt="zee",
                cognito_client_id="foo",
                cognito_refresh_token="bar",
            )

    def test_init_invalid(self):
        """
        Cannot initialize with a filename and kwargs
        """
        with self.assertRaises(TypeError):
            Config(self.client_keys_good_config, stream_url="https://bar.runelabs.io")
