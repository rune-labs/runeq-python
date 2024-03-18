"""
Fetch metadata about projects.

"""

from typing import Iterable, Optional, Type

import pandas as pd

from .client import GraphClient, global_graph_client
from .common import ItemBase, ItemSet


class Metric(ItemBase):
    """
    A measurement related to processed patient data. Each metric is related
    to a single processed data type, project, and time interval. These metrics
    are calculated periodically and updated.

    """

    def __init__(
        self,
        id: str,
        type: str,
        data_type: str,
        time_interval: str,
        updated_at: float,
        created_at: float,
        value: Optional[float] = None,
    ):
        """
        Initialize with data.

        Args:
            id: Unique identifier of the patient
            type: Type of measurement/metric. Possible types include:
                TOTAL_HOURS, LATEST_DATA, LAST_UPLOAD
            data_type: Processed stream data type that is being measured.
                Possible data types include:
                APPLEWATCH_SYMPTOM, APPLEWATCH_TREMOR,
                APPLEWATCH_DYSKINESIA, APPLEWATCH_HEART_RATE,
                PERCEPT_TREND_LOG_LFP
            value: Value of the metric (float)
            time_interval: Period over which the metric was calculated.
                Possible time intervals include:
                FOURTEEN_DAYS, NINETY_DAYS, PROJECT_ALL
            created_at: Time patient was added to the cohort (unix timestamp)
            updated_at: Time cohort patient was last updated (unix timestamp)

        """
        self.type = type
        self.data_type = data_type
        self.time_interval = time_interval
        self.created_at = created_at
        self.updated_at = updated_at
        self.value = value

        super().__init__(
            id=id,
            type=type,
            data_type=data_type,
            value=value,
            time_interval=time_interval,
            created_at=created_at,
            updated_at=updated_at,
        )


class MetricSet(ItemSet):
    """
    A collection of Metrics.

    """

    def __init__(self, items: Iterable[Metric] = ()):
        """
        Initialize with Metrics.

        """
        super().__init__(items=items)

    @property
    def _item_class(self) -> Type[ItemBase]:
        """
        Instance type of items in this set.

        """
        return Metric


class ProjectPatientMetadata(ItemBase):
    """
    A patient who has been placed within a project and is now
    associated with the project.

    """

    def __init__(
        self,
        id: str,
        updated_at: float,
        created_at: float,
        created_by: str,
        updated_by: str,
        metrics: MetricSet,
        **attributes
    ):
        """
        Initialize with data.

        Args:
            id: Patient ID of the patient in the cohort
            created_at: Time patient was added to the project (unix timestamp)
            created_by: Display name of who added the patient to the project
            updated_at: Time project patient was last updated (unix timestamp)
            updated_by: Display name of who updated the project patient record
            metrics: Project data metrics related to the patient's data
            **attributes: Other attributes associated with the project

        """
        self.created_at = created_at
        self.updated_at = updated_at
        self.created_by = created_by
        self.updated_by = updated_by
        self.metrics = metrics

        super().__init__(
            id=id,
            created_at=created_at,
            updated_at=updated_at,
            created_by=created_by,
            updated_by=updated_by,
            metrics=metrics,
            **attributes,
        )

    def to_dict(self) -> dict:
        """
        Dictionary representation of the Project Patient attributes.

        """
        attrs = self._attributes.copy()
        attrs["metrics"] = self.metrics.to_list()
        return attrs

    def get_patient_metadata_dataframe(self) -> pd.DataFrame:
        """
        Returns a new dataframe displaying the patient's metadata.

        """
        column_name_map = {
            "type": "metric_type",
            "data_type": "metric_data_type",
            "value": "metric_value",
            "time_interval": "metric_time_interval",
            "created_at": "metric_created_at",
            "updated_at": "metric_updated_at",
            "id": "metric_id",
        }
        metadata_obj = self.to_dict()
        metadata_df = pd.DataFrame(metadata_obj).rename(
            columns={"code_name": "project_patient_code_name"}
        )

        return pd.concat(
            [
                metadata_df.drop("metrics", axis=1),
                pd.DataFrame(metadata_df["metrics"].tolist()).rename(
                    columns=column_name_map
                ),
            ],
            axis=1,
        )


