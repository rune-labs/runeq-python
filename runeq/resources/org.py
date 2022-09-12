"""
V2 SDK functionality to support Org operations.

"""

from typing import List, Optional, Type

from .client import GraphClient, global_graph_client
from .common import ItemBase, ItemSet


class Org(ItemBase):
    """
    An organization.

    """

    def __init__(
        self,
        id: str,
        display_name: str,
        created_at: float,
        **attributes
    ):
        """
        Initializes an Org

        """
        norm_id = Org.normalize_id(id)
        self.display_name = display_name
        self.created_at = created_at

        super().__init__(
            id=norm_id,
            display_name=display_name,
            created_at=created_at,
            **attributes,
        )

    @staticmethod
    def normalize_id(id: str) -> str:
        """
        Strip resource prefix and suffix from Org ID if they exist.

        """
        if id.startswith("org-"):
            id = id[4:]

        if id.endswith(",org"):
            id = id[:-4]

        return id

    @staticmethod
    def denormalize_id(id: str) -> str:
        """
        Add resource prefix and suffix to Org ID if they don't exist.

        """
        if not id.startswith("org-"):
            id = f'org-{id}'

        if not id.endswith(",org"):
            id = f'{id},org'

        return id


class OrgSet(ItemSet):
    """
    A collection of organizations.

    """

    def __init__(self, items: List[Org] = []):
        """
        Initializes a set of Orgs

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
    Get the org with the specified org_id if the user has access to it.

    """
    client = client or global_graph_client()
    query = '''
        query getOrg($org_id: ID) {
            org (orgId: $org_id) {
                id
                created_at: created
                display_name: displayName
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
        display_name=org_attrs.get("display_name"),
    )


def get_orgs(client: Optional[GraphClient] = None) -> OrgSet:
    """
    Get the organizations that the current user is a member of.

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
                            display_name: displayName
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
                display_name=org_attrs.get("display_name"),
            )
            org_set.add(org)

        # endCursor is None when there are no more pages of data
        next_cursor = membership_list.get("pageInfo", {}).get("endCursor")
        if not next_cursor:
            break

    return org_set
