import os
from unittest import TestCase

from runeq import Config

TEST_ROOT = os.path.dirname(os.path.realpath(__file__))


class TestConfig(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.access_token_good_config = (
            f'{TEST_ROOT}/data/access_token_good_config.yaml'
        )
        cls.access_token_bad_config = (
            f'{TEST_ROOT}/data/access_token_bad_config.yaml'
        )
        cls.client_keys_good_config = (
            f'{TEST_ROOT}/data/client_keys_good_config.yaml'
        )
        cls.client_keys_bad_config = (
            f'{TEST_ROOT}/data/client_keys_bad_config.yaml'
        )

    def test_init_file(self):
        """
        Test initializing using a yaml file
        """
        # Test access tokens init
        cfg = Config(self.access_token_good_config)
        expected = {
            'X-Rune-User-Access-Token-Id': 'foo',
            'X-Rune-User-Access-Token-Secret': 'bar',
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
            'X-Rune-Client-Key-ID': 'abc',
            'X-Rune-Client-Access-Key': 'def',
        }
        self.assertEqual(expected, cfg.auth_headers)
        self.assertEqual(expected, cfg.client_auth_headers)
        with self.assertRaises(ValueError):
            _ = cfg.jwt_auth_headers

        with self.assertRaises(ValueError):
            _ = cfg.access_token_auth_headers

        self.assertEqual('https://foo.runelabs.io', cfg.stream_url)

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
        cfg = Config(
            access_token_id='foo',
            access_token_secret='bar'
        )
        access_token_headers = {
            'X-Rune-User-Access-Token-Id': 'foo',
            'X-Rune-User-Access-Token-Secret': 'bar',
        }
        self.assertEqual(
            access_token_headers,
            cfg.auth_headers
        )
        self.assertEqual(
            access_token_headers,
            cfg.access_token_auth_headers
        )
        with self.assertRaises(ValueError):
            _ = cfg.client_auth_headers

        with self.assertRaises(ValueError):
            _ = cfg.jwt_auth_headers

        # client keys
        cfg = Config(
            client_key_id='abc',
            client_access_key='123',
        )
        client_headers = {
            'X-Rune-Client-Key-ID': 'abc',
            'X-Rune-Client-Access-Key': '123',
        }
        self.assertEqual(client_headers, cfg.auth_headers)
        self.assertEqual(client_headers, cfg.client_auth_headers)
        with self.assertRaises(ValueError):
            _ = cfg.jwt_auth_headers

        with self.assertRaises(ValueError):
            _ = cfg.access_token_auth_headers

        # jwt
        cfg = Config(jwt='abc123')
        jwt_headers = {
            'X-Rune-User-Access-Token': 'abc123'
        }
        self.assertEqual(jwt_headers, cfg.auth_headers)
        self.assertEqual(jwt_headers, cfg.jwt_auth_headers)
        with self.assertRaises(ValueError):
            _ = cfg.client_auth_headers

        with self.assertRaises(ValueError):
            _ = cfg.access_token_auth_headers

    def test_init_kwargs_invalid(self):
        """
        Test initializing with invalid kwargs.

        """
        with self.assertRaises(ValueError):
            Config(client_key_id='abc')

        with self.assertRaises(ValueError):
            Config(client_access_key='123')

        with self.assertRaises(ValueError):
            Config(client_access_key='123', jwt='abc123')

        with self.assertRaises(ValueError):
            Config(access_token_id='foo')

        with self.assertRaises(ValueError):
            Config(
                access_token_id='foo',
                client_access_key='123'
            )

        with self.assertRaises(ValueError):
            Config(
                access_token_id='foo',
                client_access_key='123',
                jwt='zee'
            )

    def test_init_invalid(self):
        """
        Cannot initialize with a filename and kwargs
        """
        with self.assertRaises(TypeError):
            Config(
                self.client_keys_good_config,
                stream_url='https://bar.runelabs.io'
            )