class CohortPatientMetadata(ProjectPatientMetadata):
    """
    Cohort related information about a patient contained in a cohort.

    """

    def __init__(
        self,
        id: str,
        updated_at: float,
        created_at: float,
        created_by: str,
        updated_by: str,
        metrics: MetricSet,
        **attributes
    ):
        """
        Initialize with data.

        Args:
            id: Patient ID of the patient in the cohort
            created_at: Time patient was added to the cohort (unix timestamp)
            created_by: Display name of who added the patient to the cohort
            updated_at: Time cohort patient was last updated (unix timestamp)
            updated_by: Display name of who updated the cohort patient record
            metrics: Project data metrics related to the patient's data
            **attributes: Other attributes associated with the cohort

        """
        super().__init__(
            id=id,
            created_at=created_at,
            updated_at=updated_at,
            created_by=created_by,
            updated_by=updated_by,
            metrics=metrics,
            **attributes,
        )


class CohortPatientMetadataSet(ItemSet):
    """
    A collection of CohortPatientMetadata.

    """

    def __init__(self, items: Iterable[CohortPatientMetadata] = ()):
        """
        Initialize with CohortPatientMetadata.

        """
        super().__init__(items=items)

    @property
    def _item_class(self) -> Type[ItemBase]:
        """
        Instance type of items in this set.

        """
        return CohortPatientMetadata


class ProjectPatientMetadataSet(ItemSet):
    """
    A collection of ProjectPatientMetadata.

    """

    def __init__(self, items: Iterable[ProjectPatientMetadata] = ()):
        """
        Initialize with ProjectPatientMetadata.

        """
        super().__init__(items=items)

    @property
    def _item_class(self) -> Type[ItemBase]:
        """
        Instance type of items in this set.

        """
        return ProjectPatientMetadata


class Cohort(ItemBase):
    """
    A generic sub-container for a group of patients within a project.

    A cohort is a generic container within a project for a group of patients
    with workflow-related metadata: description, milestones dates,
    metrics, etc.

    A single project can have multiple cohorts.

    """

    def __init__(
        self,
        id: str,
        title: str,
        updated_at: float,
        created_at: float,
        created_by: str,
        updated_by: str,
        **attributes
    ):
        """
        Initialize with data.

        Args:
            id: ID of the project
            title: Human-readable name
            created_at: Time the cohort was created (unix timestamp)
            created_by: Display name of who created the cohort
            updated_at: Time the cohort was last updated (unix timestamp)
            updated_by: Display name of who updated the cohort
            **attributes: Other attributes associated with the cohort

        """
        self.title = title
        self.created_at = created_at
        self.updated_at = updated_at
        self.created_by = created_by
        self.updated_by = updated_by

        super().__init__(
            id=id,
            title=title,
            created_at=created_at,
            updated_at=updated_at,
            created_by=created_by,
            updated_by=updated_by,
            **attributes,
        )


class CohortSet(ItemSet):
    """
    A collection of Cohorts.

    """

    def __init__(self, items: Iterable[Cohort] = ()):
        """
        Initialize with Cohorts.

        """
        super().__init__(items=items)

    @property
    def _item_class(self) -> Type[ItemBase]:
        """
        Instance type of items in this set.

        """
        return Cohort


class Project(ItemBase):
    """
    Metadata for a project.

    A project is a generic container for a group of patients
    with workflow-related metadata: status, project type, description,
    milestones dates, etc. Data availability QC metrics are computed
    on a regular basis for all patients in a project.

    """

    def __init__(
        self,
        id: str,
        title: str,
        status: str,
        type: str,
        started_at: float,
        updated_at: float,
        created_at: float,
        created_by: str,
        updated_by: str,
        cohorts: CohortSet(),
        **attributes
    ):
        """
        Initialize with data.

        Args:
            id: ID of the project
            title: Human-readable name
            status: Status of the project
            type: Type of project. Possible types include:
                EXPLORATORY, CLINICAL_TRIAL,RETROSPECTIVE_STUDY,
                PROSPECTIVE_STUDY, SANDBOX
            started_at: Time the project started (unix timestamp)
            created_at: Time the project was created (unix timestamp)
            created_by: Display name of who created the project
            updated_at: Time the project was last updated (unix timestamp)
            updated_by: Display name of who updated the project
            cohorts: Sub-containers of patients in a project
            **attributes: Other attributes associated with the project

        """
        self.title = title
        self.created_at = created_at
        self.started_at = started_at
        self.updated_at = updated_at
        self.created_by = created_by
        self.updated_by = updated_by
        self.status = status
        self.type = type
        self.cohorts = cohorts

        super().__init__(
            id=id,
            title=title,
            created_at=created_at,
            started_at=started_at,
            updated_at=updated_at,
            created_by=created_by,
            updated_by=updated_by,
            status=status,
            type=type,
            cohorts=cohorts,
            **attributes,
        )

    def to_dict(self) -> dict:
        """
        Dictionary representation of the Project attributes.

        """
        attrs = self._attributes.copy()
        attrs["cohorts"] = self.cohorts.to_list()

        return attrs


