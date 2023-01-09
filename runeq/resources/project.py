"""
Fetch metadata about projects.

"""

from typing import Iterable, Optional, Type

from .client import GraphClient, global_graph_client
from .common import ItemBase, ItemSet


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
        **attributes
    ):
        """
        Initialize with data.

        Args:
            id: ID of the project
            title: Human-readable name
            status: Status of the project
            type: Type of project. Possible types include: EXPLORATORY,
                CLINICAL_TRIAL,RETROSPECTIVE_STUDY, PROSPECTIVE_STUDY, SANDBOX
            started_at: Time the project started (unix timestamp)
            created_at: Time the project was created (unix timestamp)
            created_by: Display name of who created the project
            updated_at: Time the project was last updated (unix timestamp)
            updated_by: Display name of who updated the project
            **attributes: Other attributes associated with the project

        """
        # Update to include required attributes
        self.title = title
        self.created_at = created_at
        self.started_at = started_at
        self.updated_at = updated_at
        self.created_by = created_by
        self.updated_by = updated_by
        self.status = status
        self.type = type

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
            **attributes,
        )


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


def get_project(
    project_id: str, client: Optional[GraphClient] = None
) -> Project:
    """
    Get the project with the specified ID.

    Args:
        project_id: Project ID
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    """
    client = client or global_graph_client()
    query = """
        query getProject($project_id: ID) {
            project (id: $project_id) {
                id,
                title,
                status,
                description,
                type,
                created_at: createdAt,
                updated_at: updatedAt,
                started_at: startedAt,
                created_by: createdBy,
                updated_by: updatedBy
            }
        }
    """

    result = client.execute(statement=query, project_id=project_id)

    project_attrs = result["project"]
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
            project = Project(**project)
            project_set.add(project)

        # endCursor is None when there are no more pages of data
        next_cursor = project_list.get("pageInfo", {}).get("endCursor")
        if not next_cursor:
            break

    return project_set
