"""
Tests for patient device queries.

"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

import runeq


class TestDevices(TestCase):
    """
    Tests for interacting with the patient device graph resource.

    """


    @patch('runeq.v2sdk.client.GraphAPIClient')
    def test_find_by_device_type(self, graphclient):
        """
        Test searching for devices matching a device type.

        """
        session = runeq.session(MagicMock())
        graphclient().fetch_patient.return_value = {
            'id': 'patient-llama0,patient',
            'codeName': 'Llama Zero',
            'createdAt': 1234567890.0
        }
        graphclient().list_patient_devices.side_effect = lambda **kwarg: iter(
            [
                {
                    'id': 'patient-llama0,device-0',
                    'alias': 'Device Zero',
                    'createdAt': 1234567890.1,
                    'deviceType': {
                        'id': 'llamadev0',
                        'displayName': 'Llama Device Type 0'
                    }
                },
                {
                    'id': 'patient-llama0,device-1',
                    'alias': 'Device One',
                    'createdAt': 1234567890.2,
                    'deviceType': {
                        'id': 'llamadev1',
                        'displayName': 'Llama Device Type 1'
                    }
                },
                {
                    'id': 'patient-llama0,device-2',
                    'alias': 'Device Two',
                    'createdAt': 1234567890.2,
                    'deviceType': {
                        'id': 'llamadev0',
                        'displayName': 'Llama Device Type 0'
                    }
                }
            ]
        )

        patient = session.patients['llama0']
        devices = list(patient.devices.find_all_by(device_type='llamadev0'))

        self.assertEqual(2, len(devices))
        self.assertEqual('Device Zero', devices[0].alias)
        self.assertEqual(
            'Llama Device Type 0',
            devices[0].device_type.display_name,
        )
        self.assertEqual('Device Two', devices[1].alias)
        self.assertEqual(
            'Llama Device Type 0',
            devices[1].device_type.display_name,
        )


    @patch('runeq.v2sdk.client.GraphAPIClient')
    def test_frozen_devices(self, graphclient):
        """
        Test listing devices when session is time frozen.

        """
        session = runeq.session(MagicMock())

        graphclient().list_patients.side_effect = lambda: iter(
            [
                {
                    'id': 'patient-llama0,patient',
                    'codeName': 'Llama Zero',
                    'createdAt': 1234567890.0
                }
            ]
        )
        graphclient().list_patient_devices.side_effect = [
            iter([
                {
                    'id': 'patient-llama0,device-0',
                    'alias': 'Device Zero',
                    'createdAt': 1234567890.1,
                    'deviceType': {
                        'id': 'llamadev',
                        'displayName': 'Llama Device'
                    }
                },
                {
                    'id': 'patient-llama0,device-1',
                    'alias': 'Device One',
                    'createdAt': 1234567890.2,
                    'deviceType': {
                        'id': 'llamadev',
                        'displayName': 'Llama Device'
                    }
                }
            ])
        ]

        session.freeze_time(1234567890.15)
        devices = list(session.devices)

        self.assertEqual(1, len(devices))
        self.assertEqual('0', devices[0].id)


    @patch('runeq.v2sdk.client.GraphAPIClient')
    def test_list_all_devices(self, graphclient):
        """
        Test listing all devices across patients

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
                }
            ]
        )
        graphclient().list_patient_devices.side_effect = [
            iter([
                {
                    'id': 'patient-llama0,device-0',
                    'alias': 'Device Zero',
                    'createdAt': 1234567890.2,
                    'deviceType': {
                        'id': 'llamadev',
                        'displayName': 'Llama Device'
                    },
                    'patientId': 'llama0'
                }
            ]),
            iter([
                {
                    'id': 'patient-llama1,device-1',
                    'alias': 'Device One',
                    'createdAt': 1234567890.3,
                    'deviceType': {
                        'id': 'llamadev',
                        'displayName': 'Llama Device'
                    },
                    'patientId': 'llama1'
                },
                {
                    'id': 'patient-llama1,device-2',
                    'alias': 'Device Two',
                    'createdAt': 1234567890.4,
                    'deviceType': {
                        'id': 'llamadev',
                        'displayName': 'Llama Device'
                    },
                    'patientId': 'llama1'
                }
            ])
        ]

        devices = list(session.devices)

        self.assertEqual(3, len(devices))
        self.assertEqual('0', devices[0].id)
        self.assertEqual('llama0', devices[0].patient_id)
        self.assertEqual('1', devices[1].id)
        self.assertEqual('llama1', devices[1].patient_id)
        self.assertEqual('2', devices[2].id)
        self.assertEqual('llama1', devices[2].patient_id)


    @patch('runeq.v2sdk.client.GraphAPIClient')
    def test_list_patient_devices(self, graphclient):
        """
        Test listing a patient's devices.

        """
        session = runeq.session(MagicMock())
        graphclient().fetch_patient.return_value = {
            'id': 'patient-llama0,patient',
            'codeName': 'Llama Zero',
            'createdAt': 1234567890.0
        }
        graphclient().list_patient_devices.side_effect = lambda **kwarg: iter(
            [
                {
                    'id': 'patient-llama0,device-0',
                    'alias': 'Device Zero',
                    'createdAt': 1234567890.1,
                    'deviceType': {
                        'id': 'llamadev',
                        'displayName': 'Llama Device'
                    }
                },
                {
                    'id': 'patient-llama0,device-1',
                    'alias': 'Device One',
                    'createdAt': 1234567890.2,
                    'deviceType': {
                        'id': 'llamadev',
                        'displayName': 'Llama Device'
                    }
                }
            ]
        )

        patient = session.patients['llama0']
        devices = list(patient.devices)

        self.assertEqual(2, len(devices))
        self.assertEqual('0', devices[0].id)
        self.assertEqual('Device Zero', devices[0].alias)
        self.assertEqual('1', devices[1].id)
        self.assertEqual('Device One', devices[1].alias)
