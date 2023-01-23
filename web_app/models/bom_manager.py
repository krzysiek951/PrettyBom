from __future__ import annotations

from abc import ABC, abstractmethod

from web_app.models.bom import AbstractBom, DefaultBom


class BaseBomManager(ABC):
    def __init__(self):
        self._bom_list: list = []

    @property
    def bom_list(self) -> list[AbstractBom]:
        return self._bom_list

    @bom_list.setter
    def bom_list(self, bom_list: list[AbstractBom]) -> None:
        self._bom_list = bom_list

    @abstractmethod
    def create_bom(self, **kwargs) -> AbstractBom:
        ...

    @abstractmethod
    def reset_bom(self, bom: AbstractBom) -> AbstractBom:
        ...

    def get_bom_count(self) -> int:
        bom_count = len(self.bom_list)
        return bom_count

    def delete_bom(self, bom: AbstractBom) -> None:
        if bom not in self.bom_list:
            raise ValueError(f'{bom} does not exist in a BOM list.')
        else:
            self.bom_list = [item for item in self.bom_list if item is not bom]

    def print_bom_list(self) -> None:
        print("==== BOM LIST ====")
        for index, bom in enumerate(self.bom_list):
            print(index, bom.__dict__)


class DefaultBomManager(BaseBomManager):
    def __init__(self):
        super().__init__()
        self.bom_manager_type = 'default'

    def create_bom(self, **kwargs) -> DefaultBom:
        bom = DefaultBom(**kwargs)
        self.bom_list.append(bom)
        return bom

    def reset_bom(self, bom: DefaultBom) -> DefaultBom:
        if bom not in self.bom_list:
            raise ValueError(f"{bom} does not exist in a BOM list.")
        else:
            clean_bom = DefaultBom()
            self.bom_list = [item if item is not bom else clean_bom for item in self.bom_list]
            return clean_bom
