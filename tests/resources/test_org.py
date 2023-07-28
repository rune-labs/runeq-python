"""
Tests for fetching org metadata.

"""
from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import GraphClient
from runeq.resources.org import (
    active_org,
    get_org,
    get_orgs,
    Org,
    set_active_org
)
from runeq.resources.user import User


class TestOrg(TestCase):
    """
    Unit tests for the Org class.

    """

    def setUp(self):
        """
        Set up mock graph client for testing.

        """
        self.mock_client = GraphClient(
            Config(
                client_key_id='test',
                client_access_key='config'
            )
        )

    def test_attributes(self):
        """
        Test attributes for an initialized Org.

        """
        test_org = Org(
            id="org1-id",
            created_at=1629300943.9179766,
            name="org1",
        )

        self.assertEqual("org1-id", test_org.id)
        self.assertEqual(1629300943.9179766, test_org.created_at)
        self.assertEqual("org1", test_org.name)

    def test_repr(self):
        """
        Test __repr__

        """
        test_org = Org(
            id="org1-id",
            created_at=1629300943.9179766,
            name="Org 1",
        )
        self.assertEqual(
            'Org(id="org1-id", name="Org 1")',
            repr(test_org)
        )

    def test_normalize_id(self):
        """
        Test strip id of resource prefix and suffix if they exist.

        """
        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            Org.normalize_id("org-d4b1c627bd464fe0a5ed940cc8e8e485,org")
        )

        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            Org.normalize_id("d4b1c627bd464fe0a5ed940cc8e8e485,org")
        )

        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            Org.normalize_id("org-d4b1c627bd464fe0a5ed940cc8e8e485")
        )

        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            Org.normalize_id("d4b1c627bd464fe0a5ed940cc8e8e485")
        )

    def test_denormalize_id(self):
        """
        Test add id resource prefix and suffix if they don't exist.

        """
        self.assertEqual(
            "org-d4b1c627bd464fe0a5ed940cc8e8e485,org",
            Org.denormalize_id("org-d4b1c627bd464fe0a5ed940cc8e8e485,org")
        )

        self.assertEqual(
            "org-d4b1c627bd464fe0a5ed940cc8e8e485,org",
            Org.denormalize_id("d4b1c627bd464fe0a5ed940cc8e8e485,org")
        )

        self.assertEqual(
            "org-d4b1c627bd464fe0a5ed940cc8e8e485,org",
            Org.denormalize_id("org-d4b1c627bd464fe0a5ed940cc8e8e485")
        )

        self.assertEqual(
            "org-d4b1c627bd464fe0a5ed940cc8e8e485,org",
            Org.denormalize_id("d4b1c627bd464fe0a5ed940cc8e8e485")
        )

    def test_get_org(self):
        """
        Test get org for specified org_id.

        """
        self.mock_client.execute = mock.Mock(return_value={
            "user": {
                "membershipList": {
                    "pageInfo": {
                        "endCursor": None
                    },
                    "memberships": [
                        {
                            "org": {
                                "id": "org1-id",
                                "created_at": 1571267538.391721,
                                "name": "org1"
                            }
                        },
                        {
                            "org": {
                                "id": "org2-id",
                                "created_at": 1630515986.9949625,
                                "name": "org2"
                            }
                        }
                    ]
                }
            }
        })

        org = get_org("org1-id", client=self.mock_client)
        self.assertEqual(
            {
                "id": "org1-id",
                "created_at": 1571267538.391721,
                "name": "org1"
            },
            org.to_dict(),
        )

        org = get_org("org2-id", client=self.mock_client)
        self.assertEqual(
            {
                "id": "org2-id",
                "created_at": 1630515986.9949625,
                "name": "org2"
            },
            org.to_dict(),
        )

    def test_get_orgs_basic(self):
        """
        Test get orgs for the initialized user.

        """
        self.mock_client.execute = mock.Mock()
        self.mock_client.execute.side_effect = [
            {
                "user": {
                    "membershipList": {
                        "pageInfo": {
                            "endCursor": None
                        },
                        "memberships": [
                            {
                                "org": {
                                    "id": "org1-id",
                                    "created_at": 1571267538.391721,
                                    "name": "org1"
                                }
                            },
                            {
                                "org": {
                                    "id": "org2-id",
                                    "created_at": 1630515986.9949625,
                                    "name": "org2"
                                }
                            },
                            {
                                "org": {
                                    "id": "org3-id",
                                    "created_at": 1649888079.066764,
                                    "name": "org3"
                                }
                            }
                        ]
                    }
                }
            }
        ]

        orgs = get_orgs(client=self.mock_client)

        self.assertEqual(
            [
                {
                    'created_at': 1571267538.391721,
                    'name': 'org1',
                    'id': 'org1-id'
                },
                {
                    'created_at': 1630515986.9949625,
                    'name': 'org2',
                    'id': 'org2-id'
                },
                {
                    'created_at': 1649888079.066764,
                    'name': 'org3',
                    'id': 'org3-id'
                }
            ],
            orgs.to_list(),
        )

    def test_get_orgs_pagination(self):
        """
        Test get orgs for the initialized user, where the user has to
        page through orgs.

        """
        self.mock_client.execute = mock.Mock()
        self.mock_client.execute.side_effect = [
            {
                "user": {
                    "membershipList": {
                        "pageInfo": {
                            "endCursor": "test_check_next"
                        },
                        "memberships": [
                            {
                                "org": {
                                    "id": "org1-id",
                                    "created_at": 1571267538.391721,
                                    "name": "org1"
                                }
                            }
                        ]
                    }
                }
            },
            {
                "user": {
                    "membershipList": {
                        "pageInfo": {
                            "endCursor": None
                        },
                        "memberships": [
                            {
                                "org": {
                                    "id": "org2-id",
                                    "created_at": 1630515986.9949625,
                                    "name": "org2"
                                }
                            }
                        ]
                    }
                }
            }
        ]

        orgs = get_orgs(client=self.mock_client)

        self.assertEqual(
            [
                {
                    'created_at': 1571267538.391721,
                    'name': 'org1',
                    'id': 'org1-id'
                },
                {
                    'created_at': 1630515986.9949625,
                    'name': 'org2',
                    'id': 'org2-id'
                }
            ],
            orgs.to_list(),
        )

    def test_set_active_org(self):

        org_id = "org1-id"
        self.mock_client.execute = mock.Mock()
        self.mock_client.execute.side_effect = [
            {
                "updateDefaultMembership": {
                    "user": {
                        "defaultMembership": {
                            "org": {
                                "id": org_id,
                                "name": "org1",
                                "created_at": 1571267538.391721,
                            }
                        }
                    }
                }
            }
        ]

        new_org = set_active_org(org_id, self.mock_client)
        self.mock_client.execute.assert_called_once()
        self.assertEqual(
            new_org.to_dict(),
            {
                'created_at': 1571267538.391721,
                'name': 'org1',
                'id': 'org1-id'
            }
        )

    @mock.patch('runeq.resources.org.get_current_user')
    @mock.patch('runeq.resources.org.set_active_org')
    def test_with_active_org(self, mock_set_active_org, mock_get_current_user):
        """
        Test active org context manager.

        """
        org1_id = "org1-id"
        org2_id = "org2-id"

        mock_get_current_user.return_value = User(
            id="user1-id",
            created_at=1629300943.9179766,
            name="User 1",
            active_org_id=org1_id,
            active_org_name="Org 1",
        )
        mock_set_active_org.return_value = Org(
            id=org2_id,
            created_at=1629300943.9179766,
            name="org2",
        )

        # Test that active org is switched when the context manager
        # is active, and then restored on exit
        with active_org(org2_id, self.mock_client) as new_org:
            mock_set_active_org.assert_called_once_with(org2_id, self.mock_client)
            self.assertEqual(new_org.id, org2_id)

            mock_set_active_org.reset_mock()

        mock_set_active_org.assert_called_with(org1_id, self.mock_client)

        mock_set_active_org.reset_mock()

        # Active org is restored even if an exception is raised
        with self.assertRaises(ValueError):
            with active_org(org2_id, self.mock_client):
                mock_set_active_org.assert_called_once_with(org2_id, self.mock_client)
                raise ValueError()

        mock_set_active_org.assert_called_with(org1_id, self.mock_client)
