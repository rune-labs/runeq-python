"""
Tests for the v2 client.

"""
from unittest import TestCase

from runeq import errors
from runeq.v2sdk import initialize
from runeq.v2sdk.stream import get_stream, NOT_INITIALIZED_ERROR


class TestInitialize(TestCase):
    """
    Unit tests for the initialization of the user's credentials.

    """

    def test_init_invalid(self):
        """
        Test that access is restricted with no initialization.

        """
        with self.assertRaises(errors.RuneError) as err:
            get_stream("stream_id")

        self.assertEqual(NOT_INITIALIZED_ERROR, str(err.exception))

    def test_init_with_access_keys(self):
        """
        Test that the user is initialized but with invalid access keys.

        """
        initialize(
            access_token_id="foo",
            access_token_secret="bar",
        )

        with self.assertRaisesRegex(errors.APIError, "404 NotFound"):
            get_stream("stream_id").__next__()

    def test_init_with_client_keys(self):
        """
        Test that the user is initialized but with invalid client keys.

        """
        initialize(
            client_key_id="foo",
            client_access_key="bar",
        )

        with self.assertRaisesRegex(
            errors.APIError,
            "401 InvalidAuthentication"
        ):
            get_stream("stream_id").__next__()
