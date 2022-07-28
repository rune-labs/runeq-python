from .common import MemberType, MemberBase


class User(MemberBase):
    """
    Representational state for a User.
    """

    member_type = MemberType.USER
