from __future__ import annotations

import copy
from typing import Union

from .bom import AbstractBom, PartsCollection
from .bom_processor_methods import ProcessorMethods


class BomProcessor:
    """Class for a BOM Processor used to process data of a Parts."""

    def __init__(self, bom: AbstractBom):
        self.bom = bom
        self.initial_part_list: PartsCollection | None = None
        self.processed_part_list: PartsCollection | None = None
        self.processing_succeeded = False
        self.part_position_delimiter: str | None = None
        self.production_part_keywords: Union[list, str, None] = None
        self.junk_part_keywords: Union[list, str, None] = None
        self.junk_part_empty_fields: Union[list, str, None] = None
        self.set_junk_for_purchased_nests: bool | None = True
        self.reverse_bom_sorting: bool = False
        self.normalized_columns: list | None = None
        self.parts_sorting: bool | None = None
        self.bom_modifiers = ProcessorMethods(self)

    def __str__(self):
        return f'Processor: {self.__dict__}'

    def __repr__(self):
        return f'{self.__dict__}'

    def print_initial_part_list(self) -> None:
        """Prints a list of parts before processing."""
        print("====== INITIAL PART LIST ======")
        for index, part in enumerate(self.initial_part_list):
            print(index, part.__dict__)

    def print_processed_part_list(self) -> None:
        """Prints a list of parts after processing."""
        print("====== PROCESSED PART LIST ======")
        for index, part in enumerate(self.processed_part_list):
            print(index, part.__dict__)

    def run_initialization(self):
        """Sets processor data for processing."""
        self.initial_part_list = copy.deepcopy(self.bom.part_list)
        self.processed_part_list = copy.deepcopy(self.bom.part_list)

    def set_attributes_from_kwargs(self, **kwargs):
        """Sets Processor attributes from keyword arguments."""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def finish_processing(self):
        """Sets BOM part list as processed part list."""
        if self.processing_succeeded:
            self.bom.part_list = self.processed_part_list

    def undo_processing(self) -> None:
        """Sets BOM Part list as initial part list."""
        self.bom.part_list = self.initial_part_list
