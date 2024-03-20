"""
Tests for fetching org metadata.

"""
from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import GraphClient
from runeq.resources.org import Org, get_org, get_orgs, set_active_org


class TestOrg(TestCase):
    """
    Unit tests for the Org class.

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
        Test attributes for an initialized Org.

        """
        test_org = Org(
            id="org1-id",
            created_at=1629300943.9179766,
            name="org1",
            tags=("tag1", "tag2"),
        )

        self.assertEqual("org1-id", test_org.id)
        self.assertEqual(1629300943.9179766, test_org.created_at)
        self.assertEqual("org1", test_org.name)
        self.assertEqual(["tag1", "tag2"], test_org.tags)

    def test_repr(self):
        """
        Test __repr__

        """
        test_org = Org(
            id="org1-id",
            created_at=1629300943.9179766,
            name="Org 1",
        )
        self.assertEqual('Org(id="org1-id", name="Org 1")', repr(test_org))

    def test_normalize_id(self):
        """
        Test strip id of resource prefix and suffix if they exist.

        """
        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            Org.normalize_id("org-d4b1c627bd464fe0a5ed940cc8e8e485,org"),
        )

        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            Org.normalize_id("d4b1c627bd464fe0a5ed940cc8e8e485,org"),
        )

        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            Org.normalize_id("org-d4b1c627bd464fe0a5ed940cc8e8e485"),
        )

        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            Org.normalize_id("d4b1c627bd464fe0a5ed940cc8e8e485"),
        )

    def test_denormalize_id(self):
        """
        Test add id resource prefix and suffix if they don't exist.

        """
        self.assertEqual(
            "org-d4b1c627bd464fe0a5ed940cc8e8e485,org",
            Org.denormalize_id("org-d4b1c627bd464fe0a5ed940cc8e8e485,org"),
        )

        self.assertEqual(
            "org-d4b1c627bd464fe0a5ed940cc8e8e485,org",
            Org.denormalize_id("d4b1c627bd464fe0a5ed940cc8e8e485,org"),
        )

        self.assertEqual(
            "org-d4b1c627bd464fe0a5ed940cc8e8e485,org",
            Org.denormalize_id("org-d4b1c627bd464fe0a5ed940cc8e8e485"),
        )

        self.assertEqual(
            "org-d4b1c627bd464fe0a5ed940cc8e8e485,org",
            Org.denormalize_id("d4b1c627bd464fe0a5ed940cc8e8e485"),
        )

    def test_get_org(self):
        """
        Test get org for specified org_id.

        """
        self.mock_client.execute = mock.Mock(
            return_value={
                "user": {
                    "membershipList": {
                        "pageInfo": {"endCursor": None},
                        "memberships": [
                            {
                                "org": {
                                    "id": "org1-id",
                                    "created_at": 1571267538.391721,
                                    "name": "org1",
                                    "tags": [],
                                }
                            },
                            {
                                "org": {
                                    "id": "org2-id",
                                    "created_at": 1630515986.9949625,
                                    "name": "org2",
                                    "tags": ["tag1", "tag2"],
                                }
                            },
                        ],
                    }
                }
            }
        )

        org = get_org("org1-id", client=self.mock_client)
        self.assertEqual(
            {
                "id": "org1-id",
                "created_at": 1571267538.391721,
                "name": "org1",
                "tags": [],
            },
            org.to_dict(),
        )

        org = get_org("org2-id", client=self.mock_client)
        self.assertEqual(
            {
                "id": "org2-id",
                "created_at": 1630515986.9949625,
                "name": "org2",
                "tags": ["tag1", "tag2"],
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
                        "pageInfo": {"endCursor": None},
                        "memberships": [
                            {
                                "org": {
                                    "id": "org1-id",
                                    "created_at": 1571267538.391721,
                                    "name": "org1",
                                    "tags": ["tag1"],
                                }
                            },
                            {
                                "org": {
                                    "id": "org2-id",
                                    "created_at": 1630515986.9949625,
                                    "name": "org2",
                                    "tags": ["tag2"],
                                }
                            },
                            {
                                "org": {
                                    "id": "org3-id",
                                    "created_at": 1649888079.066764,
                                    "name": "org3",
                                    "tags": [],
                                }
                            },
                        ],
                    }
                }
            }
        ]

        orgs = get_orgs(client=self.mock_client)

        self.assertEqual(
            [
                {
                    "created_at": 1571267538.391721,
                    "name": "org1",
                    "id": "org1-id",
                    "tags": ["tag1"],
                },
                {
                    "created_at": 1630515986.9949625,
                    "name": "org2",
                    "id": "org2-id",
                    "tags": ["tag2"],
                },
                {
                    "created_at": 1649888079.066764,
                    "name": "org3",
                    "id": "org3-id",
                    "tags": [],
                },
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
                        "pageInfo": {"endCursor": "test_check_next"},
                        "memberships": [
                            {
                                "org": {
                                    "id": "org1-id",
                                    "created_at": 1571267538.391721,
                                    "name": "org1",
                                    "tags": [],
                                }
                            }
                        ],
                    }
                }
            },
            {
                "user": {
                    "membershipList": {
                        "pageInfo": {"endCursor": None},
                        "memberships": [
                            {
                                "org": {
                                    "id": "org2-id",
                                    "created_at": 1630515986.9949625,
                                    "name": "org2",
                                    "tags": [],
                                }
                            }
                        ],
                    }
                }
            },
        ]

        orgs = get_orgs(client=self.mock_client)

        self.assertEqual(
            [
                {
                    "created_at": 1571267538.391721,
                    "name": "org1",
                    "id": "org1-id",
                    "tags": [],
                },
                {
                    "created_at": 1630515986.9949625,
                    "name": "org2",
                    "id": "org2-id",
                    "tags": [],
                },
            ],
            orgs.to_list(),
        )

    def test_set_active_org(self):
        """
        Test setting the user's active organization

        """
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
                                "tags": ["tag1"],
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
                "created_at": 1571267538.391721,
                "name": "org1",
                "id": "org1-id",
                "tags": ["tag1"],
            },
        )
