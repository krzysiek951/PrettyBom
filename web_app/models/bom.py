from __future__ import annotations

from abc import ABC, abstractmethod

from web_app.models.bom_processor import DefaultBomProcessor
from web_app.models.part import AbstractPart, DefaultPart


class AbstractBom(ABC):
    def __init__(self, **kwargs):
        self.part_list: list[AbstractPart] = []
        self.imported_bom_sources: list[dict] = []
        self.imported_bom_columns: list[str] = []
        self.part_position_column: str = kwargs.get('part_position_column', '')
        self.part_quantity_column: str = kwargs.get('part_quantity_column', '')
        self.part_number_column: str = kwargs.get('part_number_column', '')
        self.part_name_column: str = kwargs.get('part_name_column', '')
        self._main_assembly_sets: int = kwargs.get('main_assembly_sets', 0)
        self.main_assembly_name: str = kwargs.get('main_assembly_name', '')

    @abstractmethod
    def create_part(self, **kwargs) -> AbstractPart:
        ...

    @abstractmethod
    def process_part_list(self) -> None:
        ...

    def delete_part(self, part: AbstractPart) -> None:
        if part not in self.part_list:
            raise ValueError(f'{part} does not exist in a Bill of Materials.')
        else:
            self.part_list = [item for item in self.part_list if item is not part]

    def delete_all_parts(self) -> None:
        self.part_list.clear()

    def get_part_count(self) -> int:
        part_count = len(self.part_list)
        return part_count

    def print_part_list(self) -> None:
        print("==== PART LIST ====")
        for index, part in enumerate(self.part_list):
            print(index, part.__dict__)


class DefaultBom(AbstractBom):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bom_type = 'default'
        self.production_part_keywords: list = kwargs.get('production_part_keywords', [])
        self.junk_part_keywords: list = kwargs.get('junk_part_keywords', [])
        self.junk_part_empty_fields: list = kwargs.get('junk_part_empty_fields', [])
        self.normalized_columns: list = kwargs.get('normalized_columns', [])
        self.parts_sorting: bool = kwargs.get('parts_sorting', True)
        self.bom_processor: DefaultBomProcessor | None = None

    def create_part(self, **kwargs) -> DefaultPart:
        part = DefaultPart(**kwargs)
        self.part_list.append(part)
        return part

    def process_part_list(self):
        self.bom_processor = DefaultBomProcessor(
            production_part_keywords=self.production_part_keywords,
            junk_part_keywords=self.junk_part_keywords,
            junk_part_empty_fields=self.junk_part_empty_fields,
            part_position_column=self.part_position_column,
            part_quantity_column=self.part_quantity_column,
            part_number_column=self.part_number_column,
            part_name_column=self.part_name_column,
            main_assembly_name=self.main_assembly_name,
            main_assembly_sets=self.main_assembly_sets,
            normalized_columns=self.normalized_columns,
            parts_sorting=self.parts_sorting,
        )
        try:
            self.bom_processor.run_processing(self.part_list)
            self.part_list = self.bom_processor.processed_part_list
        except ValueError as error:
            return error

    def undo_processing(self) -> None:
        self.part_list = self.bom_processor.initial_part_list

    @property
    def main_assembly_sets(self) -> int:
        return self._main_assembly_sets

    @main_assembly_sets.setter
    def main_assembly_sets(self, main_assembly_sets: int) -> None:
        try:
            main_assembly_sets = int(main_assembly_sets)
            self._main_assembly_sets = main_assembly_sets
        except ValueError as e:
            raise ValueError('Main assembly sets must be of integer type.') from e
