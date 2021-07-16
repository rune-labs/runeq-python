"""
Base for Graph API representational state models.

"""
from typing import Optional, Tuple


class GraphID:
    """
    A fully qualified Graph item key.

    """

    _key: Tuple[str]
    """
    The key components.

    """


    def __contains__(self, sub):
        """
        Proxy substring queries.

        """
        if sub == ',':
            return len(self._key) > 1
        elif sub == '-':
            return True
        elif isinstance(sub, str):
            return sub in self._key[0] or sub in self._key[-1]
        else:
            return TypeError(f"in operator not supported for {type(sub)}")


    def __eq__(self, right):
        """
        Compare two graph IDs for equality.

        """
        if isinstance(right, GraphID):
            return self._key == right._key
        elif isinstance(right, str):
            return ','.join(self._key) == right
        else:
            return False


    def __init__(self, key, resource: Optional[str] = None):
        """
        Initialize the graph ID.

        """
        if isinstance(key, self.__class__):
            # Copy graph ID
            self._key = key._key
            return

        if ',' in key:
            self._key = tuple(key.split(',', 1))

        elif resource:

            if '-' not in key:
                key = f"{resource}-{key}"

            self._key = (key, resource)

        else:
            raise ValueError(f"ambiguous graph key: {key!r}")


    def __str__(self):
        """
        Format back to string Graph identifier.

        """
        return ",".join(self._key)


    def as_tuple(self):
        """
        Return the single or double containing the Graph item primary key.

        """
        return self._key


    @property
    def principal(self):
        """
        Return the principal component of the key.

        """
        return self._key[0]


    @property
    def relative(self):
        """
        Return the relative component of the key.

        """
        if len(self._key) > 1:
            return self._key[1]


    @property
    def unqualified(self):
        """
        The relative, unqualified identifier.

        """
        if len(self._key) > 1 and '-' in self._key[1]:
            return self._key[1].split('-', 1)[-1]
        else:
            return self._key[0].split('-', 1)[-1]
