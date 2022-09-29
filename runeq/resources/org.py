"""
Fetch metadata about organizations. A research lab or clinical site is
typically represented as an organization.

"""

from typing import Iterable, Optional, Type

from .client import GraphClient, global_graph_client
from .common import ItemBase, ItemSet


class Org(ItemBase):
    """
    Metadata for an organization.

    """

    def __init__(
        self,
        id: str,
        name: str,
        created_at: float,
        **attributes
    ):
        """
        Initialize with metadata.

        Args:
            id: ID of the organization
            name: Human-readable name
            created_at: When the organization was created (unix timestamp)
            **attributes: Other attributes associated with the organization

        """
        norm_id = Org.normalize_id(id)
        self.name = name
        self.created_at = created_at

        super().__init__(
            id=norm_id,
            name=name,
            created_at=created_at,
            **attributes,
        )

    @staticmethod
    def normalize_id(org_id: str) -> str:
        """
        Strip resource prefix and suffix from an org ID (if they exist).

        Args:
            org_id: Organization ID

        """
        if org_id.startswith("org-"):
            org_id = org_id[4:]

        if org_id.endswith(",org"):
            org_id = org_id[:-4]

        return org_id

    @staticmethod
    def denormalize_id(org_id: str) -> str:
        """
        Add resource prefix and suffix to an org ID (if they don't exist).

        This constructs the form of the ID that is used for requests to the
        GraphQL API.

        Args:
            org_id: Organization ID

        """
        if not org_id.startswith("org-"):
            org_id = f'org-{org_id}'

        if not org_id.endswith(",org"):
            org_id = f'{org_id},org'

        return org_id


class OrgSet(ItemSet):
    """
    A collection of Organizations.

    """

    def __init__(self, items: Iterable[Org] = ()):
        """
        Initialize with Orgs.

        """
        super().__init__(items=items)

    @property
    def _item_class(self) -> Type[ItemBase]:
        """
        Instance type of items in this set.

        """
        return Org


def get_org(org_id: str, client: Optional[GraphClient] = None) -> Org:
    """
    Get the org with the specified ID.

    Args:
        org_id: Organization ID
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    """
    client = client or global_graph_client()
    query = '''
        query getOrg($org_id: ID) {
            org (orgId: $org_id) {
                id
                created_at: created
                name: displayName
            }
        }
    '''

    full_org_id = Org.denormalize_id(org_id)

    result = client.execute(
        statement=query,
        org_id=full_org_id
    )

    org_attrs = result["org"]
    return Org(
        id=org_attrs["id"],
        created_at=org_attrs.get("created_at"),
        name=org_attrs.get("name"),
    )


def get_orgs(client: Optional[GraphClient] = None) -> OrgSet:
    """
    Get all the organizations that the current user is a member of.

    Args:
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    """
    client = client or global_graph_client()
    query = '''
        query getOrgMemberships($cursor: Cursor) {
            user {
                membershipList(cursor: $cursor) {
                    pageInfo {
                        endCursor
                    }
                    memberships {
                        org {
                            id
                            created_at: created
                            name: displayName
                        }
                    }
                }
            }
        }
    '''

    next_cursor = None
    org_set = OrgSet()

    # Use cursor to page through all org memberships
    while True:
        result = client.execute(
            statement=query,
            cursor=next_cursor
        )

        membership_list = result.get("user", {}).get("membershipList", {})

        for membership in membership_list.get("memberships", []):
            org_attrs = membership["org"]
            org = Org(
                id=org_attrs["id"],
                created_at=org_attrs.get("created_at"),
                name=org_attrs.get("name"),
            )
            org_set.add(org)

        # endCursor is None when there are no more pages of data
        next_cursor = membership_list.get("pageInfo", {}).get("endCursor")
        if not next_cursor:
            break

    return org_set
