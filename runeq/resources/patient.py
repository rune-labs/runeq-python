"""
V2 SDK functionality to support Patient and Device operations.

"""

from typing import List, Optional, Type, Union

from .client import GraphClient, global_graph_client
from .common import ItemBase, ItemSet


class Device(ItemBase):
    """
    A device.

    """

    def __init__(
        self,
        id: str,
        patient_id: str,
        alias: str,
        created_at: float,
        **attributes
    ):
        """
        Initializes a Device

        """
        self.patient_id = patient_id
        self.alias = alias
        self.created_at = created_at

        super().__init__(
            id=id,
            patient_id=patient_id,
            alias=alias,
            created_at=created_at,
            **attributes,
        )

    @staticmethod
    def normalize_id(device_id: str) -> str:
        """
        Strip resource prefix and suffix from Device ID if they exist.

        """
        id = device_id.split(",")[-1]

        if id.startswith("device-"):
            id = id[7:]

        return id

    @staticmethod
    def denormalize_id(patient_id: str, device_id: str) -> str:
        """
        Add resource prefix and suffix to Device ID if they don't exist.

        """
        norm_patient_id = Patient.normalize_id(patient_id)
        norm_device_id = Device.normalize_id(device_id)

        return f'patient-{norm_patient_id},device-{norm_device_id}'


class DeviceSet(ItemSet):
    """
    DeviceSet class which inherits from the ItemSet class.

    """

    def __init__(self, items: List[Device] = []):
        """
        Initializes a set of Devices

        """
        super().__init__(items=items)

    @property
    def _item_class(self) -> Type[ItemBase]:
        """
        Instance type of items in this set.

        """
        return Device


class Patient(ItemBase):
    """
    A patient.

    """

    def __init__(
        self,
        id: str,
        code_name: str,
        created_at: float,
        devices: DeviceSet,
        **attributes
    ):
        """
        Initializes an Org

        """
        self.code_name = code_name
        self.created_at = created_at
        self.devices = devices

        super().__init__(
            id=id,
            code_name=code_name,
            created_at=created_at,
            devices=devices,
            **attributes,
        )

    @staticmethod
    def normalize_id(id: str) -> str:
        """
        Strip resource prefix from Patient ID if it exists.

        """
        if id.startswith("patient-"):
            id = id[8:]

        return id

    @staticmethod
    def denormalize_id(id: str) -> str:
        """
        Add resource prefix to Patient ID if it doesn't exist.

        """
        if not id.startswith("patient-"):
            id = f'patient-{id}'

        return id

    def device(self, device_id: str) -> Device:
        """
        Gets the patient's device with the specified device_id.

        """
        device_id = Device.normalize_id(device_id)

        for device in self.devices:
            if device.id == device_id:
                return device

        raise ValueError("Device not found with id: %s" % device_id)

    def to_dict(self) -> dict:
        """
        Dictionary representation of the item's attributes.

        """
        attrs = self._attributes.copy()
        attrs["devices"] = self.devices.to_list()
        return attrs


class PatientSet(ItemSet):
    """
    PatientSet class which inherits from the ItemSet class.

    """

    def __init__(self, items: List[Patient] = []):
        """
        Initializes a set of Patients

        """
        super().__init__(items=items)

    @property
    def _item_class(self) -> Type[ItemBase]:
        """
        Instance type of items in this set.

        """
        return Patient

    def devices(self) -> DeviceSet:
        """
        Set of all devices that belong to the patients.

        """
        all_devices = DeviceSet()
        for patient in self._items.values():
            for device in patient.devices:
                all_devices.add(device)

        return all_devices


