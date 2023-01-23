from __future__ import annotations

from abc import ABC, abstractmethod

from web_app.models.part import AbstractPart, DefaultPart
from web_app.typing import ImportedBomSource


class AbstractBom(ABC):
    """Abstract class for Bill of Materials (BOM)."""

    def __init__(self, main_assembly_name: str = '', main_assembly_sets: int = 0):
        self.part_list: list[AbstractPart] = []
        self.imported_bom_sources: list[ImportedBomSource] = []
        self.imported_bom_columns: list[str] = []
        self._main_assembly_sets: int = main_assembly_sets
        self.main_assembly_name: str = main_assembly_name

    @property
    def main_assembly_sets(self) -> int:
        """Getter for sets of the top-level assembly."""
        return self._main_assembly_sets

    @main_assembly_sets.setter
    def main_assembly_sets(self, main_assembly_sets: int) -> None:
        """Setter for sets of the top-level assembly."""
        try:
            main_assembly_sets = int(main_assembly_sets)
            self._main_assembly_sets = main_assembly_sets
        except ValueError as e:
            raise ValueError('Main assembly sets must be of integer type.') from e

    @abstractmethod
    def create_part(self, **kwargs) -> AbstractPart:
        """Creates a new part within Bill of Materials."""
        ...

    def delete_part(self, part: AbstractPart) -> None:
        """Deletes an existing part from Bill of Materials."""
        if part not in self.part_list:
            raise ValueError(f'{part} does not exist in a Bill of Materials.')
        else:
            self.part_list = [item for item in self.part_list if item is not part]

    def delete_all_parts(self) -> None:
        """Deletes all existing parts from Bill of Materials."""
        self.part_list.clear()

    def get_part_count(self) -> int:
        """Returns the quantity of parts in Bill of Materials"""
        part_count = len(self.part_list)
        return part_count

    def print_part_list(self) -> None:
        print("==== PART LIST ====")
        for index, part in enumerate(self.part_list):
            print(index, part.__dict__)


class DefaultBom(AbstractBom):
    """Class for default type of the Bill of Materials (BOM)."""
    bom_type = 'default'

    def __init__(self, main_assembly_name: str = '', main_assembly_sets: int = 0):
        super().__init__(main_assembly_name, main_assembly_sets)

    def create_part(self, **kwargs) -> DefaultPart:
        part = DefaultPart(**kwargs)
        self.part_list.append(part)
        return part
