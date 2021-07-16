"""
Models for querying patient metadata.

"""
from typing import Iterable

from .common import SetMemberBase, QueryBase, SetBase
from .devices import DeviceQuery, DeviceSet
from .graph.model import GraphID


def _patient_graph_id(patient_id: str) -> str:
    """
    Qualify a patient ID for use in the Graph API.

    """
    if '-' not in patient_id:
        patient_id = f"patient-{patient_id}"

    if ',' not in patient_id:
        patient_id = f"{patient_id},patient"

    return patient_id


class Patient(SetMemberBase):
    """
    Representational state for a patient.

    """


    def __init__(self, res, session):
        """
        Initialize a patient representation, connected to a session for
        further active record querying.

        """
        super().__init__(res)
        self._session = session
        self._device_cache = DeviceSet()


    @property
    def devices(self) -> DeviceQuery:
        """
        Begin a query over this patient's registered devices.

        """
        return DeviceQuery(session=self._session, patient=self)


class PatientSet(SetBase):
    """
    Representational state for a collection of patients.

    """

    _member = Patient


    def __getitem__(self, patient_id: str) -> Patient:
        """
        Get a patient by ID.

        """
        return super().__getitem__(_patient_graph_id(patient_id))


class PatientsQuery(QueryBase):
    """
    A query over registered patients.

    """

    _set = PatientSet


    def __getitem__(self, patient_id: str) -> Patient:
        """
        Fetch a patient by ID.

        """
        sess = self._session

        try:
            return sess._patient_cache[patient_id]

        except KeyError:
            patient = Patient(
                sess.graph.fetch_patient(GraphID(patient_id, 'patient')),
                session=sess
            )
            sess._patient_cache.add(patient)
            return patient


    def __iter__(self):
        """
        Execute the query and return an iterator over the results.

        """
        sess = self._session

        if sess._caching:
            #
            # Use patient cache
            #
            if not sess._patient_cache._all:
                sess._patient_cache = self.query()

            if sess._now is not None:
                yield from sess._patient_cache.created_before(sess._now)
            else:
                yield from iter(sess._patient_cache)

        else:
            #
            # Iterate over paginated set, only buffering one page at a time
            #
            for patient_state in self.raw_query():
                patient = Patient(patient_state, session=sess)

                if sess._now is not None and patient.created_at >= sess._now:
                    continue

                yield patient


    def raw_query(self) -> Iterable:
        """
        Query patient state from the API.

        """
        return self._session.graph.list_patients()
