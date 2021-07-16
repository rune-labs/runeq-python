"""
Tests for the v2 client.

"""
from unittest import TestCase
from unittest.mock import patch

import runeq
from runeq.config import AUTH_METHOD_ACCESS_TOKEN, AUTH_METHOD_CLIENT_KEYS
from runeq.v2sdk.patients import Patient
from runeq.v2sdk.users import User


class TestClientSession(TestCase):
    """
    Unit tests for the client session.

    """


    @patch('runeq.v2sdk.client.GraphAPIClient')
    def test_i_patient(self, graphclient):
        """
        Test the "who am I?" functionality as a patient.

        """
        config = runeq.Config(
            auth_method=AUTH_METHOD_CLIENT_KEYS,
            graph_url='http://graph.example.io',
            client_key_id='llama',
            client_access_key='llama',
        )

        graphclient().whoami.return_value = {
            'patient': {
                'id': 'patient-llama,patient',
                'codeName': 'llama code name',
                'createdAt': 1234567890.0,
            }
        }

        rune = runeq.session(config)
        me = rune.me

        self.assertIsInstance(me, Patient)
        self.assertEqual('llama', me.id)
        self.assertEqual('llama code name', me.code_name)
        graphclient().whoami.assert_called_once()

        # Assert caching works
        me = rune.me
        graphclient().whoami.assert_called_once()


    @patch('runeq.v2sdk.client.GraphAPIClient')
    def test_i_user(self, graphclient):
        """
        Test the "who am I" functionality as a user.

        """
        config = runeq.Config(
            auth_method=AUTH_METHOD_ACCESS_TOKEN,
            graph_url='http://graph.example.io',
            access_token_id='llama',
            access_token_secret='llama'
        )

        graphclient().whoami.return_value = {
            'user': {
                'id': 'llama',
                'created': 1234567890.0,
                'defaultMembership': {
                    'id': 'rune$llama',
                    'created': 1234567890.0,
                    'org': {
                        'id': 'llama',
                        'created': 1234567890.0,
                        'displayName': 'Llama Org'
                    }
                },
                'displayName': 'Llama User',
                'email': 'llama@runelabs.io',
                'username': 'llamauser',
            }
        }

        rune = runeq.session(config)
        me = rune.me

        self.assertIsInstance(me, User)
        self.assertEqual('llama', me.id)
        self.assertEqual('llama@runelabs.io', me.email)
        graphclient().whoami.assert_called_once()

        # Assert caching works
        me = rune.me
        graphclient().whoami.assert_called_once()
