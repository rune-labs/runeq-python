"""
Tests for fetching project data.

"""
from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import GraphClient
from runeq.resources.project import Project, get_project, get_projects


class TestProject(TestCase):
    """
    Unit tests for the Project class.

    """
    def setUp(self):
        """
        Set up mock graph client for testing.

        """
        self.mock_client = GraphClient(
            Config(client_key_id="test", client_access_key="config")
        )

    def test_attributes(self):
        """
        Test attributes for an initialized Project.

        """
        test_project = Project(
            id="proj1-id",
            created_at=1630515986.9949625,
            updated_at=1630515986.9949625,
            title="Project 1",
            description="Test description.",
            created_by="user-1",
            updated_by="user-1",
            started_at=1630515986.9949625,
            status="ACTIVE",
            type="SANDBOX",
        )

        self.assertEqual("proj1-id", test_project.id)
        self.assertEqual(1630515986.9949625, test_project.created_at)
        self.assertEqual("Project 1", test_project.title)
        self.assertEqual(1630515986.9949625, test_project.updated_at)
        self.assertEqual("user-1", test_project.created_by)
        self.assertEqual("user-1", test_project.updated_by)
        self.assertEqual("ACTIVE", test_project.status)
        self.assertEqual("SANDBOX", test_project.type)

    def test_get_project(self):
        """
        Test get project for specified project_id.

        """
        self.mock_client.execute = mock.Mock()
        example_project = {
            "id": "proj1-id",
            "created_at": 1630515986.9949625,
            "updated_at": 1630515986.9949625,
            "title": "Project 1",
            "description": "Test description.",
            "created_by": "user-id-1",
            "updated_by": "user-id-1",
            "started_at": 1630515986.9949625,
            "status": "ACTIVE",
            "type": "SANDBOX",
        }

        self.mock_client.execute.side_effect = [{"project": example_project}]

        project = get_project("proj1-id", client=self.mock_client)

        self.assertEqual(
            example_project,
            project.to_dict(),
        )

    def test_get_projects_basic(self):
        """
        Test get projects for the initialized user.

        """
        self.mock_client.execute = mock.Mock()
        projects_expected = [
            {
                "id": "proj1-id",
                "created_at": 1630515986.9949625,
                "title": "Project 1",
                "description": "Test description.",
                "created_by": "user-id-1",
                "started_at": 1630515986.9949625,
                "status": "ACTIVE",
                "updated_at": 1630515986.9949625,
                "type": "SANDBOX",
                "updated_by": "user-id-1",
            },
            {
                "id": "proj2-id",
                "created_at": 1630517987.9949625,
                "title": "Project 2",
                "description": "Test description 2.",
                "created_by": "user-id-2",
                "started_at": 1630517986.9949625,
                "updated_at": 1630515986.9949625,
                "status": "ACTIVE",
                "type": "SANDBOX",
                "updated_by": "user-id-1",
            },
            {
                "id": "proj3-id",
                "created_at": 1630519988.9949625,
                "title": "Project 3",
                "description": "Test description 3.",
                "created_by": "user-id-3",
                "started_at": 1630519986.9949625,
                "updated_at": 1630515986.9949625,
                "status": "ACTIVE",
                "type": "SANDBOX",
                "updated_by": "user-id-1",
            },
        ]
        self.mock_client.execute.return_value = {
            "org": {
                "id": "org-rune,org",
                "projectList": {
                    "projects": projects_expected,
                    "pageInfo": {"endCursor": None},
                },
            }
        }

        projects = get_projects(client=self.mock_client)

        self.assertEqual(
            projects_expected,
            projects.to_list(),
        )

    def test_get_projects_pagination(self):
        """
        Test get projects for the initialized user, where the user has to
        page through projects.

        """
        project_1 = {
            "id": "proj1-id",
            "created_at": 1630515986.9949625,
            "updated_at": 1630515986.9949625,
            "title": "Project 1",
            "description": "Test description.",
            "created_by": "user-id-1",
            "started_at": 1630515986.9949625,
            "status": "ACTIVE",
            "type": "SANDBOX",
            "created_by": "user-id-1",
            "updated_by": "user-id-1",
        }
        project_2 = {
            "id": "proj2-id",
            "created_at": 1630517986.9949625,
            "updated_at": 1630515986.9949625,
            "title": "Project 2",
            "description": "Test description 2.",
            "created_by": "user-id-2",
            "started_at": 1630517986.9949625,
            "status": "ACTIVE",
            "type": "SANDBOX",
            "updated_by": "user-id-1",
        }
        project_3 = {
            "id": "proj3-id",
            "created_at": 1630519986.9949625,
            "updated_at": 1630515986.9949625,
            "title": "Project 3",
            "description": "Test description 3.",
            "created_by": "user-id-3",
            "started_at": 1630519986.9949625,
            "status": "ACTIVE",
            "type": "SANDBOX",
            "updated_by": "user-id-1",
        }

        self.mock_client.execute = mock.Mock()
        self.mock_client.execute.side_effect = [
            {
                "org": {
                    "id": "org-rune,org",
                    "projectList": {
                        "projects": [project_1, project_2],
                        "pageInfo": {"endCursor": "test_check_next"},
                    },
                }
            },
            {
                "org": {
                    "id": "org-rune,org",
                    "projectList": {
                        "projects": [project_3],
                        "pageInfo": {"endCursor": None},
                    },
                }
            },
        ]

        projects = get_projects(client=self.mock_client)

        self.assertEqual(
            [project_1, project_2, project_3],
            projects.to_list(),
        )
