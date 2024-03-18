"""
Tests for fetching patient metadata

"""
from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import GraphClient
from runeq.resources.patient import (
    Device,
    DeviceSet,
    Patient,
    PatientSet,
    get_all_devices,
    get_all_patients,
    get_device,
    get_patient,
    get_patient_devices,
)


class TestPatient(TestCase):
    """
    Unit tests for the Patient class.

    """

    def setUp(self):
        """
        Set up mock graph client for testing.

        """
        self.mock_client = GraphClient(
            Config(client_key_id="test", client_access_key="config")
        )

    def test_attributes(self):
        """
        Test attributes for an initialized Patient.

        """
        test_patient = Patient(
            id="p1",
            created_at=1629300943.9179766,
            name="patient1",
            devices=DeviceSet(
                [
                    Device(
                        id="d1",
                        patient_id="p1",
                        name="Percept",
                        created_at=1629300943.9179766,
                        device_type_id="dt1",
                    ),
                    Device(
                        id="d2",
                        patient_id="p1",
                        name="Apple Watch",
                        created_at=1629300943.9179766,
                        device_type_id="dt2",
                    ),
                ]
            ),
        )

        self.assertEqual("p1", test_patient.id)
        self.assertEqual(1629300943.9179766, test_patient.created_at)
        self.assertEqual("patient1", test_patient.name)

        actual_devices = test_patient.devices.to_list()
        self.assertEqual(2, len(actual_devices))

        self.assertEqual(
            {
                "id": "d1",
                "patient_id": "p1",
                "name": "Percept",
                "created_at": 1629300943.9179766,
                "device_type_id": "dt1",
            },
            actual_devices[0],
        )

        self.assertEqual(
            {
                "id": "d2",
                "patient_id": "p1",
                "name": "Apple Watch",
                "created_at": 1629300943.9179766,
                "device_type_id": "dt2",
            },
            actual_devices[1],
        )

        self.assertEqual(
            Device(
                id="d1",
                patient_id="p1",
                name="Percept",
                created_at=1629300943.9179766,
                device_type_id="dt1",
            ),
            test_patient.device("d1"),
        )

    def test_repr(self):
        """
        Test __repr__

        """
        test_patient = Patient(
            id="p1",
            created_at=1629300943.9179766,
            name="Patient 1",
            devices=DeviceSet(),
        )
        self.assertEqual('Patient(id="p1", name="Patient 1")', repr(test_patient))

    def test_normalize_id(self):
        """
        Test strip id of resource prefix if it exists.

        """
        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            Patient.normalize_id("patient-d4b1c627bd464fe0a5ed940cc8e8e485"),
        )

        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            Patient.normalize_id("d4b1c627bd464fe0a5ed940cc8e8e485"),
        )

    def test_denormalize_id(self):
        """
        Test add id resource prefix if it doesn't exist.

        """
        self.assertEqual(
            "patient-d4b1c627bd464fe0a5ed940cc8e8e485",
            Patient.denormalize_id("patient-d4b1c627bd464fe0a5ed940cc8e8e485"),
        )

        self.assertEqual(
            "patient-d4b1c627bd464fe0a5ed940cc8e8e485",
            Patient.denormalize_id("d4b1c627bd464fe0a5ed940cc8e8e485"),
        )

    def test_get_patient_basic(self):
        """
        Test get patient for specified patient_id.

        """
        self.mock_client.execute = mock.Mock()
        self.mock_client.execute.side_effect = [
            {
                "patient": {
                    "id": "p1",
                    "created_at": 1630515986.9949625,
                    "name": "patient1",
                    "deviceList": {
                        "pageInfo": {"endCursor": None},
                        "devices": [
                            {
                                "id": "d1",
                                "name": "Percept",
                                "created_at": 1646685476.1367705,
                                "device_type": {"id": "dt1", "name": "percept"},
                                "disabled": False,
                                "disabled_at": None,
                                "updated_at": 1646685485.9403558,
                            },
                            {
                                "id": "d2",
                                "name": "Strive PD",
                                "created_at": 1646684177.194158,
                                "device_type": {"id": "dt2", "name": "strivestudy"},
                                "disabled": False,
                                "disabled_at": None,
                                "updated_at": 1646684177.194158,
                            },
                            {
                                "id": "d3",
                                "name": "Apple Watch",
                                "created_at": 1646684177.1942198,
                                "device_type": {"id": "dt3", "name": "watch"},
                                "disabled": True,
                                "disabled_at": 1646684178.1942198,
                                "updated_at": 1646684178.1942198,
                            },
                        ],
                    },
                }
            }
        ]

        test_patient = get_patient("patient-p1", client=self.mock_client)

        self.assertEqual(
            {
                "id": "p1",
                "created_at": 1630515986.9949625,
                "name": "patient1",
                "devices": [
                    {
                        "patient_id": "p1",
                        "name": "Percept",
                        "created_at": 1646685476.1367705,
                        "device_type_id": "dt1",
                        "disabled": False,
                        "disabled_at": None,
                        "updated_at": 1646685485.9403558,
                        "id": "d1",
                    },
                    {
                        "patient_id": "p1",
                        "name": "Strive PD",
                        "created_at": 1646684177.194158,
                        "device_type_id": "dt2",
                        "disabled": False,
                        "disabled_at": None,
                        "updated_at": 1646684177.194158,
                        "id": "d2",
                    },
                    {
                        "patient_id": "p1",
                        "name": "Apple Watch",
                        "created_at": 1646684177.1942198,
                        "device_type_id": "dt3",
                        "disabled": True,
                        "disabled_at": 1646684178.1942198,
                        "updated_at": 1646684178.1942198,
                        "id": "d3",
                    },
                ],
            },
            test_patient.to_dict(),
        )

    def test_get_patient_paginated(self):
        """
        Test get patient for specified patient_id, where the gql requests
        page through devices.

        """
        self.mock_client.execute = mock.Mock()
        self.mock_client.execute.side_effect = [
            {
                "patient": {
                    "id": "p1",
                    "created_at": 1630515986.9949625,
                    "name": "patient1",
                    "deviceList": {
                        "pageInfo": {"endCursor": "test_check_next"},
                        "devices": [
                            {
                                "id": "d1",
                                "name": "Percept",
                                "created_at": 1646685476.1367705,
                                "device_type": {
                                    "id": "dt1",
                                },
                                "disabled": False,
                                "disabled_at": None,
                                "updated_at": 1646685485.9403558,
                            }
                        ],
                    },
                }
            },
            {
                "patient": {
                    "id": "p1",
                    "created_at": 1630515986.9949625,
                    "name": "patient1",
                    "deviceList": {
                        "pageInfo": {"endCursor": None},
                        "devices": [
                            {
                                "id": "d2",
                                "name": "Strive PD",
                                "created_at": 1646684177.194158,
                                "device_type": {
                                    "id": "dt2",
                                },
                                "disabled": False,
                                "disabled_at": None,
                                "updated_at": 1646684177.194158,
                            }
                        ],
                    },
                }
            },
        ]

        test_patient = get_patient("patient-p1", client=self.mock_client)

        self.assertEqual(
            {
                "id": "p1",
                "created_at": 1630515986.9949625,
                "name": "patient1",
                "devices": [
                    {
                        "patient_id": "p1",
                        "name": "Percept",
                        "created_at": 1646685476.1367705,
                        "device_type_id": "dt1",
                        "disabled": False,
                        "disabled_at": None,
                        "updated_at": 1646685485.9403558,
                        "id": "d1",
                    },
                    {
                        "patient_id": "p1",
                        "name": "Strive PD",
                        "created_at": 1646684177.194158,
                        "device_type_id": "dt2",
                        "disabled": False,
                        "disabled_at": None,
                        "updated_at": 1646684177.194158,
                        "id": "d2",
                    },
                ],
            },
            test_patient.to_dict(),
        )

    def test_get_all_patients_basic(self):
        """
        Test get patients for the initialized user.

        """
        test_patient1 = {
            "patient": {
                "id": "p1",
                "created_at": 1630515986.9949625,
                "name": "patient1",
                "deviceList": {
                    "pageInfo": {"endCursor": None},
                    "devices": [
                        {
                            "id": "d1",
                            "name": "Percept",
                            "created_at": 1646685476.1367705,
                            "device_type": {
                                "id": "dt1",
                            },
                            "disabled": False,
                            "disabled_at": None,
                            "updated_at": 1646685485.9403558,
                        }
                    ],
                },
            }
        }

        test_patient2 = {
            "patient": {
                "id": "p2",
                "created_at": 1630515986.9949625,
                "name": "patient2",
                "deviceList": {
                    "pageInfo": {"endCursor": None},
                    "devices": [
                        {
                            "id": "d1",
                            "name": "Percept",
                            "created_at": 1646685476.1367705,
                            "device_type": {
                                "id": "dt1",
                            },
                            "disabled": False,
                            "disabled_at": None,
                            "updated_at": 1646685485.9403558,
                        }
                    ],
                },
            }
        }

        self.mock_client.execute = mock.Mock()
        self.mock_client.execute.side_effect = [
            {
                "org": {
                    "patientAccessList": {
                        "pageInfo": {"endCursor": None},
                        "patientAccess": [test_patient1, test_patient2],
                    }
                }
            }
        ]

        patients = get_all_patients(client=self.mock_client)

        self.assertEqual(
            [
                {
                    "id": "p1",
                    "created_at": 1630515986.9949625,
                    "name": "patient1",
                    "devices": [
                        {
                            "patient_id": "p1",
                            "name": "Percept",
                            "created_at": 1646685476.1367705,
                            "device_type_id": "dt1",
                            "disabled": False,
                            "disabled_at": None,
                            "updated_at": 1646685485.9403558,
                            "id": "d1",
                        }
                    ],
                },
                {
                    "id": "p2",
                    "created_at": 1630515986.9949625,
                    "name": "patient2",
                    "devices": [
                        {
                            "patient_id": "p2",
                            "name": "Percept",
                            "created_at": 1646685476.1367705,
                            "device_type_id": "dt1",
                            "disabled": False,
                            "disabled_at": None,
                            "updated_at": 1646685485.9403558,
                            "id": "d1",
                        }
                    ],
                },
            ],
            patients.to_list(),
        )

    def test_get_all_patients_paginated(self):
        """
        Test get patients for the initialized user, where the gql requests
        page through patients.

        """
        test_patient1 = {
            "patient": {
                "id": "p1",
                "created_at": 1630515986.9949625,
                "name": "patient1",
                "deviceList": {
                    "pageInfo": {"endCursor": None},
                    "devices": [
                        {
                            "id": "d1",
                            "name": "Percept",
                            "created_at": 1646685476.1367705,
                            "device_type": {
                                "id": "dt1",
                            },
                            "disabled": False,
                            "disabled_at": None,
                            "updated_at": 1646685485.9403558,
                        }
                    ],
                },
            }
        }

        test_patient2 = {
            "patient": {
                "id": "p2",
                "created_at": 1630515986.9949625,
                "name": "patient2",
                "deviceList": {
                    "pageInfo": {"endCursor": None},
                    "devices": [
                        {
                            "id": "d1",
                            "name": "Percept",
                            "created_at": 1646685476.1367705,
                            "device_type": {
                                "id": "dt1",
                            },
                            "disabled": False,
                            "disabled_at": None,
                            "updated_at": 1646685485.9403558,
                        }
                    ],
                },
            }
        }

        self.mock_client.execute = mock.Mock()
        self.mock_client.execute.side_effect = [
            {
                "org": {
                    "patientAccessList": {
                        "pageInfo": {"endCursor": "test_check_next"},
                        "patientAccess": [test_patient1],
                    }
                }
            },
            {
                "org": {
                    "patientAccessList": {
                        "pageInfo": {"endCursor": None},
                        "patientAccess": [test_patient2],
                    }
                }
            },
        ]

        patients = get_all_patients(client=self.mock_client)

        self.assertEqual(
            [
                {
                    "id": "p1",
                    "created_at": 1630515986.9949625,
                    "name": "patient1",
                    "devices": [
                        {
                            "patient_id": "p1",
                            "name": "Percept",
                            "created_at": 1646685476.1367705,
                            "device_type_id": "dt1",
                            "disabled": False,
                            "disabled_at": None,
                            "updated_at": 1646685485.9403558,
                            "id": "d1",
                        }
                    ],
                },
                {
                    "id": "p2",
                    "created_at": 1630515986.9949625,
                    "name": "patient2",
                    "devices": [
                        {
                            "patient_id": "p2",
                            "name": "Percept",
                            "created_at": 1646685476.1367705,
                            "device_type_id": "dt1",
                            "disabled": False,
                            "disabled_at": None,
                            "updated_at": 1646685485.9403558,
                            "id": "d1",
                        }
                    ],
                },
            ],
            patients.to_list(),
        )


