"""
Fetch metadata about patients, including their devices.

"""

from typing import Iterable, List, Optional, Type, Union

from .client import GraphClient, global_graph_client
from .common import ItemBase, ItemSet


class Device(ItemBase):
    """
    A patient device.

    A device is a sensor serving as the datasource, such as a neural implant,
    phone, or wearable. Each device belongs to a patient. A patient may have
    multiple devices: each one has a unique identifier ("device ID").

    """

    def __init__(
        self,
        id: str,
        patient_id: str,
        name: str,
        created_at: float,
        device_type_id: str,
        **attributes,
    ):
        """
        Initialize with metadata.

        Args:
            id: ID of the device
            patient_id: ID of the patient
            name: Human-readable name for the device
            created_at: When the device was created (unix timestamp)
            **attributes: Other attributes associated with the device

        """
        self.patient_id = patient_id
        self.name = name
        self.created_at = created_at
        self.device_type_id = device_type_id

        super().__init__(
            id=id,
            patient_id=patient_id,
            name=name,
            created_at=created_at,
            device_type_id=device_type_id,
            **attributes,
        )

    @staticmethod
    def normalize_id(device_id: str) -> str:
        """
        Strip resource prefix and suffix from a device ID (if they exist).

        Args:
            device_id: Device ID
        """
        id = device_id.split(",")[-1]

        if id.startswith("device-"):
            id = id[7:]

        return id

    @staticmethod
    def denormalize_id(patient_id: str, device_id: str) -> str:
        """
        Add resource prefix and suffix to a patient/device ID.

        This constructs the form of the ID that is used for requests to the
        GraphQL API.

        Args:
            patient_id: ID of the patient who owns the device
            device_id: Device ID

        """
        norm_patient_id = Patient.normalize_id(patient_id)
        norm_device_id = Device.normalize_id(device_id)

        return f"patient-{norm_patient_id},device-{norm_device_id}"

    def __repr__(self):
        """
        Override repr, to include the patient ID (as well as the device ID
        and name)

        """
        return (
            f'{self.__class__.__name__}(id="{self.id}", '
            f'name="{self.name}", patient_id="{self.patient_id}")'
        )


class DeviceSet(ItemSet):
    """
    A collection of Devices.

    """

    def __init__(self, items: Iterable[Device] = ()):
        """
        Initialize with Devices.

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

    A patient represents a person about whom data was measured. This may
    include a StrivePD user, a person with a neural implant, etc. Each patient
    has a unique identifier ("patient ID").

    """

    def __init__(
        self, id: str, name: str, created_at: float, devices: DeviceSet, **attributes
    ):
        """
        Initialize with metadata.

        Args:
            id: ID of the patient
            name: Human-readable display name for the patient
            created_at: When the patient's record was created (unix timestamp)
            devices: Devices that belong to the patient
            **attributes: Other attributes associated with the patient
        """
        self.name = name
        self.created_at = created_at
        self.devices = devices

        super().__init__(
            id=id,
            name=name,
            created_at=created_at,
            devices=devices,
            **attributes,
        )

    @staticmethod
    def normalize_id(patient_id: str) -> str:
        """
        Strip resource prefix from a patient ID (if it exists).

        Args:
            patient_id: Patient ID

        """
        if patient_id.startswith("patient-"):
            patient_id = patient_id[8:]

        return patient_id

    @staticmethod
    def denormalize_id(patient_id: str) -> str:
        """
        Add resource prefix to a patient ID (if it doesn't exist).

        This constructs the form of the ID that is used for requests to the
        GraphQL API.

        Args:
            patient_id: Patient ID

        """
        if not patient_id.startswith("patient-"):
            patient_id = f"patient-{patient_id}"

        return patient_id

    def device(self, device_id: str) -> Device:
        """
        Return the patient's device with the specified device ID.

        Args:
            device_id: Device ID

        Raises:
            ValueError: if the patient does not have a device with the ID

        """
        device_id = Device.normalize_id(device_id)

        for device in self.devices:
            if device.id == device_id:
                return device

        raise ValueError("Device not found with id: %s" % device_id)

    def to_dict(self) -> dict:
        """
        Dictionary representation of the Patient attributes.

        """
        attrs = self._attributes.copy()
        attrs["devices"] = self.devices.to_list()
        return attrs


