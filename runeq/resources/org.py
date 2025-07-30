"""
Fetch metadata about organizations. A research lab or clinical site is
typically represented as an organization.

"""
from typing import Iterable, Optional, Type, Union

from .client import GraphClient, global_graph_client
from .common import ItemBase, ItemSet


class Org(ItemBase):
    """
    Metadata for an organization.

    """

    def __init__(
        self, id: str, name: str, created_at: float, tags: Iterable = (), **attributes
    ):
        """
        Initialize with metadata.

        Args:
            id: ID of the organization
            name: Human-readable name
            created_at: When the organization was created (unix timestamp)
            tags: Organization tags
            **attributes: Other attributes associated with the organization

        """
        norm_id = Org.normalize_id(id)
        self.name = name
        self.created_at = created_at
        self.tags = list(tags)

        super().__init__(
            id=norm_id,
            name=name,
            created_at=created_at,
            tags=self.tags,
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
            org_id = f"org-{org_id}"

        if not org_id.endswith(",org"):
            org_id = f"{org_id},org"

        return org_id


class OrgSet(ItemSet[Org]):
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


def _iter_all_orgs(client: Optional[GraphClient] = None):
    """
    Fetch all orgs that the current user is a member of, and yield each
    one (while paging through the response)

    """
    client = client or global_graph_client()
    query = """
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
                            tags: orgTags
                        }
                    }
                }
            }
        }
    """

    next_cursor = None

    # Use cursor to page through all orgs that the user is a member of. Yield
    # each one as an Org
    while True:
        result = client.execute(statement=query, cursor=next_cursor)

        membership_list = result.get("user", {}).get("membershipList", {})

        for membership in membership_list.get("memberships", []):
            org_attrs = membership["org"]
            yield Org(**org_attrs)

        # endCursor is None when there are no more pages of data
        next_cursor = membership_list.get("pageInfo", {}).get("endCursor")
        if not next_cursor:
            break


def get_org(org_id: str, client: Optional[GraphClient] = None) -> Org:
    """
    Get the org with the specified ID.

    Args:
        org_id: Organization ID
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    """
    org_id = Org.normalize_id(org_id)
    # The getOrg query only works for the user's currently active organization.
    # To make this work for any org that the user is a member of, use
    # getOrgMemberships and try to find a matching org ID. It's slow, but it
    # works for now.
    for org in _iter_all_orgs(client):
        if org_id == org.id:
            return org

    raise ValueError(f"Org not found with id: {org_id}")


def get_orgs(client: Optional[GraphClient] = None) -> OrgSet:
    """
    Get all the organizations that the current user is a member of.

    Args:
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    """

    org_set = OrgSet()
    for org in _iter_all_orgs(client):
        org_set.add(org)

    return org_set


def set_active_org(org: Union[str, Org], client: Optional[GraphClient] = None) -> Org:
    """
    Set the active organization for the current user.

    Args:
        org: an org ID or Org
        client: If specified, this client is used to fetch metadata from the
            API. Otherwise, the global GraphClient is used.

    Returns:
        The active organization

    """
    client = client or global_graph_client()
    org_id = org.id if isinstance(org, Org) else org

    statement = """
    mutation updateDefaultMembership($input: UpdateDefaultMembershipInput!) {
        updateDefaultMembership(input: $input) {
            user {
                defaultMembership {
                    org {
                        id
                        created_at: created
                        name: displayName
                        tags: orgTags
                    }
                }
            }
        }
    }
    """

    result = client.execute(statement=statement, input={"orgId": org_id})

    user_attrs = result.get("updateDefaultMembership", {}).get("user", {})
    org_attrs = user_attrs.get("defaultMembership", {}).get("org")
    return Org(**org_attrs)
