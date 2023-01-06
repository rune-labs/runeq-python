"""
Tests for fetching project data.

"""
from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import GraphClient
from runeq.resources.project import Project, get_project, get_projects
from runeq.resources.client import initialize


class TestProject(TestCase):
    """
    Unit tests for the Project class.

    """

    def setUp(self):
        """
        Set up mock graph client for testing.

        """
        self.mock_client = GraphClient(
            Config(
                client_key_id="test",
                client_access_key="config"
            )
        )

    def test_attributes(self):
        """
        Test attributes for an initialized Project.

        """
        test_org = Project(
            id="project1-id",
            created_at=1629300943.9179766,
            title="project1",
        )

        self.assertEqual("project1-id", test_org.id)
        self.assertEqual(1629300943.9179766, test_org.created_at)
        self.assertEqual("project1", test_org.title)

    def test_get_project(self):
        """
        Test get project for specified project_id.

        """
        self.mock_client.execute = mock.Mock()
        example_project = {
            "id": "proj1-id",
            "created_at": 1630515986.9949625,
            "title": "Project 1",
            "description": "Test description.",
            "created_by": "user-id-1",
            "started_at": 1630515986.9949625,
            "status": "ACTIVE",
            "project_type": "SANDBOX"
        }

        self.mock_client.execute.side_effect = [
            {
                "project": example_project
            }
        ]

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
        self.mock_client.execute.return_value = {
            'org': {
                'id': 'org-rune,org', 
                'projectList': {
                    'projects': [
                        {
                            "id": "proj1-id",
                            "created_at": 1630515986.9949625,
                            "title": "Project 1",
                            "description": "Test description.",
                            "created_by": "user-id-1",
                            "started_at": 1630515986.9949625,
                            "status": "ACTIVE",
                            "project_type": "SANDBOX"
                        },
                        {
                            "id": "proj2-id",
                            "created_at": 1630517986.9949625,
                            "title": "Project 2",
                            "description": "Test description 2.",
                            "created_by": "user-id-2",
                            "started_at": 1630517986.9949625,
                            "status": "ACTIVE",
                            "project_type": "SANDBOX"

                        },
                        {
                            "id": "proj3-id",
                            "created_at": 1630519986.9949625,
                            "title": "Project 3",
                            "description": "Test description 3.",
                            "created_by": "user-id-3",
                            "started_at": 1630519986.9949625,
                            "status": "ACTIVE",
                            "project_type": "SANDBOX"
                        },
                    ],
                    'pageInfo': {
                        'endCursor': None
                    }
                }
            }
        }

        projects = get_projects(client=self.mock_client)

        self.assertEqual(
            [
                {
                    "id": "proj1-id",
                    "created_at": 1630515986.9949625,
                    "title": "Project 1",
                    "description": "Test description.",
                    "created_by": "user-id-1",
                    "started_at": 1630515986.9949625,
                    "status": "ACTIVE",
                    "project_type": "SANDBOX"
                },
                {
                    "id": "proj2-id",
                    "created_at": 1630517986.9949625,
                    "title": "Project 2",
                    "description": "Test description 2.",
                    "created_by": "user-id-2",
                    "started_at": 1630517986.9949625,
                    "status": "ACTIVE",
                    "project_type": "SANDBOX"
                },
                {
                    "id": "proj3-id",
                    "created_at": 1630519986.9949625,
                    "title": "Project 3",
                    "description": "Test description 3.",
                    "created_by": "user-id-3",
                    "started_at": 1630519986.9949625,
                    "status": "ACTIVE",
                    "project_type": "SANDBOX"
                }
            ],
            projects.to_list(),
        )

    def test_get_projects_pagination(self):
        """
        Test get projects for the initialized user, where the user has to
        page through projects.

        """
        self.mock_client.execute = mock.Mock()
        self.mock_client.execute.side_effect = [
            {
                'org': {
                    'id': 'org-rune,org', 
                    'projectList': {
                        'projects': [
                            {
                                "id": "proj1-id",
                                "created_at": 1630515986.9949625,
                                "title": "Project 1",
                                "description": "Test description.",
                                "created_by": "user-id-1",
                                "started_at": 1630515986.9949625,
                                "status": "ACTIVE",
                                "project_type": "SANDBOX"
                            },
                            {
                                "id": "proj2-id",
                                "created_at": 1630517986.9949625,
                                "title": "Project 2",
                                "description": "Test description 2.",
                                "created_by": "user-id-2",
                                "started_at": 1630517986.9949625,
                                "status": "ACTIVE",
                                "project_type": "SANDBOX"

                            },
                        ],
                        "pageInfo": {
                            "endCursor": "test_check_next"
                        },
                    }
                }
            },
            {
                'org': {
                    'id': 'org-rune,org', 
                    'projectList': {
                        'projects': [
                            {
                                "id": "proj3-id",
                                "created_at": 1630519986.9949625,
                                "title": "Project 3",
                                "description": "Test description 3.",
                                "created_by": "user-id-3",
                                "started_at": 1630519986.9949625,
                                "status": "ACTIVE",
                                "project_type": "SANDBOX"
                            },
                        ],
                        "pageInfo": {
                            "endCursor": None
                        },
                    }
                }
            },
        ]

        projects = get_projects(client=self.mock_client)

        self.assertEqual(
            [
                {
                    "id": "proj1-id",
                    "created_at": 1630515986.9949625,
                    "title": "Project 1",
                    "description": "Test description.",
                    "created_by": "user-id-1",
                    "started_at": 1630515986.9949625,
                    "status": "ACTIVE",
                    "project_type": "SANDBOX"
                },
                {
                    "id": "proj2-id",
                    "created_at": 1630517986.9949625,
                    "title": "Project 2",
                    "description": "Test description 2.",
                    "created_by": "user-id-2",
                    "started_at": 1630517986.9949625,
                    "status": "ACTIVE",
                    "project_type": "SANDBOX"
                },
                {
                    "id": "proj3-id",
                    "created_at": 1630519986.9949625,
                    "title": "Project 3",
                    "description": "Test description 3.",
                    "created_by": "user-id-3",
                    "started_at": 1630519986.9949625,
                    "status": "ACTIVE",
                    "project_type": "SANDBOX"
                }
            ],
            projects.to_list(),
        )