class ProjectSet(ItemSet):
    """
    A collection of Projects.

    """

    def __init__(self, items: Iterable[Project] = ()):
        """
        Initialize with Projects.

        """
        super().__init__(items=items)

    @property
    def _item_class(self) -> Type[ItemBase]:
        """
        Instance type of items in this set.

        """
        return Project


def get_project(project_id: str, client: Optional[GraphClient] = None) -> Project:
    """
    Get the project with the specified ID.

    Args:
        project_id: Project ID
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    """
    client = client or global_graph_client()
    query = """
        query getProject($id: ID) {
            project (id: $id) {
                id,
                title,
                status,
                description,
                type,
                cohortList {
                    cohorts {
                        id,
                        title,
                        description,
                        created_at: createdAt,
                        updated_at: updatedAt,
                        created_by: createdBy,
                        updated_by: updatedBy,
                    }
                },
                created_at: createdAt,
                updated_at: updatedAt,
                started_at: startedAt,
                created_by: createdBy,
                updated_by: updatedBy
            }
        }
    """

    result = client.execute(statement=query, id=project_id)

    project_attrs = result["project"]

    # Move cohorts to attribute level
    cohorts = project_attrs.get("cohortList", {}).get("cohorts", [])
    cohort_set = CohortSet()

    for cohort in cohorts:
        cohort_obj = Cohort(**cohort)
        cohort_set.add(cohort_obj)

    project_attrs["cohorts"] = cohort_set
    del project_attrs["cohortList"]

    return Project(**project_attrs)


def get_projects(client: Optional[GraphClient] = None) -> ProjectSet:
    """
    Get all the projects that the current user has access to.

    Args:
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    """
    client = client or global_graph_client()
    query = """
        query($cursor: DateTimeUUIDCursor) {
            org {
                id
                projectList(cursor: $cursor) {
                    projects {
                        id,
                        title,
                        status,
                        description,
                        type,
                        cohortList {
                            cohorts {
                                id,
                                title,
                                description,
                                created_at: createdAt,
                                updated_at: updatedAt,
                                created_by: createdBy,
                                updated_by: updatedBy,
                            }
                        },
                        created_at: createdAt,
                        updated_at: updatedAt,
                        started_at: startedAt,
                        created_by: createdBy,
                        updated_by: updatedBy
                    }
                    pageInfo {
                        endCursor
                    }
                }
            }
        }
    """

    next_cursor = None
    project_set = ProjectSet()

    # Use cursor to page through all projects
    while True:
        result = client.execute(statement=query, cursor=next_cursor)
        project_list = result.get("org", {}).get("projectList", {})

        for project in project_list.get("projects", []):
            cohorts = project.get("cohortList", {}).get("cohorts", [])
            cohort_set = CohortSet()

            for cohort in cohorts:
                cohort_obj = Cohort(**cohort)
                cohort_set.add(cohort_obj)

            project["cohorts"] = cohort_set
            del project["cohortList"]

            project = Project(**project)
            project_set.add(project)

        # endCursor is None when there are no more pages of data
        next_cursor = project_list.get("pageInfo", {}).get("endCursor")
        if not next_cursor:
            break

    return project_set


def _parse_patient_metrics(metrics: dict) -> MetricSet:
    """
    Helper function that intakes a metric dictionary and outputs a metric set.

    """
    metric_set = MetricSet()

    for metric in metrics:
        metric = Metric(**metric)
        metric_set.add(metric)

    return metric_set


