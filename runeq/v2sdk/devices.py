"""
Models for querying device metadata.

"""
from typing import Iterable, Iterator, Optional, Union

from .common import SetMemberBase, QueryBase, SetBase
from .graph.model import GraphID


class DeviceType(SetMemberBase):
    """
    Representational state for a device type.

    """


    def __eq__(self, right):
        """
        Case-insensitive device type name comparison.

        """
        if isinstance(right, str):
            right = right.lower()
            return (
                self.id.lower() == right
                or
                self.display_name.lower() == right
            )
        else:
            return super().__eq__(right)


class Device(SetMemberBase):
    """
    Representational state for a patient device.

    """

    _relations = {
        'deviceType': DeviceType
    }


class DeviceSet(SetBase):
    """
    Representational state for a collection of devices.

    """

    _member = Device
    """
    Type for a member of a device set.

    """

    _patient_id: Optional[GraphID] = None
    """
    The patient, if any, that all devices in this set belong to.

    """


    def __getitem__(self, device_id: str) -> Device:
        """
        Get a device by ID.

        """
        if ',' in device_id:
            # Absolute graph item ID
            key = GraphID(device_id).as_tuple()

        elif self._patient_id:
            # Relative device ID
            if '-' not in device_id:
                device_id = f"device-{device_id}"

            key = (self._patient_id.principal, device_id)

        else:
            raise KeyError(device_id)

        return super().__getitem__(key)


    def ids(self) -> Iterator[Union[str, GraphID]]:
        """
        Iterator over device IDs.

        """
        if self._patient_id:
            # Return relative IDs
            return (
                device.id for device in self._members.values()
            )
        else:
            # Return absolute IDs
            return (
                device._id for device in self._members.values()
            )


class DeviceQuery(QueryBase):
    """
    A query over devices for one or all patients.

    """

    _set = DeviceSet
    """
    Type for a set of devices.

    """


    def __getitem__(self, device_id: str) -> Device:
        """
        Fetch a device by ID.

        Only supported with a patient in context.

        """
        if self._patient:

            if ',' in device_id:
                # Qualified ID: parse and verify
                device_id = GraphID(device_id)

                if device_id.principal != self._patient._id.principal:
                    raise ValueError(
                        "device does not belong to the specified patient")

                device_id = device_id.unqualified

            elif '-' in device_id:
                # Strip resource prefix
                device_id = device_id.split('-', 1)[-1]

            # Load all patient devices and scan for it
            for device in self:
                if device.id == device_id:
                    return device

            raise KeyError(device_id)

        else:
            raise TypeError("no patient specified for device query")


    def __init__(self, session, patient=None):
        """
        Initialize a new query.

        """
        super().__init__(session=session)
        self._patient = patient


    def __iter__(self):
        """
        Iterate over the results.

        The patient and device cache will be used, if caching is enabled.

        """
        sess = self._session
        patient = self._patient

        if patient:
            #
            # Devices of one patient
            #
            if sess._caching:
                # Work from the cache
                if not patient._device_cache._all:
                    patient._device_cache = self.query()

                if sess._now is not None:
                    yield from patient._device_cache.created_before(sess._now)
                else:
                    yield from iter(patient._device_cache)

            else:
                # Stream
                for device_state in self.raw_query():
                    device = Device(device_state)

                    if (sess._now is not None
                            and device.created_at >= sess._now):
                        continue

                    yield device

        else:
            #
            # Iterate devices across all patients
            #
            for patient in sess.patients:
                yield from iter(patient.devices)


    def query(self):
        """
        Execute patient query and return results.

        This method always executes an API query. Use `iter(query)` for
        general use instead.

        """
        result = super().query()

        if self._patient:
            result._patient_id = self._patient._id

        return result


    def raw_query(self) -> Iterable:
        """
        Execute patient devices query and return results.

        This method always executes an API query. Use `iter(devices)` if
        you want to take advantage of caching and `session.freeze_time()`.

        """
        sess = self._session
        patient = self._patient

        if patient:
            #
            # Devices of one patient
            #
            yield from sess.graph.list_patient_devices(patient_id=patient._id)

        else:
            #
            # All devices across all patients
            #
            for patient in sess.patients:
                yield from patient.devices.raw_query()
