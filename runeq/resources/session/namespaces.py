from functools import wraps
from typing import Any

from runeq.resources.client import GraphClient, StreamClient, StriveClient
from runeq.resources.event import (
    get_patient_activity_events,
    get_patient_events,
    get_patient_medication_events,
    get_patient_symptom_events,
    get_patient_wellbeing_events,
)
from runeq.resources.org import get_org, get_orgs, set_active_org
from runeq.resources.patient import (
    get_all_devices,
    get_all_patients,
    get_device,
    get_patient,
    get_patient_devices,
)
from runeq.resources.project import (
    get_cohort_patients,
    get_project,
    get_project_patients,
    get_projects,
)
from runeq.resources.sleep import get_sleep_metrics
from runeq.resources.stream import (
    get_stream_aggregate_window,
    get_stream_availability,
    get_stream_daily_aggregate,
    get_stream_data,
)
from runeq.resources.stream_metadata import (
    get_all_stream_types,
    get_patient_stream_metadata,
    get_stream_availability_dataframe,
    get_stream_dataframe,
    get_stream_metadata,
)


def inject_client(cls_inst):
    for name, func in type(cls_inst).__dict__.items():
        if callable(func) and not name.startswith("_"):

            def _make_wrapper(f):
                @wraps(f)
                def wrapper(*args, **kwargs):
                    return f(*args, **kwargs, client=cls_inst.client)

                return wrapper

            setattr(cls_inst, name, _make_wrapper(func))


class Injectable:
    client: Any

    def __init__(self, client: Any):
        self.client = client

        inject_client(self)


class OrgNamespace(Injectable):
    get_org: get_org = get_org
    get_orgs: get_orgs = get_orgs
    set_active_org: set_active_org = set_active_org

    client: GraphClient


class EventNamespace(Injectable):
    get_patient_events: get_patient_events = get_patient_events
    get_patient_activity_events: get_patient_activity_events = (
        get_patient_activity_events
    )
    get_patient_medication_events: get_patient_medication_events = (
        get_patient_medication_events
    )
    get_patient_symptom_events: get_patient_symptom_events = get_patient_symptom_events
    get_patient_wellbeing_events: get_patient_wellbeing_events = (
        get_patient_wellbeing_events
    )

    client: GraphClient


class PatientNamespace(Injectable):
    get_patient: get_patient = get_patient
    get_all_patients: get_all_patients = get_all_patients
    get_device: get_device = get_device
    get_patient_devices: get_patient_devices = get_patient_devices
    get_all_devices: get_all_devices = get_all_devices

    client: GraphClient


class ProjectNamespace(Injectable):
    get_project: get_project = get_project
    get_projects: get_projects = get_projects
    get_project_patients: get_project_patients = get_project_patients
    get_cohort_patients: get_cohort_patients = get_cohort_patients

    client: GraphClient


class SleepNamespace(Injectable):
    get_sleep_metrics: get_sleep_metrics = get_sleep_metrics

    client: StriveClient


class StreamMetadataNamespace(Injectable):
    get_all_stream_types: get_all_stream_types = get_all_stream_types
    get_stream_metadata: get_stream_metadata = get_stream_metadata
    get_patient_stream_metadata: get_patient_stream_metadata = (
        get_patient_stream_metadata
    )
    get_stream_dataframe: get_stream_dataframe = get_stream_dataframe
    get_stream_availability_dataframe: get_stream_availability_dataframe = (
        get_stream_availability_dataframe
    )

    client: GraphClient


class StreamNamespace(Injectable):
    get_stream_data: get_stream_data = get_stream_data
    get_stream_availability: get_stream_availability = get_stream_availability
    get_stream_daily_aggregate: get_stream_daily_aggregate = get_stream_daily_aggregate
    get_stream_aggregate_window: get_stream_aggregate_window = (
        get_stream_aggregate_window
    )

    client: StreamClient
