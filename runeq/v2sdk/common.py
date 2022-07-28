"""
Common utilities and base classes.

"""
from collections import OrderedDict
from enum import Enum
from typing import Any, Dict, Iterator


class MemberType(Enum):
    ORG = "ORG"
    USER = "USER"
    PATIENT = "PATIENT"
    DEVICE = "DEVICE"
    STREAM = "STREAM"
    STREAM_TYPE = "STREAM_TYPE"
    DIMENSION = "DIMENSION"


class MemberBase:
    """
    Base class for representing member metadata.

    """

    member_type: MemberType
    member_id: str
    attributes: dict

    def __init__(self, member_type: MemberType, attributes: Dict[str, Any]):
        """
        Initialize member's representational state.
        """

    def __eq__(self, right):
        """
        Compare two member items for equality by ID.

        """

    def __getattr__(self, attr: str):
        """
        Get the value of any attribute in self.attributes.
        """

    def __getitem__(self, attr: str):
        """
        Get the value of any attribute in self.attributes.
        """

    def __iter__(self):
        """
        Iterator over the attribute in self.attributes.
        """

    def __len__(self):
        """
        Number of attribute in self.attributes.
        """

    def __repr__(self):
        """
        Format the member representation.
        """

    def __str__(self):
        """
        String representation of the member's type and attributes.
        """

    def to_dict(self):
        """
        Dictionary representation of the member's attributes.
        """

    def to_dataframe(self):
        """
        pandas.DataFrame representation of the member's attributes.
        """


class MemberSet:
    """
    Base class for representing a set of members' metadata.

    """

    member_type: MemberType

    members: OrderedDict
    """
    The members of this set.

    """

    def __init__(self, member_type: MemberType, members: list[MemberBase]):
        """
        Initialize members set representational state.
        """

    def __iter__(self) -> Iterator:
        """
        Iterate over the members of the set.
        """

    def __getitem__(self, attr: str):
        """
        Get a member by member_id.
        """

    def add(self, member: MemberBase):
        """
        Add a member to this set.
        """

    def remove(self, member: MemberBase):
        """
        Remove a member from this set.
        """

    def filter(self, attributes: Dict[str, Any]):
        """
        Filter out members that don't match ALL the attributes.
        This operation is destructive and can remove members from the set.
        """

    def ids(self) -> Iterator[str]:
        """
        Iterator over the member IDs.
        """

    def __str__(self):
        """
        String representation of the set of members.
        """

    def to_dict(self):
        """
        Dictionary representation of the set of members.
        """

    def to_dataframe(self):
        """
        pandas.DataFrame representation of the set of members.
        """
