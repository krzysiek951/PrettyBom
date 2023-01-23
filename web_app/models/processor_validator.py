from __future__ import annotations

from web_app.functions import *
from web_app.models.part import AbstractPart


class BomProcessorValidator:
    def __init__(self):
        self.validation_succeded: bool = False
        self.error_messages: list[str] = []
        self.invalid_position_value_parts: list = []
        self.invalid_quantity_value_parts: list = []
        self.part_position_delimiter: str | None = None

    def run(
            self,
            part_list: list[AbstractPart],
            part_position_column: str,
            part_quantity_column: str,
    ) -> None:
        """  """
        print('Part list validation started...')
        validated_parts = []

        for part in part_list:
            part_validators = [
                self.is_position_delimiter_unique(part, part_position_column),
                self.is_quantity_a_number(part, part_quantity_column),
            ]
            is_part_valid = all(part_validators)
            validated_parts.append(is_part_valid)

            self.validation_succeded = all(validated_parts)

            if self.invalid_position_value_parts:
                self.error_messages.append(
                    f'Part position must be of integer type and use unique delimiter. Found '
                    f'{len(self.invalid_position_value_parts)} invalid parts.')
            if self.invalid_quantity_value_parts:
                self.error_messages.append(
                    f'Part quantity must be of integer type. Found '
                    f'{len(self.invalid_quantity_value_parts)} invalid parts.')
        print('Part list validation finished.')

    def is_position_delimiter_unique(self, part: AbstractPart, part_position_column: str) -> bool:
        """ Returns true if position column has at least one non-digit unique delimiter for all parts. """
        try:
            position_delimiter = get_position_delimiter(getattr(part, part_position_column))
            if not position_delimiter or position_delimiter is self.part_position_delimiter:
                return True
            elif position_delimiter and not self.part_position_delimiter:
                self.part_position_delimiter = position_delimiter
                return True
            else:
                self.invalid_position_value_parts.append(part)
                return False
        except ValueError:
            self.invalid_position_value_parts.append(part)
            return False

    def is_quantity_a_number(self, part: AbstractPart, column_name: str) -> bool:
        part_quantity = str(getattr(part, column_name))
        is_quantity_a_number = part_quantity.isdigit()
        if not is_quantity_a_number:
            self.invalid_quantity_value_parts.append(part)
            return is_quantity_a_number
        return is_quantity_a_number