def get_patient(
    patient_id: str,
    client: Optional[GraphClient] = None
) -> Patient:
    """
    Get the patient with the specified patient_id.

    """
    client = client or global_graph_client()
    query = '''
        query getPatient($patient_id: ID!, $cursor: Cursor) {
            patient(id: $patient_id) {
                id
                code_name: codeName
                created_at: createdAt
                deviceList(cursor: $cursor) {
                    pageInfo {
                        endCursor
                    }
                    devices {
                        id: deviceShortId
                        denormalized_id: id
                        alias
                        created_at: createdAt
                        disabled
                        disabled_at: disabledAt
                        updated_at: updatedAt
                    }
                }
            }
        }
    '''

    patient_id = Patient.normalize_id(patient_id)
    patient_attrs = {}

    next_cursor = None
    device_set = DeviceSet()

    # Use cursor to page through all patient devices
    while True:
        result = client.execute(
            statement=query,
            patient_id=patient_id,
            cursor=next_cursor
        )

        patient_attrs = result["patient"]

        # Add the patient's devices to device_set
        device_list = patient_attrs.get("deviceList", {})
        for device_attrs in device_list.get("devices", []):
            device = Device(
                patient_id=patient_id,
                **device_attrs
            )
            device_set.add(device)

        # next_cursor is None when there are no more devices for this patient
        next_cursor = device_list.get("pageInfo", {}).get("endCursor")
        if not next_cursor:
            break

    del patient_attrs["deviceList"]
    return Patient(devices=device_set, **patient_attrs)


def get_all_patients(client: Optional[GraphClient] = None) -> PatientSet:
    """
    Get a set of all patients the user has access to.

    """
    client = client or global_graph_client()
    patients_query = '''
        query getPatientList($patient_cursor: Cursor, $device_cursor: Cursor) {
            org {
                patientAccessList(cursor: $patient_cursor) {
                    pageInfo {
                        endCursor
                    }
                    patientAccess {
                        patient {
                            id
                            code_name: codeName
                            created_at: createdAt
                            deviceList(cursor: $device_cursor) {
                                pageInfo {
                                    endCursor
                                }
                                devices {
                                    id: deviceShortId
                                    denormalized_id: id
                                    alias
                                    created_at: createdAt
                                    disabled
                                    disabled_at: disabledAt
                                    updated_at: updatedAt
                                }
                            }
                        }
                    }
                }
            }
        }
    '''

    patient_cursor = None
    patient_set = PatientSet()

    # Use cursor to page through all patients
    while True:
        result = client.execute(
            statement=patients_query,
            patient_cursor=patient_cursor,
            device_cursor=None,
        )

        # Loop over all accessible patients
        curr_pal = result.get("org", {}).get("patientAccessList", {})
        for patient_info in curr_pal.get("patientAccess", []):
            patient_attrs = patient_info["patient"]
            patient_id = Patient.normalize_id(patient_attrs["id"])

            # Add the patient's devices to device_set
            device_set = DeviceSet()
            device_list = patient_attrs.get("deviceList", {})
            for device_attrs in device_list.get("devices", []):
                device = Device(
                    patient_id=patient_id,
                    **device_attrs
                )
                device_set.add(device)

            device_cursor = device_list.get("pageInfo", {}).get("endCursor")
            if not device_cursor:
                # If there are no more devices for this patient, device_set is
                # complete and the patient can be added to the patient_set.
                del patient_attrs["deviceList"]
                patient = Patient(devices=device_set, **patient_attrs)
                patient_set.add(patient)
            else:
                # If there are more devices for this patient, then query for
                # all their patient data at once.
                patient = get_patient(patient_id, client=client)
                patient_set.add(patient)

        # patient_cursor is None when there are no more pages of patients.
        patient_cursor = curr_pal.get("pageInfo", {}).get("endCursor")
        if not patient_cursor:
            break

    return patient_set


def get_device(
    patient: Union[Patient, str],
    device_id: str,
    client: Optional[GraphClient] = None,
) -> Device:
    """
    Get the device for the patient with the specified device_id.

    """
    if type(patient) is str:
        patient = get_patient(patient=patient, client=client)

    return patient.device(device_id=device_id)


def get_patient_devices(
    patient: Union[Patient, str],
    client: Optional[GraphClient] = None,
) -> DeviceSet:
    """
    Get all the devices with the specified device_id.

    """
    if type(patient) is str:
        patient = get_patient(patient=patient, client=client)

    return patient.devices


def get_all_devices(
    patients: Union[PatientSet, List[str]] = None,
    client: Optional[GraphClient] = None,
) -> DeviceSet:
    """
    Get a set of all devices across a set of patients or all patients in
    the org the user is currently a member of.

    """
    if not patients:
        return get_all_patients(client=client).devices

    if type(patients) is list:
        all_devices = DeviceSet()

        for patient_id in patients:
            patient = get_patient(patient_id=patient_id, client=client)
            for device in patient.devices:
                all_devices.add(device)

        return all_devices

    return patients.devices()
