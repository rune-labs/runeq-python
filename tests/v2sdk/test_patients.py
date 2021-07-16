"""
Tests for patient queries and record interaction.

"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

import runeq


class TestPatients(TestCase):
    """
    Tests for interacting with the patient graph resource.

    """


    @patch('runeq.v2sdk.graph.client.GQLClient')
    def test_fetch_patient_by_id(self, gqlclient):
        """
        Test listing all patients with a frozen time session.

        """
        session = runeq.session(MagicMock())
        gqlclient().execute.return_value = {
            'patient': {
                'id': 'patient-llama,patient',
                'codeName': 'Llama Patient',
                'createdAt': 1234567890.0
            }
        }

        patient = session.patients['llama']

        self.assertEqual('llama', patient.id)
        self.assertEqual('Llama Patient', patient.code_name)
        self.assertEqual(1234567890.0, patient.created_at)
        gqlclient().execute.assert_called_once()

        # Test patient caching
        patient = session.patients['llama']
        gqlclient().execute.assert_called_once()


    @patch('runeq.v2sdk.client.GraphAPIClient')
    def test_find_by_codename(self, graphclient):
        """
        Test searching for a patient by code name.

        """
        session = runeq.session(MagicMock())
        graphclient().list_patients.side_effect = lambda: iter(
            [
                {
                    'id': 'patient-llama0,patient',
                    'codeName': 'Llama Zero',
                    'createdAt': 1234567890.0
                },
                {
                    'id': 'patient-llama1,patient',
                    'codeName': 'Llama One',
                    'createdAt': 1234567890.1
                },
                {
                    'id': 'patient-llama2,patient',
                    'codeName': 'Llama Two',
                    'createdAt': 1234567890.2
                }
            ]
        )

        patients = list(session.patients.find_all_by(code_name='Llama One'))

        self.assertEqual(1, len(patients))
        self.assertEqual('llama1', patients[0].id)


    @patch('runeq.v2sdk.graph.client.GQLClient')
    def test_frozen_patients(self, gqlclient):
        """
        Test listing all patients with a frozen time session.

        """
        session = runeq.session(MagicMock())
        gqlclient().execute.return_value = {
            'org': {
                'patientAccessList': {
                    'pageInfo': {'endCursor': None},
                    'patientAccess': [
                        {
                            'patient': {
                                'id': 'patient-llama0,patient',
                                'codeName': 'Patient Llama 0',
                                'createdAt': 1234567890.0,
                            }
                        },
                        {
                            'patient': {
                                'id': 'patient-llama1,patient',
                                'codeName': 'Patient Llama 1',
                                'createdAt': 1234567890.1,
                            }
                        }
                    ]
                }
            }
        }

        session.freeze_time(1234567890.05)
        patients = list(session.patients)

        self.assertEqual(1, len(patients))
        self.assertEqual('llama0', patients[0].id)
        gqlclient().execute.assert_called_once()


    @patch('runeq.v2sdk.graph.client.GQLClient')
    def test_list_all_patients(self, gqlclient):
        """
        Test listing all patients.

        """
        session = runeq.session(MagicMock())
        gqlclient().execute.return_value = {
            'org': {
                'patientAccessList': {
                    'pageInfo': {'endCursor': None},
                    'patientAccess': [
                        {
                            'patient': {
                                'id': 'patient-llama0,patient',
                                'codeName': 'Patient Llama 0',
                                'createdAt': 1234567890.0,
                            }
                        },
                        {
                            'patient': {
                                'id': 'patient-llama1,patient',
                                'codeName': 'Patient Llama 1',
                                'createdAt': 1234567890.1,
                            }
                        }
                    ]
                }
            }
        }

        patients = list(session.patients)

        self.assertEqual(2, len(patients))
        self.assertEqual('llama0', patients[0].id)
        self.assertEqual('llama1', patients[1].id)
        gqlclient().execute.assert_called_once()

        # Test that caching is working
        patients = list(session.patients)
        self.assertEqual(2, len(patients))
        self.assertEqual('llama0', patients[0].id)
        self.assertEqual('llama1', patients[1].id)
        gqlclient().execute.assert_called_once()

        # Test that retrieve uses the cache
        patient = session.patients['llama1']
        self.assertEqual('llama1', patient.id)
        gqlclient().execute.assert_called_once()
