"""
Tests for fetching project data.

"""

from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import GraphClient
from runeq.resources.project import (
    Cohort,
    CohortSet,
    Project,
    ProjectPatientMetadata,
    get_cohort_patients,
    get_project,
    get_project_patients,
    get_projects,
)


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

    def test_project_attributes(self):
        """
        Test attributes for an initialized Project.

        """
        example_cohorts = CohortSet(
            [
                Cohort(
                    id="cohort-1",
                    title="title-1",
                    created_at=1630515986.9949625,
                    updated_at=1630515986.9949625,
                    created_by="user-1",
                    updated_by="user-1",
                ),
                Cohort(
                    id="cohort-2",
                    title="title-2",
                    created_at=1630515986.9949625,
                    updated_at=1630515986.9949625,
                    created_by="user-1",
                    updated_by="user-1",
                ),
            ]
        )

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
            cohorts=example_cohorts,
        )

        self.assertEqual("proj1-id", test_project.id)
        self.assertEqual(1630515986.9949625, test_project.created_at)
        self.assertEqual("Project 1", test_project.title)
        self.assertEqual(1630515986.9949625, test_project.updated_at)
        self.assertEqual("user-1", test_project.created_by)
        self.assertEqual("user-1", test_project.updated_by)
        self.assertEqual("ACTIVE", test_project.status)
        self.assertEqual("SANDBOX", test_project.type)
        self.assertEqual(example_cohorts, test_project.cohorts)

    def test_get_project(self):
        """
        Test get project for specified project_id.

        """
        example_cohorts = [
            {
                "id": "test-id-1",
                "title": "test-1",
                "description": "Some cohort 1",
                "created_at": 1667225389.222881,
                "updated_at": 1667225389.084547,
                "created_by": "Computer wizard",
                "updated_by": "Computer wizard",
            }
        ]
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
            "cohortList": {"cohorts": example_cohorts},
        }

        expected_project = {
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
            "cohorts": example_cohorts,
        }

        self.mock_client.execute.side_effect = [{"project": example_project}]

        project = get_project("proj1-id", client=self.mock_client)

        self.assertEqual(
            expected_project,
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
                "cohorts": [],
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
                "cohorts": [],
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
                "cohorts": [],
            },
        ]
        self.mock_client.execute.return_value = {
            "org": {
                "id": "org-rune,org",
                "projectList": {
                    "projects": [
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
                            "cohortList": {"cohorts": []},
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
                            "cohortList": {"cohorts": []},
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
                            "cohortList": {"cohorts": []},
                        },
                    ],
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
            "cohorts": [],
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
            "cohorts": [],
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
            "cohorts": [],
        }

        self.mock_client.execute = mock.Mock()
        self.mock_client.execute.side_effect = [
            {
                "org": {
                    "id": "org-rune,org",
                    "projectList": {
                        "projects": [
                            {
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
                                "cohortList": {"cohorts": []},
                            },
                            {
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
                                "cohortList": {"cohorts": []},
                            },
                        ],
                        "pageInfo": {"endCursor": "test_check_next"},
                    },
                }
            },
            {
                "org": {
                    "id": "org-rune,org",
                    "projectList": {
                        "projects": [
                            {
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
                                "cohortList": {"cohorts": []},
                            }
                        ],
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

    def test_project_patient_attributes(self):
        """
        Test attributes for an initialized Project Patient.

        """
        test_project = ProjectPatientMetadata(
            id="proj-patient-id",
            project_code_name="Code Name",
            start_time=1630515986.9949625,
            end_time=1630515986.9949625,
            created_at=1630515986.9949625,
            updated_at=1630515986.9949625,
            created_by="user-1",
            updated_by="user-1",
            started_at=1630515986.9949625,
        )

        self.assertEqual("proj-patient-id", test_project.id)
        self.assertEqual("Code Name", test_project.project_code_name)
        self.assertEqual(1630515986.9949625, test_project.start_time)
        self.assertEqual(1630515986.9949625, test_project.end_time)
        self.assertEqual(1630515986.9949625, test_project.created_at)
        self.assertEqual(1630515986.9949625, test_project.updated_at)
        self.assertEqual("user-1", test_project.created_by)
        self.assertEqual("user-1", test_project.updated_by)

    def test_cohort_attributes(self):
        """
        Test attributes for an initialized Cohort.

        """
        test_cohort = Cohort(
            id="cohort1-id",
            created_at=1630515986.9949625,
            updated_at=1630515986.9949625,
            title="Cohort 1",
            description="Test description.",
            created_by="user-1",
            updated_by="user-1",
        )

        self.assertEqual("cohort1-id", test_cohort.id)
        self.assertEqual(1630515986.9949625, test_cohort.created_at)
        self.assertEqual("Cohort 1", test_cohort.title)
        self.assertEqual(1630515986.9949625, test_cohort.updated_at)
        self.assertEqual("user-1", test_cohort.created_by)
        self.assertEqual("user-1", test_cohort.updated_by)

    def test_get_project_patients_basic(self):
        """
        Test get project patients for the initialized user.

        """
        self.mock_client.execute = mock.Mock()
        project_patients_expected = [
            {
                "id": "patient-1",
                "project_code_name": "code name 1",
                "start_time": 1673467625.063822,
                "end_time": 1673467625.063822,
                "created_at": 1673467625.063822,
                "updated_at": 1673467625.063822,
                "created_by": "user 1",
                "updated_by": "user 2",
            },
            {
                "id": "patient-2",
                "project_code_name": "code name 2",
                "start_time": 1673467625.063822,
                "end_time": 1673467625.063822,
                "created_at": 1673467625.063822,
                "updated_at": 1673467625.063822,
                "created_by": "user 2",
                "updated_by": "user 3",
            },
        ]

        self.mock_client.execute.return_value = {
            "project": {
                "organization_id": "org-rune",
                "projectPatientList": {
                    "projectPatients": [
                        {
                            "patient": {
                                "id": "patient-1",
                                "patientAccessList": {
                                    "patientAccess": [
                                        {
                                            "org": {
                                                "id": "org-rune,org",
                                            },
                                            "start_time": 1673467625.063822,
                                            "end_time": 1673467625.063822,
                                        },
                                    ]
                                },
                            },
                            "project_code_name": "code name 1",
                            "created_at": 1673467625.063822,
                            "updated_at": 1673467625.063822,
                            "created_by": "user 1",
                            "updated_by": "user 2",
                        },
                        {
                            "patient": {
                                "id": "patient-2",
                                "patientAccessList": {
                                    "patientAccess": [
                                        {
                                            "org": {
                                                "id": "org-rune,org",
                                            },
                                            "start_time": 1673467625.063822,
                                            "end_time": 1673467625.063822,
                                        },
                                    ]
                                },
                            },
                            "project_code_name": "code name 2",
                            "created_at": 1673467625.063822,
                            "updated_at": 1673467625.063822,
                            "created_by": "user 2",
                            "updated_by": "user 3",
                        },
                    ],
                    "pageInfo": {"codeNameEndCursor": None},
                },
            }
        }

        project_patients = get_project_patients(
            client=self.mock_client, project_id="test-project-1"
        )

        self.assertEqual(
            project_patients_expected,
            project_patients.to_list(),
        )

    def test_get_project_patients_patient_in_multiple_orgs(self):
        """
        Test get project patients for the initialized user. This tests to make sure
        that the correct start/end times are returned for a project patient that belongs
        to multiple organizations.

        """
        self.mock_client.execute = mock.Mock()
        project_patients_expected = [
            {
                "id": "patient-1",
                "project_code_name": "code name 1",
                "start_time": 1673467625.063822,
                "end_time": 1673467625.063822,
                "created_at": 1673467625.063822,
                "updated_at": 1673467625.063822,
                "created_by": "user 1",
                "updated_by": "user 2",
            },
            {
                "id": "patient-2",
                "project_code_name": "code name 2",
                "start_time": 1673467625.063822,
                "end_time": 1673467625.063822,
                "created_at": 1673467625.063822,
                "updated_at": 1673467625.063822,
                "created_by": "user 2",
                "updated_by": "user 3",
            },
        ]

        self.mock_client.execute.return_value = {
            "project": {
                "organization_id": "org-rune",
                "projectPatientList": {
                    "projectPatients": [
                        {
                            "patient": {
                                "id": "patient-1",
                                "patientAccessList": {
                                    "patientAccess": [
                                        {
                                            "org": {
                                                "id": "org-other,org",
                                            },
                                            "start_time": 1704838800.0,
                                            "end_time": None,
                                        },
                                        {
                                            "org": {
                                                "id": "org-rune,org",
                                            },
                                            "start_time": 1673467625.063822,
                                            "end_time": 1673467625.063822,
                                        },
                                    ]
                                },
                            },
                            "project_code_name": "code name 1",
                            "created_at": 1673467625.063822,
                            "updated_at": 1673467625.063822,
                            "created_by": "user 1",
                            "updated_by": "user 2",
                        },
                        {
                            "patient": {
                                "id": "patient-2",
                                "patientAccessList": {
                                    "patientAccess": [
                                        {
                                            "org": {
                                                "id": "org-rune,org",
                                            },
                                            "start_time": 1673467625.063822,
                                            "end_time": 1673467625.063822,
                                        },
                                    ]
                                },
                            },
                            "project_code_name": "code name 2",
                            "created_at": 1673467625.063822,
                            "updated_at": 1673467625.063822,
                            "created_by": "user 2",
                            "updated_by": "user 3",
                        },
                    ],
                    "pageInfo": {"codeNameEndCursor": None},
                },
            }
        }

        project_patients = get_project_patients(
            client=self.mock_client, project_id="test-project-1"
        )

        self.assertEqual(
            project_patients_expected,
            project_patients.to_list(),
        )

    def test_get_project_patients_pagination(self):
        """
        Test get project patients pagination for the initialized user.

        """
        self.mock_client.execute = mock.Mock()
        project_patients_expected = [
            {
                "id": "patient-1",
                "project_code_name": "code name 1",
                "start_time": 1673467625.063822,
                "end_time": 1673467625.063822,
                "created_at": 1673467625.063822,
                "updated_at": 1673467625.063822,
                "created_by": "user 1",
                "updated_by": "user 2",
            },
            {
                "id": "patient-2",
                "project_code_name": "code name 2",
                "start_time": 1673467625.063822,
                "end_time": 1673467625.063822,
                "created_at": 1673467625.063822,
                "updated_at": 1673467625.063822,
                "created_by": "user 2",
                "updated_by": "user 3",
            },
        ]

        self.mock_client.execute.side_effect = [
            {
                "project": {
                    "organization_id": "org-rune",
                    "projectPatientList": {
                        "projectPatients": [
                            {
                                "patient": {
                                    "id": "patient-1",
                                    "patientAccessList": {
                                        "patientAccess": [
                                            {
                                                "org": {
                                                    "id": "org-rune,org",
                                                },
                                                "start_time": 1673467625.063822,
                                                "end_time": 1673467625.063822,
                                            },
                                        ]
                                    },
                                },
                                "project_code_name": "code name 1",
                                "created_at": 1673467625.063822,
                                "updated_at": 1673467625.063822,
                                "created_by": "user 1",
                                "updated_by": "user 2",
                            },
                        ],
                        "pageInfo": {"codeNameEndCursor": "code name 1"},
                    },
                }
            },
            {
                "project": {
                    "organization_id": "org-rune",
                    "projectPatientList": {
                        "projectPatients": [
                            {
                                "patient": {
                                    "id": "patient-2",
                                    "patientAccessList": {
                                        "patientAccess": [
                                            {
                                                "org": {
                                                    "id": "org-rune,org",
                                                },
                                                "start_time": 1673467625.063822,
                                                "end_time": 1673467625.063822,
                                            },
                                        ]
                                    },
                                },
                                "project_code_name": "code name 2",
                                "created_at": 1673467625.063822,
                                "updated_at": 1673467625.063822,
                                "created_by": "user 2",
                                "updated_by": "user 3",
                            },
                        ],
                        "pageInfo": {"codeNameEndCursor": None},
                    },
                }
            },
        ]

        project_patients = get_project_patients(
            client=self.mock_client, project_id="test-project-1"
        )

        self.assertEqual(
            project_patients_expected,
            project_patients.to_list(),
        )

    def test_get_cohort_patients_basic(self):
        """
        Test get cohort patients for the initialized user.

        """
        self.mock_client.execute = mock.Mock()
        cohort_patients_expected = [
            {
                "id": "patient-1",
                "project_code_name": "code name 1",
                "start_time": 1673467625.063822,
                "end_time": 1673467625.063822,
                "created_at": 1673467625.063822,
                "updated_at": 1673467625.063822,
                "created_by": "user 1",
                "updated_by": "user 2",
            },
            {
                "id": "patient-2",
                "project_code_name": "code name 2",
                "start_time": 1673467625.063822,
                "end_time": 1673467625.063822,
                "created_at": 1673467625.063822,
                "updated_at": 1673467625.063822,
                "created_by": "user 2",
                "updated_by": "user 3",
            },
        ]

        self.mock_client.execute.return_value = {
            "cohort": {
                "organization_id": "org-rune",
                "cohortPatientList": {
                    "cohortPatients": [
                        {
                            "patient": {
                                "id": "patient-1",
                                "patientAccessList": {
                                    "patientAccess": [
                                        {
                                            "org": {
                                                "id": "org-rune,org",
                                            },
                                            "start_time": 1673467625.063822,
                                            "end_time": 1673467625.063822,
                                        },
                                    ]
                                },
                            },
                            "project_code_name": "code name 1",
                            "created_at": 1673467625.063822,
                            "updated_at": 1673467625.063822,
                            "created_by": "user 1",
                            "updated_by": "user 2",
                        },
                        {
                            "patient": {
                                "id": "patient-2",
                                "patientAccessList": {
                                    "patientAccess": [
                                        {
                                            "org": {
                                                "id": "org-rune,org",
                                            },
                                            "start_time": 1673467625.063822,
                                            "end_time": 1673467625.063822,
                                        },
                                    ]
                                },
                            },
                            "project_code_name": "code name 2",
                            "created_at": 1673467625.063822,
                            "updated_at": 1673467625.063822,
                            "created_by": "user 2",
                            "updated_by": "user 3",
                        },
                    ],
                    "pageInfo": {"codeNameEndCursor": None},
                },
            }
        }

        cohort_patients = get_cohort_patients(
            client=self.mock_client, cohort_id="test-cohort-1"
        )

        self.assertEqual(
            cohort_patients_expected,
            cohort_patients.to_list(),
        )

    def test_get_cohort_patients_pagination(self):
        """
        Test get cohort patients pagination for the initialized user.

        """
        self.mock_client.execute = mock.Mock()
        cohort_patients_expected = [
            {
                "id": "patient-1",
                "project_code_name": "code name 1",
                "start_time": 1673467625.063822,
                "end_time": 1673467625.063822,
                "created_at": 1673467625.063822,
                "updated_at": 1673467625.063822,
                "created_by": "user 1",
                "updated_by": "user 2",
            },
            {
                "id": "patient-2",
                "project_code_name": "code name 2",
                "start_time": 1673467625.063822,
                "end_time": 1673467625.063822,
                "created_at": 1673467625.063822,
                "updated_at": 1673467625.063822,
                "created_by": "user 2",
                "updated_by": "user 3",
            },
        ]

        self.mock_client.execute.side_effect = [
            {
                "cohort": {
                    "organization_id": "org-rune",
                    "cohortPatientList": {
                        "cohortPatients": [
                            {
                                "patient": {
                                    "id": "patient-1",
                                    "patientAccessList": {
                                        "patientAccess": [
                                            {
                                                "org": {
                                                    "id": "org-rune,org",
                                                },
                                                "start_time": 1673467625.063822,
                                                "end_time": 1673467625.063822,
                                            },
                                        ]
                                    },
                                },
                                "project_code_name": "code name 1",
                                "created_at": 1673467625.063822,
                                "updated_at": 1673467625.063822,
                                "created_by": "user 1",
                                "updated_by": "user 2",
                            },
                        ],
                        "pageInfo": {"codeNameEndCursor": "code name 1"},
                    },
                }
            },
            {
                "cohort": {
                    "organization_id": "org-rune",
                    "cohortPatientList": {
                        "cohortPatients": [
                            {
                                "patient": {
                                    "id": "patient-2",
                                    "patientAccessList": {
                                        "patientAccess": [
                                            {
                                                "org": {
                                                    "id": "org-rune,org",
                                                },
                                                "start_time": 1673467625.063822,
                                                "end_time": 1673467625.063822,
                                            },
                                        ]
                                    },
                                },
                                "project_code_name": "code name 2",
                                "created_at": 1673467625.063822,
                                "updated_at": 1673467625.063822,
                                "created_by": "user 2",
                                "updated_by": "user 3",
                            },
                        ],
                        "pageInfo": {"codeNameEndCursor": None},
                    },
                }
            },
        ]

        cohort_patients = get_cohort_patients(
            client=self.mock_client, cohort_id="test-cohort-1"
        )

        self.assertEqual(
            cohort_patients_expected,
            cohort_patients.to_list(),
        )
