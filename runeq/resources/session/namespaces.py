import datetime
from datetime import date
from typing import Dict, Iterable, Iterator, List, Literal, Optional, Union

import pandas as pd

from runeq.resources.client import GraphClient, StreamClient, StriveClient
from runeq.resources.event import (
    EventSet,
    get_patient_activity_events,
    get_patient_events,
    get_patient_medication_events,
    get_patient_symptom_events,
    get_patient_wellbeing_events,
)
from runeq.resources.internal import _time_type
from runeq.resources.org import Org, OrgSet, get_org, get_orgs, set_active_org
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
from runeq.resources.project import (
    Project,
    ProjectPatientMetadataSet,
    ProjectSet,
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
    StreamMetadata,
    StreamMetadataSet,
    StreamTypeSet,
    get_all_stream_types,
    get_patient_stream_metadata,
    get_stream_availability_dataframe,
    get_stream_dataframe,
    get_stream_metadata,
)
from runeq.resources.user import User, get_current_user


class OrgNamespace:
    client: GraphClient

    def __init__(self, client: GraphClient):
        self.client = client

    def get_org(self, org_id: str) -> Org:
        return get_org(org_id, client=self.client)

    def get_orgs(self) -> OrgSet:
        return get_orgs(client=self.client)

    def set_active_org(self, org: Union[str, Org]) -> Org:
        return set_active_org(org, client=self.client)


class EventNamespace:
    client: GraphClient

    def __init__(self, client: GraphClient):
        self.client = client

    def get_patient_events(
        self,
        patient_id: str,
        start_time: _time_type,
        end_time: _time_type,
        include_filters: Optional[list] = None,
    ) -> EventSet:
        return get_patient_events(
            patient_id,
            start_time,
            end_time,
            include_filters=include_filters,
            client=self.client,
        )

    def get_patient_activity_events(
        self,
        patient_id: str,
        start_time: _time_type,
        end_time: _time_type,
    ) -> EventSet:
        return get_patient_activity_events(
            patient_id,
            start_time,
            end_time,
            client=self.client,
        )

    def get_patient_medication_events(
        self,
        patient_id: str,
        start_time: _time_type,
        end_time: _time_type,
    ) -> EventSet:
        return get_patient_medication_events(
            patient_id,
            start_time,
            end_time,
            client=self.client,
        )

    def get_patient_symptom_events(
        self,
        patient_id: str,
        start_time: _time_type,
        end_time: _time_type,
    ) -> EventSet:
        return get_patient_symptom_events(
            patient_id,
            start_time,
            end_time,
            client=self.client,
        )

    def get_patient_wellbeing_events(
        self,
        patient_id: str,
        start_time: _time_type,
        end_time: _time_type,
    ) -> EventSet:
        return get_patient_wellbeing_events(
            patient_id,
            start_time,
            end_time,
            client=self.client,
        )


class PatientNamespace:
    client: GraphClient

    def __init__(self, client: GraphClient):
        self.client = client

    def get_patient(self, patient_id: str) -> Patient:
        return get_patient(patient_id, client=self.client)

    def get_all_patients(self) -> PatientSet:
        return get_all_patients(client=self.client)

    def get_device(
        self,
        patient: Union[Patient, str],
        device_id: str,
    ) -> Device:
        return get_device(patient, device_id, client=self.client)

    def get_patient_devices(
        self,
        patient: Union[Patient, str],
    ) -> DeviceSet:
        return get_patient_devices(patient, client=self.client)

    def get_all_devices(
        self,
        patients: Union[PatientSet, List[str]] = None,
    ) -> DeviceSet:
        return get_all_devices(patients, client=self.client)


class ProjectNamespace:
    client: GraphClient

    def __init__(self, client: GraphClient):
        self.client = client

    def get_project(self, project_id: str) -> Project:
        return get_project(project_id, client=self.client)

    def get_projects(self) -> ProjectSet:
        return get_projects(client=self.client)

    def get_project_patients(
        self,
        project_id: str,
    ) -> ProjectPatientMetadataSet:
        return get_project_patients(project_id, client=self.client)

    def get_cohort_patients(
        self,
        cohort_id: str,
    ) -> ProjectPatientMetadataSet:
        return get_cohort_patients(cohort_id, client=self.client)


