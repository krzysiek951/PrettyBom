from __future__ import annotations

import copy
from typing import Union, Callable

from .bom import AbstractBom
from .part import AbstractPart
from .processor_validator import PartListValidator, AbstractPartListValidator
from ..typing import BomProcessorClassTypes


class AbstractBomProcessor:
    """Abstract class for a BOM Processor used to process data of a Parts."""

    def __init__(self, bom: AbstractBom):
        self.bom = bom
        self.initial_part_list: list[AbstractPart] = []
        self.processed_part_list: list[AbstractPart] = []
        self.processing_succeeded = False
        self.part_position_delimiter: str | None = None
        self.production_part_keywords: Union[list, str, None] = None
        self.junk_part_keywords: Union[list, str, None] = None
        self.junk_part_empty_fields: Union[list, str, None] = None
        self.set_junk_for_purchased_nests: bool | None = True
        self.reverse_bom_sorting: bool = False
        self.part_position_column: str | None = None
        self.part_quantity_column: str | None = None
        self.part_number_column: str | None = None
        self.part_name_column: str | None = None
        self.normalized_columns: list | None = None
        self.parts_sorting: bool | None = None
        self.processor_validator: AbstractPartListValidator | None = None

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

    def run_validation(self) -> None:
        """Runs part list data validation."""
        ...

    def update_parts_with(self, func: Callable):
        """Sets Parts attributes with a new values."""
        if not self.processor_validator.validation_succeeded:
            self._abort_processing('Part list validation not passed. Processing aborted.')
            return

        for part in self.processed_part_list:
            func(processor=self, part=part)
        self.processing_succeeded = True

    def _abort_processing(self, message):
        """Sets the Processor to its initial state."""
        self.processing_succeeded = False
        self.initial_part_list = []
        self.processed_part_list = []
        print(message)

    def run_initialization(self):
        """Sets processor data for processing."""
        self.initial_part_list = copy.deepcopy(self.bom.part_list)
        self.processed_part_list = copy.deepcopy(self.bom.part_list)
        self.run_validation()
        if self.processor_validator.validation_succeeded:
            self.set_detected_delimiter()

    def set_detected_delimiter(self):
        """Sets part_position_delimiter detected in Part 'position' column."""
        self.part_position_delimiter = self.processor_validator.part_position_delimiter

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


class DefaultBomProcessor(AbstractBomProcessor):
    """Class for Default type of the BOM Processor."""
    processor_type: BomProcessorClassTypes = 'default'

    def __init__(self, bom: AbstractBom):
        super().__init__(bom)

    def run_validation(self):
        """Runs part list data validation."""
        validator = self.processor_validator = PartListValidator(self)
        validator.run()
