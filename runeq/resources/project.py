"""
Fetch metadata about projects.

"""

from typing import Iterable, Optional, Type

from .client import GraphClient, global_graph_client
from .common import ItemBase, ItemSet
from .org import Org


class ProjectPatientMetadata(ItemBase):
    """
    A patient who has been placed within a project and is now
    associated with the project.

    """

    def __init__(
        self,
        id: str,
        project_code_name: str,
        start_time: Optional[float],
        end_time: Optional[float],
        updated_at: float,
        created_at: float,
        created_by: str,
        updated_by: str,
        **attributes,
    ):
        """
        Initialize with data.

        Args:
            id: Patient ID
            project_code_name: Code name of the patient within the project
            start_time: The project start time for the patient (unix timestamp)
            end_time: The project end time for the patient (unix timestamp)
            created_at: Time patient was added to the project (unix timestamp)
            created_by: Display name of who added the patient to the project
            updated_at: Time project patient was last updated (unix timestamp)
            updated_by: Display name of who updated the project patient record
            **attributes: Other attributes associated with the project

        """
        self.start_time = start_time
        self.end_time = end_time
        self.created_at = created_at
        self.updated_at = updated_at
        self.created_by = created_by
        self.updated_by = updated_by
        self.project_code_name = project_code_name

        super().__init__(
            id=id,
            project_code_name=project_code_name,
            start_time=start_time,
            end_time=end_time,
            created_at=created_at,
            updated_at=updated_at,
            created_by=created_by,
            updated_by=updated_by,
            **attributes,
        )

    def __repr__(self):
        """
        Override the item representation.

        """
        return (
            f"{self.__class__.__name__}"
            f'(patient_id="{self.id}", project_code_name="{self.project_code_name}")'
        )

    def to_dict(self) -> dict:
        """
        Dictionary representation of the Project Patient attributes.

        """
        attrs = self._attributes.copy()
        return attrs


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
        **attributes,
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

    def __repr__(self):
        """
        Override the item representation.

        """
        return f"{self.__class__.__name__}" f'(id="{self.id}", title="{self.title}")'


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
    milestones dates, etc.

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
        cohorts: CohortSet,
        **attributes,
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

    def __repr__(self):
        """
        Override the item representation.

        """
        return f"{self.__class__.__name__}" f'(id="{self.id}", title="{self.title}")'

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


def get_project_patients(
    project_id: str,
    client: Optional[GraphClient] = None,
) -> ProjectPatientMetadataSet:
    """
    Get all patients in a project.

    Args:
        project_id: ID of the project
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    """
    client = client or global_graph_client()
    project_patients_query = """
        query($id: ID, $cursorInput: CursorInput) {
            project(id: $id) {
                organization_id: organizationId,
                projectPatientList(
                    cursorInput: $cursorInput
                ){
                    projectPatients{
                        patient {
                            id
                            patientAccessList {
                                patientAccess {
                                    org {
                                        id
                                    }
                                    start_time: startTime
                                    end_time: endTime
                                }
                            }
                        },
                        project_code_name: codeName,
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

        # Fetch the project organization id and normalize it
        project_org_id = Org.normalize_id(
            org_id=result.get("project", {}).get("organization_id")
        )

        # Loop over all project patients
        patient_list = result.get("project", {}).get("projectPatientList")

        for patient_info in patient_list.get("projectPatients", []):
            patient_attrs = patient_info

            # Move patient id to top level attribute
            patient_attrs["id"] = patient_attrs.get("patient").get("id")

            patient_access_list = (
                patient_attrs.get("patient", {})
                .get("patientAccessList", {})
                .get("patientAccess", [])
            )
            for patient_access in patient_access_list:
                # Fetch the patient access organization id and normalize it. Start/end times are set at the org level, so we
                # only need to parse the start/end times for the patient access record for the org that matches the project org id.
                patient_access_org_id = Org.normalize_id(
                    org_id=patient_access.get("org", {}).get("id")
                )
                if patient_access_org_id == project_org_id:
                    patient_attrs["start_time"] = patient_access.get("start_time")
                    patient_attrs["end_time"] = patient_access.get("end_time")
                    break

            del patient_attrs["patient"]

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
) -> ProjectPatientMetadataSet:
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
                organization_id: organizationId,
                cohortPatientList(cursorInput: $cursorInput) {
                    cohortPatients {
                        patient {
                            id
                            patientAccessList {
                                patientAccess {
                                    org {
                                        id
                                    }
                                    start_time: startTime
                                    end_time: endTime
                                }
                            }
                        }
                        project_code_name: codeName,
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
    cohort_patient_set = ProjectPatientMetadataSet()

    while True:
        result = client.execute(
            statement=cohort_patients_query,
            id=cohort_id,
            cursor_input=cursor_input,
        )

        cohort_patient_list = result.get("cohort").get("cohortPatientList", {})
        cohort_patients = cohort_patient_list.get("cohortPatients", [])

        # Fetch the cohort organization id and normalize it
        cohort_org_id = Org.normalize_id(
            org_id=result.get("cohort", {}).get("organization_id")
        )

        for patient_info in cohort_patients:
            patient_attrs = patient_info

            # Move patient id to top level attribute
            patient_attrs["id"] = patient_attrs.get("patient").get("id")

            patient_access_list = (
                patient_attrs.get("patient", {})
                .get("patientAccessList", {})
                .get("patientAccess", [])
            )
            for patient_access in patient_access_list:
                # Fetch the patient access organization id and normalize it. Start/end times are set at the org level, so we
                # only need to parse the start/end times for the patient access record for the org that matches the cohort org id.
                patient_access_org_id = Org.normalize_id(
                    org_id=patient_access.get("org", {}).get("id")
                )
                if patient_access_org_id == cohort_org_id:
                    patient_attrs["start_time"] = patient_access.get("start_time")
                    patient_attrs["end_time"] = patient_access.get("end_time")
                    break

            del patient_attrs["patient"]

            patient = ProjectPatientMetadata(**patient_attrs)
            cohort_patient_set.add(patient)

        cursor = cohort_patient_list.get("pageInfo", {}).get("codeNameEndCursor")

        if not cursor:
            break

        cursor_input = {"codeNameCursor": cursor}

    return cohort_patient_set
