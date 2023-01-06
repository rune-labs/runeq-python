"""
Fetch metadata about projects.

"""

from typing import Iterable, Optional, Type

from .client import GraphClient, global_graph_client
from .common import ItemBase, ItemSet


class Project(ItemBase):
    """
    Metadata for an project.

    """

    def __init__(
        self,
        id: str,
        title: str,
        created_at: float,
        **attributes
    ):
        """
        Initialize with metadata.

        Args:
            id: ID of the project
            title: Human-readable name
            created_at: When the organization was created (unix timestamp)
            **attributes: Other attributes associated with the project

        """
        # Update to include required attributes
        self.title = title
        self.created_at = created_at

        super().__init__(
            id=id,
            title=title,
            created_at=created_at,
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
    query = '''
        query getProject($project_id: ID) {
            project (projectId: $project_id) {
                id
                created_at
                title
                description
                project_status
                project_type
                started_at
                created_by
            }
        }
    '''

    result = client.execute(
        statement=query,
        project_id=project_id
    )

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
    query = '''
        query($cursor: DateTimeUUIDCursor) {
            org {
                id
                projectList(cursor: $cursor) {
                    projects {
                        id,
                        title,
                        status,
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
    '''

    next_cursor = None
    project_set = ProjectSet()

    # Use cursor to page through all org memberships
    while True:
        result = client.execute(
            statement=query,
            cursor=next_cursor
        )
        project_list = result.get("org", {}).get("projectList", {})

        for project in project_list.get("projects", []):
            project = Project(**project)
            project_set.add(project)

        # endCursor is None when there are no more pages of data
        next_cursor = project_list.get("pageInfo", {}).get("endCursor")
        if not next_cursor:
            break

    return project_set
