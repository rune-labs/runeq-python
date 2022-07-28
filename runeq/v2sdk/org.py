from typing import Optional

from .common import MemberType, MemberBase, MemberSet


class Org(MemberBase):
    """
    Representational state for an Org.
    """

    member_type = MemberType.ORG


class OrgSet(MemberSet):
    """
    Representational state for a set of Orgs.
    """

    member_type = MemberType.ORG


def get_org(org_id: str) -> Org:
    """
    get_org returns the org with the specified org_id if the user has access to the org.
    """


def get_orgs() -> OrgSet:
    """
    get_orgs returns a list of orgs the user is a member of.
    """


def switch_org(org_id: Optional[str], org: Optional[Org]) -> Org:
    """
    switch_org changes the users membership to the specified org_id or org.
    """
