import os
from unittest import TestCase

from runeq import Config

TEST_ROOT = os.path.dirname(os.path.realpath(__file__))


class TestConfig(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.good_config = f'{TEST_ROOT}/data/good_config.yaml'
        cls.bad_config = f'{TEST_ROOT}/data/bad_config.yaml'

    def test_init_file(self):
        """
        Test initializing using a yaml file
        """
        cfg = Config(self.good_config)

        expected = {
            'X-Rune-Client-Key-ID': 'abc',
            'X-Rune-Client-Access-Key': 'def',
        }
        self.assertEqual(expected, cfg.auth_headers)
        self.assertEqual(expected, cfg.client_auth_headers)
        with self.assertRaises(ValueError):
            _ = cfg.jwt_auth_headers

        self.assertEqual('https://foo.runelabs.io', cfg.stream_url)

    def test_init_file_invalid(self):
        """
        Test initializing with an invalid YAML file
        """
        with self.assertRaises(ValueError):
            Config(self.bad_config)

    def test_init_kwargs(self):
        """
        Test initializing with valid kwargs
        """
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

        # jwt
        cfg = Config(jwt='abc123')
        jwt_headers = {
            'X-Rune-User-Access-Token': 'abc123'
        }
        self.assertEqual(jwt_headers, cfg.auth_headers)
        self.assertEqual(jwt_headers, cfg.jwt_auth_headers)
        with self.assertRaises(ValueError):
            _ = cfg.client_auth_headers

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

    def test_init_invalid(self):
        """
        Cannot initialize with a filename and kwargs
        """
        with self.assertRaises(TypeError):
            Config(self.good_config, stream_url='https://bar.runelabs.io')
