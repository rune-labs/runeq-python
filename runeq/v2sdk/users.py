"""
Models for querying Rune users.

"""
from .common import SetMemberBase



class Org(SetMemberBase):
    """
    Representational state for a Rune organization.

    """


class Membership(SetMemberBase):
    """
    Representational state for a user's membership to an organization.

    """

    _relations = {
        'org': Org
    }


class User(SetMemberBase):
    """
    Representational state for a Rune platform user.

    """

    _relations = {
        'defaultMembership': Membership
    }