class SleepNamespace:
    client: StriveClient

    def __init__(self, client: StriveClient):
        self.client = client

    def get_sleep_metrics(
        self,
        patient_id: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        return get_sleep_metrics(
            patient_id,
            start_date,
            end_date,
            client=self.client,
        )


class StreamMetadataNamespace:
    graph_client: GraphClient
    stream_client: StreamClient

    def __init__(self, graph_client: GraphClient, stream_client: StreamClient):
        self.graph_client = graph_client
        self.stream_client = stream_client

    def get_all_stream_types(self) -> StreamTypeSet:
        return get_all_stream_types(client=self.graph_client)

    def get_stream_metadata(
        self,
        stream_ids: Union[str, Iterable[str]],
    ) -> Union[StreamMetadata, StreamMetadataSet]:
        return get_stream_metadata(stream_ids, client=self.graph_client)

    def get_patient_stream_metadata(
        self,
        patient_id: str,
        device_id: Optional[str] = None,
        stream_type_id: Optional[str] = None,
        algorithm: Optional[str] = None,
        category: Optional[str] = None,
        measurement: Optional[str] = None,
        **parameters,
    ) -> StreamMetadataSet:
        return get_patient_stream_metadata(
            patient_id,
            device_id=device_id,
            stream_type_id=stream_type_id,
            algorithm=algorithm,
            category=category,
            measurement=measurement,
            client=self.graph_client,
            **parameters,
        )

    def get_stream_dataframe(
        self,
        stream_ids: Union[str, Iterable[str]],
        start_time: Optional[Union[float, datetime.date]] = None,
        start_time_ns: Optional[int] = None,
        end_time: Optional[Union[float, datetime.date]] = None,
        end_time_ns: Optional[int] = None,
        limit: Optional[int] = None,
        page_token: Optional[str] = None,
        timestamp: Optional[str] = "iso",
        timezone: Optional[int] = None,
        translate_enums: Optional[bool] = True,
    ) -> pd.DataFrame:
        return get_stream_dataframe(
            stream_ids,
            start_time=start_time,
            start_time_ns=start_time_ns,
            end_time=end_time,
            end_time_ns=end_time_ns,
            limit=limit,
            page_token=page_token,
            timestamp=timestamp,
            timezone=timezone,
            translate_enums=translate_enums,
            stream_client=self.stream_client,
            graph_client=self.graph_client,
        )

    def get_stream_availability_dataframe(
        self,
        stream_ids: Union[str, Iterable[str]],
        start_time: Union[float, datetime.date],
        end_time: Union[float, datetime.date],
        resolution: int,
        batch_operation: Optional[str] = None,
        limit: Optional[int] = None,
        page_token: Optional[str] = None,
        timestamp: Optional[str] = "iso",
        timezone: Optional[int] = None,
    ) -> pd.DataFrame:
        return get_stream_availability_dataframe(
            stream_ids,
            start_time=start_time,
            end_time=end_time,
            resolution=resolution,
            batch_operation=batch_operation,
            limit=limit,
            page_token=page_token,
            timestamp=timestamp,
            timezone=timezone,
            stream_client=self.stream_client,
            graph_client=self.graph_client,
        )


class StreamNamespace:
    client: StreamClient

    def __init__(self, client: StreamClient):
        self.client = client

    def get_stream_data(
        self,
        stream_id: str,
        start_time: Optional[_time_type] = None,
        start_time_ns: Optional[int] = None,
        end_time: Optional[_time_type] = None,
        end_time_ns: Optional[int] = None,
        format: Optional[str] = "csv",
        limit: Optional[int] = None,
        page_token: Optional[str] = None,
        timestamp: Optional[str] = "iso",
        timezone: Optional[int] = None,
        timezone_name: Optional[str] = None,
        translate_enums: Optional[bool] = True,
    ) -> Iterator[Union[str, dict]]:
        return get_stream_data(
            stream_id,
            start_time=start_time,
            start_time_ns=start_time_ns,
            end_time=end_time,
            end_time_ns=end_time_ns,
            format=format,
            limit=limit,
            page_token=page_token,
            timestamp=timestamp,
            timezone=timezone,
            timezone_name=timezone_name,
            translate_enums=translate_enums,
            client=self.client,
        )

    def get_stream_availability(
        self,
        stream_ids: Union[str, Iterable[str]],
        start_time: _time_type,
        end_time: _time_type,
        resolution: int,
        batch_operation: Optional[str] = None,
        format: Optional[str] = "csv",
        limit: Optional[int] = None,
        page_token: Optional[str] = None,
        timestamp: Optional[str] = "iso",
        timezone: Optional[int] = None,
        timezone_name: Optional[str] = None,
    ) -> Iterator[Union[str, dict]]:
        return get_stream_availability(
            stream_ids,
            start_time=start_time,
            end_time=end_time,
            resolution=resolution,
            batch_operation=batch_operation,
            format=format,
            limit=limit,
            page_token=page_token,
            timestamp=timestamp,
            timezone=timezone,
            timezone_name=timezone_name,
            client=self.client,
        )

    def get_stream_daily_aggregate(
        self,
        stream_id: str,
        start_time: _time_type,
        resolution: int,
        n_days: int,
    ) -> dict:
        return get_stream_daily_aggregate(
            stream_id,
            start_time,
            resolution,
            n_days,
            client=self.client,
        )

    def get_stream_aggregate_window(
        self,
        stream_id: str,
        start_time: _time_type,
        end_time: _time_type,
        resolution: int,
        aggregate_function: Literal["sum", "mean"],
        timestamp: Optional[str] = "iso",
        timezone: Optional[int] = None,
        timezone_name: Optional[str] = None,
    ) -> dict:
        return get_stream_aggregate_window(
            stream_id,
            start_time=start_time,
            end_time=end_time,
            resolution=resolution,
            aggregate_function=aggregate_function,
            timestamp=timestamp,
            timezone=timezone,
            timezone_name=timezone_name,
            client=self.client,
        )


class UserNamespace:
    client: GraphClient

    def __init__(self, client: GraphClient):
        self.client = client

    def get_current_user(self) -> User:
        return get_current_user(client=self.client)