def get_project_patients(
    project_id: str,
    client: Optional[GraphClient] = None,
) -> ProjectPatientMetadataSet:
    """
    Get all patients in a project and their associated project data metrics.

    Args:
        project_id: ID of the project
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    """
    client = client or global_graph_client()
    project_patients_query = """
        query($id: ID, $cursorInput: CursorInput) {
            project(id: $id) {
                projectPatientList(
                    cursorInput: $cursorInput
                ){
                    projectPatients{
                        patient {
                            id
                        },
                        metricList {
                            metrics {
                                id,
                                updated_at: updatedAt,
                                created_at: createdAt,
                                type,
                                data_type: dataType,
                                value,
                                time_interval: timeInterval
                            }
                        },
                        code_name: codeName,
                        created_at: createdAt,
                        updated_at: updatedAt,
                        created_by: createdBy,
                        updated_by: updatedBy,
                    },
                    pageInfo{
                        codeNameEndCursor
                    }
                },
            }
        }
    """

    cursor_input = None
    project_patient_set = ProjectPatientMetadataSet()

    # Use cursor to page through all patients
    while True:
        result = client.execute(
            statement=project_patients_query,
            id=project_id,
            cursor_input=cursor_input,
        )

        # Loop over all project patients
        patient_list = result.get("project", {}).get("projectPatientList")

        for patient_info in patient_list.get("projectPatients", []):
            patient_attrs = patient_info

            # Move patient id to top level attribute
            patient_attrs["id"] = patient_attrs.get("patient").get("id")
            del patient_attrs["patient"]

            metrics = patient_attrs.get("metricList").get("metrics")
            patient_attrs["metrics"] = _parse_patient_metrics(metrics)
            del patient_attrs["metricList"]

            patient = ProjectPatientMetadata(**patient_attrs)
            project_patient_set.add(patient)

        # cursor is None when there are no more pages of project patients.
        cursor = patient_list.get("pageInfo", {}).get("codeNameEndCursor")
        if not cursor:
            break

        cursor_input = {"codeNameCursor": cursor}

    return project_patient_set


def get_cohort_patients(
    cohort_id: str,
    client: Optional[GraphClient] = None,
) -> CohortPatientMetadataSet:
    """
    Get all patients in a cohort.

    Args:
        cohort_id: ID of the cohort
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    """
    client = client or global_graph_client()
    cohort_patients_query = """
        query($id: ID, $cursorInput: CursorInput) {
            cohort(id: $id) {
                id,
                cohortPatientList(cursorInput: $cursorInput) {
                    cohortPatients {
                        patient {
                            id
                        }
                        metricList {
                            metrics {
                                id,
                                type,
                                data_type: dataType,
                                value,
                                time_interval: timeInterval,
                                created_at: createdAt,
                                updated_at: updatedAt
                            }
                        }
                        code_name: codeName,
                        created_at: createdAt,
                        updated_at: updatedAt,
                        created_by: createdBy,
                        updated_by: updatedBy,
                    }
                    pageInfo {
                        codeNameEndCursor
                    }
                }
            }
        }
    """
    cursor_input = None
    cohort_patient_set = CohortPatientMetadataSet()

    while True:
        result = client.execute(
            statement=cohort_patients_query,
            id=cohort_id,
            cursor_input=cursor_input,
        )

        cohort_patient_list = result.get("cohort").get("cohortPatientList", {})
        cohort_patients = cohort_patient_list.get("cohortPatients", [])

        for patient_info in cohort_patients:
            patient_attrs = patient_info

            # Move patient id to top level attribute
            patient_attrs["id"] = patient_attrs.get("patient").get("id")
            del patient_attrs["patient"]

            metrics = patient_attrs.get("metricList", {}).get("metrics", [])
            patient_attrs["metrics"] = _parse_patient_metrics(metrics)
            del patient_attrs["metricList"]

            patient = CohortPatientMetadata(**patient_attrs)
            cohort_patient_set.add(patient)

        cursor = cohort_patient_list.get("pageInfo", {}).get("codeNameEndCursor")

        if not cursor:
            break

        cursor_input = {"codeNameCursor": cursor}

    return cohort_patient_set
