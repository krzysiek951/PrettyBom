from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import AbstractPartListValidator
    from ..models import AbstractPart


def is_position_delimiter_unique(validator: AbstractPartListValidator, part: AbstractPart) -> bool:
    """ Returns true if position column has at least one non-digit unique delimiter for all parts. """

    validation_succeeded = False
    validator.invalid_position_parts = []

    try:
        position_delimiter = get_position_delimiter(getattr(part, validator.processor.part_position_column))
        if not position_delimiter or position_delimiter is validator.part_position_delimiter:
            validation_succeeded = True
        elif position_delimiter and not validator.part_position_delimiter:
            validator.part_position_delimiter = position_delimiter
            validation_succeeded = True

    except ValueError:
        validation_succeeded = False

    return validation_succeeded


def is_quantity_a_number(validator: AbstractPartListValidator, part: AbstractPart) -> bool:
    """"Returns True if Part quantity is a digit."""
    part_quantity = str(getattr(part, validator.processor.part_quantity_column))
    is_part_quantity_a_number = part_quantity.isdigit()
    return is_part_quantity_a_number


def get_position_delimiter(string: str) -> Optional[str]:
    """" Returns unique non-digit delimiter between numbers. """

    delimiter_candidates = {char for char in string if not char.isdigit()}

    if len(delimiter_candidates) > 1:
        raise ValueError("Only one number delimiter is allowed.")
    if not delimiter_candidates:
        return None
    delimiter = ''.join(delimiter_candidates)

    return delimiter


def invalid_position_error_message(validator: AbstractPartListValidator):
    message = f"Part position must be of integer type and use unique delimiter. " \
              f"Found {len(validator.invalid_position_parts)} invalid parts."
    return message


def invalid_quantity_error_message(validator: AbstractPartListValidator):
    message = f"Part quantity must be of integer type. Found {len(validator.invalid_quantity_parts)} invalid parts."
    return message
