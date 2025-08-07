"""
Common utilities and base classes.

"""

from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Dict, Generic, Iterable, Iterator, List, Type, TypeVar, Union

import pandas as pd


class ItemBase:
    """
    Base class for representing an item.

    """

    # ID of the Item
    _id: str

    # Dictionary of attributes associated with the Item
    _attributes: dict

    def __init__(self, id: str, **attributes):
        """
        Initialize item's representational state.

        """
        self._id = id

        attributes["id"] = id
        self._attributes = attributes

    @property
    def id(self) -> str:
        """
        ID of the item.

        """
        return self._id

    def __eq__(self, right):
        """
        Two items are equal if they are the same type and have the same ID

        """
        # intentionally comparing types instead of using isinstance(), because
        # we don't want to consider a subclass to be equal
        return type(self) == type(right) and self.id == right.id  # noqa: E721

    def __getitem__(self, attr: str):
        """
        Get the value of any attribute in self.attributes.

        """
        return self._attributes.get(attr)

    def get(self, attr: str, default: Any = None):
        """
        Get the value of any attribute in self.attributes.

        """
        return self._attributes.get(attr, default)

    def __repr__(self):
        """
        Format the item representation.

        """
        if hasattr(self, "name"):
            return f"{self.__class__.__name__}" f'(id="{self.id}", name="{self.name}")'
        else:
            return f'{self.__class__.__name__}(id="{self.id}")'

    def to_dict(self) -> dict:
        """
        Dictionary representation of the item's attributes.

        """
        return self._attributes


Item = TypeVar("Item", bound=ItemBase)


class ItemSet(ABC, Generic[Item]):
    """
    Base class for representing a set of items.

    """

    # The Items in this set. Maps id to item.
    _items: Dict[str, Item]

    def __init__(self, items: Iterable[Item] = ()):
        """
        Initialize items set representational state.

        """
        self._items = OrderedDict()
        for item in items:
            self.add(item)

    def __iter__(self) -> Iterator[Item]:
        """
        Iterate over the items of the set.

        """
        return iter(self._items.values())

    def __len__(self):
        """
        Number of items in the set.

        """
        return len(self._items)

    def __getitem__(self, id: str):
        """
        Get an item.

        """
        return self._items.get(id)

    @property
    @abstractmethod
    def _item_class(self) -> Type[ItemBase]:
        """
        Instance type of items in this set.

        """
        pass

    def get(self, id: str) -> Item:
        """
        Get an item by id.

        Raises:
            ValueError: if the set does not contain an item with the ID.

        """
        try:
            return self._items[id]
        except KeyError:
            pass

        raise ValueError(
            f"{self.__class__.__name__} does not contain "
            f"{self._item_class.__name__} with ID {id}"
        )

    def add(self, item: Item):
        """
        Add a single item to the set. Must be the same type as other members
        of the collection

        """
        if type(item) is not self._item_class:
            raise TypeError(
                f"cannot add {str(item)}; must be type " f"{self._item_class.__name__}"
            )

        self._items[item.id] = item

    def update(self, items: Iterable[Item]):
        """
        Add an iterable of item(s) to this set. All items must be the same
        class as members of this collection.

        """
        for item in items:
            if type(item) is not self._item_class:
                raise TypeError(
                    f"cannot update with {str(item)}; all items must be type "
                    f"{self._item_class.__name__}"
                )

            self._items[item.id] = item

    def remove(self, *items: Union[str, Item]):
        """
        Remove item(s) from this set.

        """
        for item in items:
            if type(item) is str:
                # item is an id
                self._items.pop(item, None)
            else:
                # item is an instance of Item
                self._items.pop(item.id, None)

    def ids(self) -> Iterator[str]:
        """
        Iterator over the IDs of the items in this set.

        """
        return iter(self._items.keys())

    def __repr__(self):
        """
        String representation of the set of items. Returns information on
        the number of items in the set, the type of the set, and up to 3
        items.

        """
        item_strs = []
        for i, item in enumerate(self):
            if i > 2:
                item_strs.append(f"\t... (and {len(self._items.keys()) - 3} others)\n")
                break

            item_strs.append(f"\t{str(item)}\n")

        items_str = "".join(item_strs)
        return f"{type(self).__name__} {{\n{items_str}}}"

    def to_list(self) -> List[dict]:
        """
        List of all the items in the set. Each item is formatted as a
        dictionary, using the item's `to_dict()` method.

        """
        items_list = []
        for item in self._items.values():
            items_list.append(item.to_dict())

        return items_list

    def to_dataframe(self) -> pd.DataFrame:
        """Convert items to a dataframe (wraps `to_list()`)"""
        return pd.DataFrame(self.to_list())
