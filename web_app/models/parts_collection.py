from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING

from web_app.functions.functions import sort_by_type_and_number

if TYPE_CHECKING:
    from web_app.models import AbstractPart


class PartsCollection(Iterable):
    def __init__(self, part_list: list[AbstractPart] = None) -> None:
        self._collection = part_list

    def __iter__(self) -> DefaultOrderIterator:
        return DefaultOrderIterator(self._collection)

    def __len__(self):
        return len(self._collection)

    def add_part(self, part: AbstractPart):
        """Adds Part to the Parts collection."""
        if self._collection is None:
            self._collection = []
        self._collection.append(part)

    def get_tree_part_list(self):
        """Returns tree list iterator."""
        return TreeOrderIterator(self._collection)


class AbstractPartListIterator(ABC, Iterator):
    def __init__(self, part_list: list[AbstractPart]):
        self._collection = part_list
        self._position = 0

    def __next__(self):
        try:
            value = self._iteration_list[self._position]
            self._position += 1
        except IndexError:
            raise StopIteration()
        return value

    @property
    @abstractmethod
    def _iteration_list(self) -> list[AbstractPart]:
        """Returns a list of Parts to iterate."""
        ...

    @property
    def collection(self):
        collection = self._collection if self._collection else []
        return collection

    @collection.setter
    def collection(self, part_list):
        self._collection = part_list


class DefaultOrderIterator(AbstractPartListIterator):
    def __init__(self, part_list: list[AbstractPart]):
        super().__init__(part_list)

    @property
    def _iteration_list(self) -> list[AbstractPart]:
        """Returns a list of Parts sorted by 'Part number'."""
        return self.collection


class PartNumberOrderIterator(AbstractPartListIterator):
    def __init__(self, part_list: list[AbstractPart]):
        super().__init__(part_list)

    @property
    def _iteration_list(self) -> list[AbstractPart]:
        """Returns a list of Parts sorted by 'Part number'."""
        return sorted(self._collection, key=lambda part: part.number, reverse=False)


class TreeOrderIterator(AbstractPartListIterator):
    def __init__(self, part_list: list[AbstractPart]):
        super().__init__(part_list)

    @property
    def _iteration_list(self) -> list[AbstractPart]:
        """Returns a list of Parts sorted as tree by 'Part number' and 'Type'."""
        initial_bom_tree_list = [part for part in self.collection if not part.parent]
        bom_tree_list = sorted(initial_bom_tree_list, key=lambda part: part.number)
        last_generation = 20
        for generation in range(1, last_generation):
            for part in bom_tree_list:
                part_generation = len(part.position.split(part.get_pos_delimiter()))
                if part_generation == generation:
                    child_bom = sort_by_type_and_number(part.child)
                    for item in child_bom:
                        bom_tree_list.insert(bom_tree_list.index(part) + 1, item)
        return bom_tree_list
