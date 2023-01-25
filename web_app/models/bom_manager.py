from __future__ import annotations

from abc import ABC, abstractmethod

from web_app.models.bom import AbstractBom, DefaultBom
from web_app.typing import BomManagerClassTypes


class AbstractBomManager(ABC):
    """Abstract class for a Manager of the Bill of Materials."""

    def __init__(self):
        self.bom_list: list[AbstractBom] = []

    @abstractmethod
    def create_bom(self, **kwargs) -> AbstractBom:
        """Creates a new Bill of Materials within BOM Manager."""
        ...

    @abstractmethod
    def reset_bom(self, bom: AbstractBom) -> AbstractBom:
        """Completely cleans up the existing bill of materials."""
        ...

    def get_bom_count(self) -> int:
        """Returns the quantity of a Bill of Materials in the BOM Manager."""
        bom_count = len(self.bom_list)
        return bom_count

    def delete_bom(self, bom: AbstractBom) -> None:
        """Deletes an existing BOM from BOM Manager."""
        if bom not in self.bom_list:
            raise ValueError(f'{bom} does not exist in a BOM list.')
        else:
            self.bom_list = [item for item in self.bom_list if item is not bom]

    def print_bom_list(self) -> None:
        """Prints all existing BOMs in BOM Manager."""
        print("==== BOM LIST ====")
        for index, bom in enumerate(self.bom_list):
            print(index, bom.__dict__)


class DefaultBomManager(AbstractBomManager):
    """Class for default type of the BOM Manager."""
    manager_type: BomManagerClassTypes = 'default'

    def __init__(self):
        super().__init__()

    def create_bom(self, main_assembly_name: str = '', main_assembly_sets: int = 0) -> DefaultBom:
        bom = DefaultBom(main_assembly_name, main_assembly_sets)
        self.bom_list.append(bom)
        return bom

    def reset_bom(self, bom: DefaultBom) -> DefaultBom:
        if bom not in self.bom_list:
            raise ValueError(f"{bom} does not exist in a BOM list.")
        else:
            clean_bom = DefaultBom()
            self.bom_list = [item if item is not bom else clean_bom for item in self.bom_list]
            return clean_bom
