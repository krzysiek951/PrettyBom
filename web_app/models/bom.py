from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from web_app.exceptions import InvalidPartSetsValue, ObjectNotFound, AttrNotSetException
from web_app.models.part import AbstractPart, DefaultPart
from web_app.models.parts_collection import PartsCollection
from web_app.typing import ImportedBomSource, BomClassTypes


class AbstractBom(ABC):
    """Abstract class for Bill of Materials (BOM)."""
    bom_type: BomClassTypes = None

    def __init__(self, main_assembly_name: str = '', main_assembly_sets: int = 0):
        self.part_list: PartsCollection = PartsCollection()
        self.imported_bom_sources: list[ImportedBomSource] = []
        self.imported_bom_columns: list[str] = []
        self._main_assembly_sets: int = main_assembly_sets
        self.main_assembly_name: str = main_assembly_name

    def __str__(self):
        return f'{self.bom_type} BOM:{self.__dict__}'

    def __repr__(self):
        return f'{self.__dict__}'

    def __len__(self):
        return len(self.part_list)

    @property
    def main_assembly_sets(self) -> int:
        """Getter for sets of the top-level assembly."""
        if not self._main_assembly_sets:
            raise AttrNotSetException('BOM must have "Assembly sets" set.')
        return self._main_assembly_sets

    @main_assembly_sets.setter
    def main_assembly_sets(self, main_assembly_sets: int) -> None:
        """Setter for sets of the top-level assembly."""
        try:
            main_assembly_sets = int(main_assembly_sets)
            self._main_assembly_sets = main_assembly_sets
        except ValueError as e:
            raise InvalidPartSetsValue(main_assembly_sets) from e

    @abstractmethod
    def create_part(self, **kwargs) -> AbstractPart:
        """Creates a new part within Bill of Materials."""
        ...

    def delete_part(self, part: AbstractPart) -> None:
        """Deletes an existing part from Bill of Materials."""
        if part not in self.part_list:
            raise ObjectNotFound(part, self)
        else:
            self.part_list = [item for item in self.part_list if item is not part]

    def delete_all_parts(self) -> None:
        """Deletes all existing parts from Bill of Materials."""
        self.part_list = PartsCollection()

    def get_part_count(self) -> int:
        """Returns the quantity of parts in Bill of Materials"""
        part_count = len(self.part_list)
        return part_count

    def print_part_list(self) -> None:
        """Prints a list of Parts in the Bill of Materials"""
        part_list = [part.__dict__ for part in self.part_list]
        df = pd.DataFrame(part_list)
        pd.set_option('display.max_rows', 100)
        pd.set_option('display.max_columns', 50)
        pd.set_option('display.width', 500)
        print(f"==== PART LIST ====\n"
              f"{df}")

    def print_tree_part_list(self) -> None:
        """Prints a tree list of Parts in the Bill of Materials."""
        part_list = [part.__dict__ for part in self.part_list.get_tree_part_list()]
        df = pd.DataFrame(part_list)
        pd.set_option('display.max_rows', 100)
        pd.set_option('display.max_columns', 50)
        pd.set_option('display.width', 500)
        print(f"==== PART LIST ====\n"
              f"{df}")


class DefaultBom(AbstractBom):
    """Class for default type of the Bill of Materials."""
    bom_type: BomClassTypes = 'default'

    def __init__(self, main_assembly_name: str = '', main_assembly_sets: int = 0):
        super().__init__(main_assembly_name, main_assembly_sets)

    def create_part(self, **kwargs) -> DefaultPart:
        """Creates a new Default Part within Bill of Materials."""
        part = DefaultPart(**kwargs)
        self.part_list.add_part(part)
        return part
