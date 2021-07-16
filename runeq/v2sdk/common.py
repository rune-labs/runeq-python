"""
Common utilities and base classes.

"""
from collections import OrderedDict
import re
from typing import Any, Dict, Iterable, Iterator, Optional

from .graph.model import GraphID


INDENTATION = "    "
"""
Indentation string used in formatting.

"""

_camel_to_snake = re.compile(r'(?<!^)(?=[A-Z])')
"""
Regular expression pattern for coercing CamelCase to snake_case.

"""


class SetMemberBase:
    """
    Base class for graph models representing a single member of a set.

    """

    _id: Optional[GraphID] = None
    """
    The Graph item ID.

    """

    _relations: Dict = {}
    """
    Mapping of fields to model classes.

    """


    def __eq__(self, right):
        """
        Compare two graph items for equality by ID.

        """
        if isinstance(right, SetMemberBase):
            return self._id == right._id
        else:
            return self._id == right


    def __getattr__(self, attr: str) -> Any:
        """
        Facilitate access to fields in both canonical snake case and their
        original GraphQL case (lowercase camel).

        """
        if '_' in attr:
            field_name = attr[0] + attr.title()[1:].replace('_', '')
        else:
            field_name = attr

        try:
            return self._res[field_name]
        except KeyError:
            raise AttributeError(field_name)


    def __getitem__(self, field_name: str) -> Any:
        """
        Access the raw representational state directly.

        """
        return self._res[field_name]


    def __init__(self, res: Dict[str, Any], session=None):
        """
        Initialize representational state.

        res
            The raw representational state dictionary, as returned by the
            Graph API. Note that this object takes ownership, and may modify
            it in-place. The caller should not continue to use the state.

        session
            Shared reference to the client session.

        """
        try:
            self._id = GraphID(res['id'], self.resource)
        except KeyError:
            pass
        else:
            res['id'] = self._id.unqualified

        for field_name, model in self._relations.items():
            try:
                field_res = res[field_name]
            except KeyError:
                continue

            if isinstance(field_res, list):
                res[field_name] = [model(state) for state in field_res]
            else:
                res[field_name] = model(field_res)

        self._res = res
        self._session = session


    def __iter__(self):
        """
        Iterator over the representational state dictionary.

        """
        return iter(self._res)


    def __len__(self):
        """
        Number of fields in state.

        """
        return len(self._res)


    def __repr__(self):
        """
        Format the diagnostic representaion.

        """
        return repr(self._res)


    def __str__(self):
        """
        Format the human-readable representation.

        """
        return self._format(0)


    def _format(self, indent: int) -> str:
        """
        Format human-readable string representation with indentation.

        """
        fmt = f"{self.resource} {{\n"

        for field, value in self._res.items():
            fmt += INDENTATION * (indent + 1)
            attr = _camel_to_snake.sub('_', field).lower()

            if isinstance(value, SetMemberBase):
                # Recursively format child
                fmt += f"{attr}: {value._format(indent + 1)}\n"

            elif (
                isinstance(value, list)
                and
                len(value)
                and isinstance(value[0], SetMemberBase)
            ):
                # Recursively format many children
                fmt += f"{attr}: [\n"

                for child in value:
                    fmt += INDENTATION * (indent + 2)
                    fmt += f"{child._format(indent + 2)}\n"

                fmt += INDENTATION * (indent + 1)
                fmt += "]\n"

            else:
                # Scalar
                fmt += f"{attr}: {value}\n"

        fmt += INDENTATION * indent
        fmt += '}'

        return fmt


    @property
    def resource(self) -> str:
        """
        The resource name.

        """
        return self.__class__.__name__.lower()


class SetBase:
    """
    Base class for collections of items.

    """

    _all: bool
    """
    Metadata about whether this contains all the available members of the
    set.

    """

    _member: SetMemberBase
    """
    The collection member class.

    """

    _members: OrderedDict
    """
    The members of this set.

    """


    def __getitem__(self, key: str):
        """
        Get a member by ID.

        """
        if isinstance(key, str):
            key = GraphID(key)

        return self._members[key.as_tuple()]


    def __init__(self, all_=False):
        """
        Initialize the base

        """
        self._all = all_
        self._members = OrderedDict()


    def __iter__(self) -> Iterator:
        """
        Iterate over the members of the set.

        """
        return iter(self._members.values())


    def __str__(self):
        """
        Format the list of members for human readability.

        """
        return "\n".join(str(member) for member in self._members.values())


    def add(self, member):
        """
        Add a member to this set.

        """
        self._members[member._id.as_tuple()] = member


    def created_before(self, t: float) -> Iterator:
        """
        Iterator for members created before a given time.

        """
        for member in self._members.values():
            t_created = member.created_at

            if t_created is not None and member.created_at >= t:
                continue

            yield member


    def filtered_by(self, **conditions) -> Iterator:
        """
        Filter members with specific attributes equal to a value.

        Return an iterator over only items that match ALL of the attribute
        constraints. This is identical to `find_all_by()` on a query, but for
        cached sets that are already loaded.

        ```
        # Get all apple watches from a cached device set
        for device in device_cache.filtered_by(device_type='apple watch'):
            do_something(device)
        ```

        This method is intended for internal SDK use only.

        """
        if not conditions:
            raise TypeError(
                "at least one attribute filter condition expected")

        for member in self._members.values():

            for attr, value in conditions.items():
                if getattr(member, attr) != value:
                    break
            else:
                yield member


    def ids(self) -> Iterator[str]:
        """
        Iterator over the member IDs.

        """
        return (member.id for member in self._members.values())


    def update(self, other: Iterable):
        """
        Add members to the set from an iterable

        """
        for member in other:
            self.add(member)


class QueryBase:
    """
    Base class for query classes.

    """

    _set: SetBase
    """
    The set class.

    """


    def __init__(self, session):
        """
        Initialize the base

        """
        self._session = session


    def __getitem__(self, member_id: str):
        """
        Retrieve a specific member of the collection by its ID.

        """
        raise NotImplementedError()


    def __iter__(self):
        """
        Execute a streaming query and return an iterator over the results.

        Uses the local cache when enabled.

        """
        raise NotImplementedError()


    def __str__(self):
        """
        Execute the query.

        This magic behavior is implemented to support, e.g.
        `print(rune.patients)`.

        """
        result = self._set(all_=True)

        for member in self:
            result.add(member)

        return str(result)


    def find_all_by(self, **conditions) -> Iterator:
        """
        Find subset with specific attributes.

        """
        if not conditions:
            raise TypeError(
                "at least one attribute filter condition expected")

        for member in self:

            for attr, value in conditions.items():
                if getattr(member, attr) != value:
                    break
            else:
                yield member


    def query(self):
        """
        Execute query and return results.

        This method always executes an API query. Use `iter(query)` for
        general use instead.

        """
        sess = self._session
        result = self._set(all_=True)

        for member_state in self.raw_query():
            result.add(self._set._member(member_state, session=sess))

        return result


    def raw_query(self) -> Iterable:
        """
        Execute a GraphQL query to the API and return the raw state result.

        """
        raise NotImplementedError()

