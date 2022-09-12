"""
Common utilities and base classes.

"""
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Dict, Iterator, List, Type, Union


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
        Compare two items for equality by ID.

        """
        return type(self) == type(right) and self._id == right.id

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
        return (
            f'{self.__class__.__name__}(\n\tid={self._id},\n\t'
            f'attributes={self._attributes}\n)'
        )

    def to_dict(self) -> dict:
        """
        Dictionary representation of the item's attributes.

        """
        return self._attributes


class ItemSet(ABC):
    """
    Base class for representing a set of items.

    """

    # The Items in this set. Maps id to item.
    _items: Dict[str, ItemBase]

    def __init__(self, items: List[ItemBase] = []):
        """
        Initialize items set representational state.

        """
        self._items = OrderedDict()
        for item in items:
            self.add(item)

    def __iter__(self) -> Iterator[ItemBase]:
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

    def get(self, id: str) -> ItemBase:
        """
        Get an item by id.

        """
        return self._items.get(id)

    def add(self, *items: ItemBase):
        """
        Add item(s) to this set.

        """
        for item in items:
            if type(item) is not self._item_class:
                raise TypeError(
                    f'cannot add {str(item)}; must be type {self._item_class}'
                )

            self._items[item.id] = item

    def remove(self, *items: Union[str, ItemBase]):
        """
        Remove item(s) from this set.

        """
        for item in items:
            if type(item) is str:
                # item is an id
                self._items.pop(item, None)
            else:
                # item is an instance of ItemBase
                self._items.pop(item.id, None)

    def ids(self) -> Iterator[str]:
        """
        Iterator over the item IDs.

        """
        return iter(self._items.keys())

    def __str__(self):
        """
        String representation of the set of items. Returns information on
        the number of items in the set, the type of the set, and up to 3
        item ids.

        """
        items_ids = self._items.keys()
        items_str = ''.join([f'\t{str(id)}\n' for id in list(items_ids)[:3]])
        if len(items_ids) > 3:
            items_str += f'\t... (and {len(self._items.keys()) - 3} others)\n'

        return f'{type(self).__name__} {{\n{items_str}}}'

    def to_list(self) -> list:
        """
        List of all of the items in the set. Each item is formatted as a
        dictionary, using the item's `to_dict()` method.

        For example, the following item set:
        item_set = ItemSet(
            items=[
                ItemBase(
                    id="item_1",
                    attributes={id=1, "category": "neural"},
                ),
                ItemBase(
                    id="item_2",
                    attributes={id=2},
                ),
                ItemBase(
                    id="item_3",
                    attributes={
                        id=3,
                        "category": "symptom",
                        "stream_type": "current"
                    },
                ),
            ]
        )

        Would result in the following list:
        item_set.to_list() == [
            {"id": 1, "category": "neural", "stream_type": None}
            {"id": 2, "category": None, "stream_type": None}
            {"id": 3, "category": "symptom", "stream_type": "current"}
        ]
        """
        items_list = []
        for item in self._items.values():
            items_list.append(item.to_dict())

        return items_list
