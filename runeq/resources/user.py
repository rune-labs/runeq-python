"""
Fetch metadata about Rune platform users.

"""

from typing import Optional

from .client import GraphClient, global_graph_client
from .common import ItemBase


class User(ItemBase):
    """
    A user of the Rune platform.

    """

    def __init__(
        self,
        id: str,
        name: str,
        created_at: float,
        active_org_id: str,
        active_org_name: str,
        **attributes
    ):
        """
        Initialize with metadata.

        Args:
            id: User ID
            name: Human-readable display name for the user
            created_at: When the user was created (unix timestamp)
            active_org_id: ID of the user's currently active organization
            active_org_name: Display name of the user's currently
                active organization

        """
        norm_id = id
        self.name = name
        self.created_at = created_at
        self.active_org_id = active_org_id
        self.active_org_name = active_org_name

        super().__init__(
            id=norm_id,
            name=name,
            created_at=created_at,
            active_org_id=active_org_id,
            active_org_name=active_org_name,
            **attributes,
        )

    @staticmethod
    def normalize_id(user_id: str) -> str:
        """
        Strip resource prefix and suffix from the user ID (if they exist).

        Args:
            user_id: User ID

        """
        if user_id.startswith("user-"):
            user_id = user_id[5:]

        if user_id.endswith(",user"):
            user_id = user_id[:-5]

        return user_id


def get_current_user(client: Optional[GraphClient] = None) -> User:
    """
    Get information about the current user (based on the API credentials).

    Args:
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.
    """
    client = client or global_graph_client()
    query = """
        query getUser {
            user {
                id
                created_at: created
                name: displayName
                defaultMembership {
                    org {
                        id
                        name: displayName
                    }
                }
                email
            }
        }
    """

    result = client.execute(statement=query)

    user_attrs = result["user"]

    org = user_attrs.get("defaultMembership", {}).get("org")

    return User(
        id=user_attrs["id"],
        name=user_attrs.get("name"),
        created_at=user_attrs.get("created_at"),
        active_org_id=org.get("id"),
        active_org_name=org.get("name"),
        email=user_attrs.get("email"),
    )
