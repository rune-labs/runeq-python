"""
Tests for the Graph API client.

"""
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from gql import gql

from runeq.config import AUTH_METHOD_ACCESS_TOKEN, AUTH_METHOD_CLIENT_KEYS
from runeq.v2sdk.graph.client import GraphAPIClient
from runeq.v2sdk.graph.model import GraphID



class TestGraphID(TestCase):
    """
    Test the graph identifier wrapper.

    """


    def test_from_absolute(self):
        """
        Test parsing an absolute graph ID.

        """
        graphid = GraphID('patient-llama,device-123')

        self.assertEqual('patient-llama', graphid.principal)
        self.assertEqual('device-123', graphid.relative)
        self.assertEqual('123', graphid.unqualified)
        self.assertEqual('patient-llama,device-123', str(graphid))


    def test_from_relative(self):
        """
        Test constructing from a relative ID.

        """
        graphid = GraphID('llama', 'patient')

        self.assertEqual('patient-llama', graphid.principal)
        self.assertEqual('patient', graphid.relative)
        self.assertEqual('llama', graphid.unqualified)
        self.assertEqual('patient-llama,patient', str(graphid))


    def test_ambigous(self):
        """
        Test that ambiguous IDs raise an error.

        """
        self.assertRaises(ValueError, lambda: GraphID('llama'))