class PatientSet(ItemSet):
    """
    A collection of Patients.

    """

    def __init__(self, items: Iterable[Patient] = ()):
        """
        Initialize with Patients.

        """
        super().__init__(items=items)

    @property
    def _item_class(self) -> Type[ItemBase]:
        """
        Instance type of items in this set.

        """
        return Patient

    @property
    def devices(self) -> DeviceSet:
        """
        Set of all devices that belong to the patients in this collection.

        """
        all_devices = DeviceSet()
        for patient in self._items.values():
            for device in patient.devices:
                all_devices.add(device)

        return all_devices


def get_patient(patient_id: str, client: Optional[GraphClient] = None) -> Patient:
    """
    Get the patient with the specified patient ID.

    Args:
        patient_id: Patient ID
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    """
    client = client or global_graph_client()
    query = """
        query getPatient($patient_id: ID!, $cursor: Cursor) {
            patient(id: $patient_id) {
                id
                name: codeName
                created_at: createdAt
                deviceList(cursor: $cursor) {
                    pageInfo {
                        endCursor
                    }
                    devices {
                        id: deviceShortId
                        name: alias
                        created_at: createdAt
                        device_type: deviceType {
                            id
                        }
                        disabled
                        disabled_at: disabledAt
                        updated_at: updatedAt
                    }
                }
            }
        }
    """

    patient_id = Patient.normalize_id(patient_id)
    patient_attrs = {}

    next_cursor = None
    device_set = DeviceSet()

    # Use cursor to page through all patient devices
    while True:
        result = client.execute(
            statement=query, patient_id=patient_id, cursor=next_cursor
        )

        patient_attrs = result["patient"]

        # Add the patient's devices to device_set
        device_list = patient_attrs.get("deviceList", {})
        for device_attrs in device_list.get("devices", []):
            device_type = device_attrs["device_type"]
            device_attrs["device_type_id"] = device_type["id"]
            del device_attrs["device_type"]

            device = Device(patient_id=patient_id, **device_attrs)
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

    Args:
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    """
    client = client or global_graph_client()
    patients_query = """
        query getPatientList($patient_cursor: Cursor, $device_cursor: Cursor) {
            org {
                patientAccessList(cursor: $patient_cursor) {
                    pageInfo {
                        endCursor
                    }
                    patientAccess {
                        patient {
                            id
                            name: codeName
                            created_at: createdAt
                            deviceList(cursor: $device_cursor) {
                                pageInfo {
                                    endCursor
                                }
                                devices {
                                    id: deviceShortId
                                    name: alias
                                    created_at: createdAt
                                    device_type: deviceType {
                                        id
                                    }
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
    """

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
                device_type = device_attrs["device_type"]
                device_attrs["device_type_id"] = device_type["id"]
                del device_attrs["device_type"]

                device = Device(patient_id=patient_id, **device_attrs)
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
    Get a patient's device, by the device ID.

    Note that if a Patient object is provided, this function serves
    as a wrapper around Patient.device(). If a patient ID is provided, metadata
    is fetched from the API.

    Args:
        patient: a patient ID or Patient object
        device_id: Device ID
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    """
    if type(patient) is str:
        patient = get_patient(patient_id=patient, client=client)

    return patient.device(device_id=device_id)


def get_patient_devices(
    patient: Union[Patient, str],
    client: Optional[GraphClient] = None,
) -> DeviceSet:
    """
    Get all devices for a patient.

    Note that if a Patient object is provided, this function serves
    as a wrapper around Patient.devices. If a patient ID is provided,
    metadata is fetched from the API.

    Args:
        patient: a patient ID or Patient object
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    """
    if type(patient) is str:
        patient = get_patient(patient_id=patient, client=client)

    return patient.devices


def get_all_devices(
    patients: Union[PatientSet, List[str]] = None,
    client: Optional[GraphClient] = None,
) -> DeviceSet:
    """
    Get a set of all devices belonging to a set of patients. If a specific
    set is not specified, returns all devices belonging to all patients
    in the user's active organization.

    Args:
        patients: a list of patient IDs or a PatientSet
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

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

    return patients.devices
