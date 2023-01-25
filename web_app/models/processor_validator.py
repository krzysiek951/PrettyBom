from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Callable

from ..functions import is_position_delimiter_unique, is_quantity_a_number, invalid_quantity_error_message, \
    invalid_position_error_message

if TYPE_CHECKING:
    from .bom_processor import AbstractBomProcessor
from .part import AbstractPart


class AbstractPartListValidator:
    def __init__(self, processor: AbstractBomProcessor):
        self.invalid_position_parts: list[AbstractPart] = []
        self.invalid_quantity_parts: list[AbstractPart] = []
        self.processor = processor
        self.validation_succeeded: bool = False
        self.error_messages: list[str] = []
        self.part_position_delimiter: str | None = None

    @abstractmethod
    def run(self):
        """Starts the Validator."""
        ...

    def validate_with(self, func: Callable, invalid_parts_list, error_message):
        """
        Validates the Part list with given function.
        Invalid parts exports to given lists.
        Error message will be printed to user.
        """
        invalid_parts = [part for part in self.processor.initial_part_list if not func(self, part)]
        setattr(self, invalid_parts_list, invalid_parts)
        if invalid_parts:
            self.error_messages.append(error_message)

    def finish_validation(self):
        """Sets True if every Part has passed the validation."""
        self.validation_succeeded = True if not self.invalid_position_parts and not self.invalid_quantity_parts else False


class PartListValidator(AbstractPartListValidator):
    def __init__(self, processor: AbstractBomProcessor):
        super().__init__(processor)

    def run(self) -> None:
        self.validate_with(is_quantity_a_number, 'invalid_quantity_parts', invalid_quantity_error_message(self))
        self.validate_with(is_position_delimiter_unique, 'invalid_position_parts', invalid_position_error_message(self))
        self.finish_validation()
