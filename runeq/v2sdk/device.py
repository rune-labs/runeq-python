from .common import MemberType, MemberBase, MemberSet


class Device(MemberBase):
    """
    Representational state for a Device.
    """

    member_type = MemberType.DEVICE


class DeviceSet(MemberSet):
    """
    Representational state for a set of Devices.
    """

    member_type = MemberType.DEVICE


def get_device(device_id: str) -> Device:
    """
    get_device returns the device with the specified device_id.
    """


def get_all_patient_devices() -> DeviceSet:
    """
    get_all_patient_devices returns a set of all devices across all patients
    in the org the user is currently a member of.
    """
