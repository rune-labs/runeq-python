"""
Tests for fetching user metadata.

"""
from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import GraphClient
from runeq.resources.user import User, get_current_user


class TestUser(TestCase):
    """
    Unit tests for the User class.

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
        Test attributes for an initialized User.

        """
        test_user = User(
            id="user1-id",
            created_at=1629300943.9179766,
            name="user1",
            active_org_id="org1-id",
            active_org_name="org1",
        )

        self.assertEqual("user1-id", test_user.id)
        self.assertEqual(1629300943.9179766, test_user.created_at)
        self.assertEqual("user1", test_user.name)
        self.assertEqual("org1-id", test_user.active_org_id)
        self.assertEqual("org1", test_user.active_org_name)

    def test_repr(self):
        """
        Test __repr__

        """
        test_user = User(
            id="user1-id",
            created_at=1629300943.9179766,
            name="User 1",
            active_org_id="org1-id",
            active_org_name="Org 1",
        )

        self.assertEqual('User(id="user1-id", name="User 1")', repr(test_user))

    def test_normalize_id(self):
        """
        Test strip id of resource prefix and suffix if they exist.

        """
        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            User.normalize_id("user-d4b1c627bd464fe0a5ed940cc8e8e485,user"),
        )

        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            User.normalize_id("d4b1c627bd464fe0a5ed940cc8e8e485,user"),
        )

        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            User.normalize_id("user-d4b1c627bd464fe0a5ed940cc8e8e485"),
        )

        self.assertEqual(
            "d4b1c627bd464fe0a5ed940cc8e8e485",
            User.normalize_id("d4b1c627bd464fe0a5ed940cc8e8e485"),
        )

    def test_get_user(self):
        """
        Test get org for specified org_id.

        """
        self.mock_client.execute = mock.Mock()
        self.mock_client.execute.side_effect = [
            {
                "user": {
                    "id": "user1-id",
                    "created_at": 1629300943.9179766,
                    "name": "user1",
                    "defaultMembership": {"org": {"id": "org1-id", "name": "org1"}},
                    "email": "user1@email.com",
                }
            }
        ]

        user = get_current_user(client=self.mock_client)

        self.assertEqual(
            {
                "id": "user1-id",
                "created_at": 1629300943.9179766,
                "name": "user1",
                "active_org_id": "org1-id",
                "active_org_name": "org1",
                "email": "user1@email.com",
            },
            user.to_dict(),
        )