class TestGraphAPIClient(TestCase):
    """
    Tests for the Graph API client.

    """


    @patch('runeq.v2sdk.graph.client.GQLClient')
    def test_fetch_patient(self, gqlclient):
        """
        Test query for single patient by ID.

        """
        config = MagicMock()
        client = GraphAPIClient(config)

        patient0 = {
            'id': 'patient-llama,patient',
            'codeName': 'Llama Patient',
            'createdAt': 1234567890.0
        }
        gqlclient().execute.return_value = {'patient': patient0}

        self.assertEqual(
            patient0,
            client.fetch_patient(GraphID('llama', 'patient'))
        )

        gqlclient().execute.assert_called_once_with(
            gql('''
                query($patientId: ID!) {
                    patient(id: $patientId) {
                        id
                        codeName
                        createdAt
                    }
                }
            '''),
            variable_values={'patientId': 'patient-llama,patient'}
        )


    @patch('runeq.v2sdk.graph.client.GQLClient')
    def test_list_patient_devices(self, gqlclient):
        """
        Test query for listing devices for a patient.

        """
        config = MagicMock()
        client = GraphAPIClient(config)

        device0 = {
            'id': 'patient-llama,device-0',
            'alias': "Device Zero",
            'createdAt': 1234567890.0,
            'deviceType': {
                'id': 'llama',
                'displayName': "Llama Device"
            }
        }
        device1 = {
            'id': 'patient-llama,device-1',
            'alias': "Device One",
            'createdAt': 1234567890.1,
            'deviceType': {
                'id': 'llama',
                'displayName': "Llama Device"
            }
        }
        device2 = {
            'id': 'patient-llama,device-2',
            'alias': "Device Two",
            'createdAt': 1234567890.2,
            'deviceType': {
                'id': 'llama',
                'displayName': "Llama Device"
            }
        }

        gqlclient().execute.side_effect = [
            {
                'patient': {
                    'deviceList': {
                        'pageInfo': {
                            'endCursor': 'llamacursor0',
                        },
                        'devices': [
                            device0,
                            device1,
                        ]
                    }
                }
            },
            {
                'patient': {
                    'deviceList': {
                        'pageInfo': {
                            'endCursor': None,
                        },
                        'devices': [
                            device2
                        ]
                    }
                }
            }
        ]

        devices = client.list_patient_devices(
            patient_id=GraphID('patient-llama,patient')
        )

        self.assertEqual(device0, next(devices))
        self.assertEqual(device1, next(devices))
        self.assertEqual(device2, next(devices))
        self.assertRaises(StopIteration, lambda: next(devices))

        expected_gql = gql('''
            query(
                $patientId: ID!,
                $withDisabled: Boolean!,
                $cursor: Cursor
            ) {
                patient(id: $patientId) {
                    deviceList(
                        withDisabled: $withDisabled,
                        cursor: $cursor
                    ) {
                        devices {
                            id
                            alias
                            createdAt
                            deviceType {
                                id
                                displayName
                            }
                        }
                        pageInfo {
                            endCursor
                        }
                    }
                }
            }
        ''')

        self.assertEqual(2, gqlclient().execute.call_count)
        gqlclient().execute.assert_has_calls([
            call(
                expected_gql,
                variable_values={
                    'cursor': None,
                    'patientId': 'patient-llama,patient',
                    'withDisabled': False
                }
            ),
            call(
                expected_gql,
                variable_values={
                    'cursor': 'llamacursor0',
                    'patientId': 'patient-llama,patient',
                    'withDisabled': False
                }
            )
        ])


    @patch('runeq.v2sdk.graph.client.GQLClient')
    def test_list_patients(self, gqlclient):
        """
        Test query for listing all patients.

        """
        config = MagicMock()
        client = GraphAPIClient(config)

        patient0 = {
            'id': 'patient-llama0,patient',
            'codeName': 'Patient Llama 0',
            'createdAt': 1234567890.0,
        }
        patient1 = {
            'id': 'patient-llama1,patient',
            'codeName': 'Patient Llama 1',
            'createdAt': 1234567890.1,
        }
        patient2 = {
            'id': 'patient-llama2,patient',
            'codeName': 'Patient Llama 2',
            'createdAt': 1234567890.2,
        }

        gqlclient().execute.side_effect = [
            {
                'org': {
                    'patientAccessList': {
                        'pageInfo': {
                            'endCursor': 'llamacursor0',
                        },
                        'patientAccess': [
                            {'patient': patient0},
                            {'patient': patient1}
                        ]
                    }
                }
            },
            {
                'org': {
                    'patientAccessList': {
                        'pageInfo': {
                            'endCursor': None,
                        },
                        'patientAccess': [
                            {'patient': patient2}
                        ]
                    }
                }
            }
        ]

        patients = client.list_patients()

        self.assertEqual(patient0, next(patients))
        self.assertEqual(patient1, next(patients))
        self.assertEqual(patient2, next(patients))
        self.assertRaises(StopIteration, lambda: next(patients))

        expected_gql = gql('''
            query($cursor: Cursor) {
                org {
                    patientAccessList(cursor: $cursor) {
                        pageInfo {
                            endCursor
                        }
                        patientAccess {
                            patient {
                                id
                                codeName
                                createdAt
                            }
                        }
                    }
                }
            }
        ''')

        self.assertEqual(2, gqlclient().execute.call_count)
        gqlclient().execute.assert_has_calls([
            call(expected_gql, variable_values={'cursor': None}),
            call(expected_gql, variable_values={'cursor': 'llamacursor0'})
        ])


    @patch('runeq.v2sdk.graph.client.GQLClient')
    def test_whoami_patient(self, gqlclient):
        """
        Test that the "who am I?" query for a patient.

        """
        config = MagicMock(auth_method=AUTH_METHOD_CLIENT_KEYS)
        client = GraphAPIClient(config)

        gqlclient().execute.return_value = {
            'patient': {
                'id': 'patient-llama,patient',
                'codeName': 'Patient Llama',
                'createdAt': 1234567890.0,
            }
        }

        self.assertEqual(
            gqlclient().execute.return_value,
            client.whoami()
        )

        gqlclient().execute.assert_called_once_with(
            gql('''
                query {
                    patient {
                        id
                        codeName
                        createdAt
                    }
                }
            '''),
            variable_values={}
        )


    @patch('runeq.v2sdk.graph.client.GQLClient')
    def test_whoami_user(self, gqlclient):
        """
        Test that the "who am I?" query for a user.

        """
        config = MagicMock(auth_method=AUTH_METHOD_ACCESS_TOKEN)
        client = GraphAPIClient(config)

        gqlclient().execute.return_value = {
            'user': {
                'id': 'llama',
                'created': 1234567890.0,
                'defaultMembership': {
                    'id': 'llama',
                    'created': 1234567890.0,
                    'org': {
                        'id': 'llama',
                        'created': 1234567890.0,
                        'displayName': 'Llama Org',
                    }
                },
                'displayName': 'Llama User',
                'email': 'llama@runelabs.io',
                'username': 'llamauser'
            }
        }

        self.assertEqual(
            gqlclient().execute.return_value,
            client.whoami()
        )

        gqlclient().execute.assert_called_once_with(
            gql('''
                query {
                    user {
                        id
                        created
                        defaultMembership {
                            id
                            created
                            org {
                                id
                                created
                                displayName
                            }
                        }
                        displayName
                        email
                        username
                    }
                }
            '''),
            variable_values={}
        )
