from .common import MemberType, MemberBase, MemberSet
from .device import Device, DeviceSet


class Patient(MemberBase):
    """
    Representational state for a Patient.
    """

    member_type = MemberType.PATIENT

    def get_device(device_id: str) -> Device:
        """
        get_device returns the device with the specified device_id.
        """

    def get_devices() -> DeviceSet:
        """
        get_devices returns a set of all devices that belong to the patient.
        """


class PatientSet(MemberSet):
    """
    Representational state for a set of Patients.
    """

    member_type = MemberType.PATIENT

    def get_devices() -> DeviceSet:
        """
        get_devices returns a set of all devices across all patients in this patient set.
        """


def get_patient(patient_id: str) -> Patient:
    """
    get_patient returns the patient with the specified patient_id.
    """


def get_patients() -> PatientSet:
    """
    get_patients returns a set of all patients in the org the user is currently a member of.
    """