class TestDevice(TestCase):
    """
    Unit tests for the Device class.

    """

    def setUp(self):
        """
        Set up mock graph client for testing.

        """
        self.maxDiff = None
        self.mock_client = GraphClient(
            Config(client_key_id="test", client_access_key="config")
        )

    def test_attributes(self):
        """
        Test attributes for an initialized Device.

        """
        test_device = Device(
            id="device-1",
            patient_id="patient-1",
            name="Percept",
            created_at=1629300943.9179766,
            device_type_id="dt1",
        )

        self.assertEqual("device-1", test_device.id)
        self.assertEqual("patient-1", test_device.patient_id)
        self.assertEqual("Percept", test_device.name)
        self.assertEqual(1629300943.9179766, test_device.created_at)
        self.assertEqual("dt1", test_device.device_type_id)

    def test_repr(self):
        """
        Test __repr__

        """
        test_device = Device(
            id="1",
            patient_id="p1",
            name="Percept",
            created_at=1629300943.9179766,
            device_type_id="dt1",
        )
        self.assertEqual(
            'Device(id="1", name="Percept", patient_id="p1")', repr(test_device)
        )

    def test_normalize_id(self):
        """
        Test strip id of resource prefix if it exists.

        """
        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            Device.normalize_id("device-d4b1c627bd464fe0a5ed940cc8e8e485"),
        )

        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            Device.normalize_id("d4b1c627bd464fe0a5ed940cc8e8e485"),
        )

    def test_denormalize_id(self):
        """
        Test add resource prefix and suffix to if they don't exist.

        """
        self.assertEqual(
            "patient-d4b1c627bd4,device-d4b1c627bd46",
            Device.denormalize_id("patient-d4b1c627bd4", "device-d4b1c627bd46"),
        )

        self.assertEqual(
            "patient-d4b1c627bd4,device-d4b1c627bd46",
            Device.denormalize_id("patient-d4b1c627bd4", "d4b1c627bd46"),
        )

        self.assertEqual(
            "patient-d4b1c627bd4,device-d4b1c627bd46",
            Device.denormalize_id("d4b1c627bd4", "device-d4b1c627bd46"),
        )

        self.assertEqual(
            "patient-d4b1c627bd4,device-d4b1c627bd46",
            Device.denormalize_id("d4b1c627bd4", "d4b1c627bd46"),
        )

    def test_get_device(self):
        """
        Test get device.

        """
        test_device = Device(
            id="1",
            patient_id="p1",
            name="Percept",
            created_at=1629300943.9179766,
            device_type_id="dt1",
        )

        test_patient = Patient(
            id="p1",
            created_at=1629300943.9179766,
            name="patient1",
            devices=DeviceSet([test_device]),
        )

        act_device = get_device(patient=test_patient, device_id="device-1")
        self.assertEqual(test_device.to_dict(), act_device.to_dict())

    def test_get_patient_devices(self):
        """
        Test get patient devices.

        """
        test_device_1 = Device(
            id="d1",
            patient_id="p1",
            name="Percept",
            created_at=1629300943.9179766,
            device_type_id="dt1",
        )

        test_device_2 = Device(
            id="d2",
            patient_id="p1",
            name="Apple Watch",
            created_at=1629300943.9179766,
            device_type_id="dt2",
        )

        test_patient = Patient(
            id="p1",
            created_at=1629300943.9179766,
            name="patient1",
            devices=DeviceSet([test_device_1, test_device_2]),
        )

        act_devices = get_patient_devices(
            patient=test_patient,
        )
        self.assertEqual(
            [test_device_1.to_dict(), test_device_2.to_dict()], act_devices.to_list()
        )

    def test_get_all_devices(self):
        """
        Test get all devices.

        """
        test_device_1 = Device(
            id="d1",
            patient_id="p1",
            name="Percept",
            created_at=1629300943.9179766,
            device_type_id="dt1",
        )

        test_patient_1 = Patient(
            id="p1",
            created_at=1629300943.9179766,
            name="patient1",
            devices=DeviceSet([test_device_1]),
        )

        test_device_2 = Device(
            id="d2",
            patient_id="p1",
            name="Apple Watch",
            created_at=1629300943.9179766,
            device_type_id="dt2",
        )

        test_patient_2 = Patient(
            id="p2",
            created_at=1629300943.9179766,
            name="patient2",
            devices=DeviceSet([test_device_2]),
        )

        patients = PatientSet([test_patient_1, test_patient_2])

        act_devices = get_all_devices(patients=patients)
        self.assertEqual(
            [test_device_1.to_dict(), test_device_2.to_dict()], act_devices.to_list()
        )
